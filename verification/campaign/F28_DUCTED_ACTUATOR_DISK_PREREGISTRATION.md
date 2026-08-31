# F28 — DUCTED ACTUATOR DISK: THRUST vs AIRSPEED — PRE-REGISTRATION

> ## FROZEN. **Status at freeze: ARMED — never run.**
>
> **Frozen by the commit that carries this file**, 2026-08-31, by `cfd-supervisor`
> personally under `SUPERVISION_CHARTER.md` §3 check 4. **After first compute the
> gates, thresholds, cap and labels below are CLOSED**; changes land only as dated
> addenda that cannot alter a gate, a threshold, a cap or a label, and originals are
> struck, never rewritten (`CLAUDE.md` rule 2).
>
> **THE FOUR THINGS THE SUPERVISOR VERIFIED PERSONALLY BEFORE STAMPING THIS, each
> re-derived on disk rather than taken from the drafting lane's report:**
>
> 1. **NO COMPUTE HAS OCCURRED.** `verification/runs/*F28*` does not exist,
>    `cases/*F28*` does not exist, and no `F28` entry exists anywhere under
>    `verification/queue/`. The gates below are therefore still open in the only sense
>    rule 2 cares about: **they could not have been chosen to fit an answer, because
>    there is no answer.** This is the freeze's entire evidentiary content.
> 2. **THE COST ARITHMETIC CLOSES, and it is the defect that sank the previous
>    draft.** §10's stages sum 4 + 30 + 70 + 40 + 240 = **384 core-min against the
>    registered cap of 400** — re-added by the supervisor, not read off the table's own
>    "Running" column. §2.8's original 320 would not have held it (the earlier draft's
>    144 + 240 = 384 > 320 is exactly the arithmetic that failed), which is why the cap
>    is an **upward, disclosed** departure and why it goes to Sanaa's desk as one.
> 3. **THE THEORY CONSTANT IS VERIFIED, NOT REMEMBERED — three independent ways**, per
>    the directive's own instruction that *"the constants written here are to be
>    checked, not trusted"*: this lane's SymPy derivation (§3.1), **Chew, Gan & Hesse
>    (2021) printed p.5 eq (7)** (§3.2), and **Geldenhuys (2015) printed p.7** (§3.3),
>    whose *"26% more"* is `(2 x 1)^(1/3)` in words. `2^(1/3) = 1.2599210498948732`,
>    re-evaluated by the supervisor. Both PDFs carry **title-page verification per
>    standing rule 15 / L-144**, and §3.2 discloses that its source is the Glasgow
>    Enlighten accepted version, not the AIAA version of record.
> 4. **THE RULE-11 ID IS A MAXIMUM, NOT A COUNT.** `git ls-tree -r HEAD` returns
>    exactly **one** path containing `F28` — this document itself — so the maximum
>    existing `F` number excluding this file is **27** and `F28` is correct. The id is
>    hereby **CONFIRMED, no longer PROVISIONAL.**
>
> **What the supervisor did NOT verify, stated so the stamp is not read wider than it
> is:** the mesh script, the comparator and the launcher **do not yet exist**. Their
> shas are registered at §5, §11.6 and §12 as artifacts to be recorded when written,
> and **each is subject to check 1 — the supervisor reads the measurement code as a
> diff before any number from it is believed.** This freeze fixes the *gates*; it does
> not certify an *instrument* that has not been built.
>
> **REVISION 2, 2026-08-30, retained as the record of how the document reached
> freezable state.** The three questions this lane raised in §14 and declined to
> decide — the ill-posed forward-flight balance, the under-specified open-disk
> reference, and the cost arithmetic that does not close — were all **ruled by
> `cfd-supervisor`** and are registered in §9.6/§9.6a, §7.1 and §2.7/§10. **§14 records
> each ruling with its author.** No question in this document was open at freeze, none
> was decided by the lane that raised it, and **none was decided after seeing a result,
> because no compute had been run.**

- **Team:** cfd
- **Rung id:** `F28` — **PROVISIONAL.** Derived from the tail per rule 11 (maximum
  existing `F` number in `git ls-tree -r HEAD` is 27, so 28 is next; this is a
  maximum, not a count). Assigning a family id is a supervisor call; rename freely
  before freeze.
- **Drafted:** 2026-08-30, by a `lab-lane` for `cfd-supervisor`.
- **Governing directive:** `etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md`,
  CASE 2, §2.1–§2.8. Sanaa's text governs; every departure from it is named in §2 below.
- **Standing rules:** `CLAUDE.md` rules 1–16 bind this document whether or not it
  repeats them.

---

## 1. What is being measured, and what would count as being wrong

A fan inside a duct, modelled as an actuator disk — **a thin cellZone carrying a
uniform axial momentum source equivalent to a pressure jump `delta_p`. No blades,
no swirl, no rotation. "Actuator-disk representation; no rotor" is DISCLOSED on
every surface this case produces**, per §2.1 of the directive.

The product is the map of total thrust (disk + duct) against airspeed at fixed disk
loading, plus one theory gate against ducted-actuator-disk momentum theory at static
conditions and one internal momentum-balance gate in forward flight.

This registration can produce `GATE FAIL` and is expected to be able to. The theory
gate's band has a **hard upper edge at the ideal value**: a simulated augmentation
*above* the ideal is not a good result, it is evidence the force integration or the
source calibration is wrong, and it fails the gate in that direction. That
asymmetry is deliberate and is registered here before any solve.

---

## 2. DEPARTURES FROM THE DIRECTIVE — declared before anything else

Sanaa's header authorises exactly this class of correction, verbatim:

> Every theory gate below: the team pulls the PRIMARY reference, verifies the
> formula and constants against it (quote page), and only then freezes — **the
> constants written here are to be checked, not trusted.**

### 2.1 DEPARTURE 1 — the theory gate's basis is EQUAL POWER, and only equal power

**Directive §2.7(a) as written:** *"the simulated static `T_total / T_open` (run the
open disk, **same delta_p and power**, same domain)"* against the ideal
`(2 sigma)^(1/3)` and band `[1.05, 1.26]`.

**"Same delta_p" and "same power" are two different bases and they give two
different numbers.** They are simultaneously satisfiable at one value of sigma only,
and it is not one of the registered values. Derived independently by this lane and
reproduced symbolically in §12:

| basis | ideal `T_total / T_open` | sigma=0.85 | sigma=1.0 | sigma=1.2 |
|---|---|---|---|---|
| **equal power** | `(2 sigma)^(1/3)` | 1.1935 | **1.2599** | 1.3389 |
| **equal delta_p** | `2 sigma` | 1.7000 | **2.0000** | 2.4000 |
| ratio between bases | `(2 sigma)^(2/3)` | 1.4244 | **1.5874** | 1.7926 |

The two coincide only where `2 sigma = (2 sigma)^(1/3)`, i.e. `sigma = 0.5` — and
`sigma_d = 0.5` **is the open rotor**, independently, per Chew et al. (2021) printed
p.5 eq (7): *"which can be predicted as 0.5 for open rotor configurations using
simple momentum theory."* The registered sigma values are 1.0, 0.85 and 1.2. None is 0.5.

**`(2 sigma)^(1/3)` is an EQUAL-POWER result.** Frozen as the directive words it,
the gate would compare an equal-delta_p measurement reading 2.0 against a band whose
upper edge is 1.26 and return `GATE FAIL` — a failure caused **entirely by the basis
mismatch and not by any physics**, and unrepairable after first compute because
rule 2 closes the gate. This registration therefore **names EQUAL POWER**.

*Ruled by `cfd-supervisor` before drafting; recorded here as a departure, not as a
lane's discretion.*

### 2.2 DEPARTURE 2 — BOTH ratios are registered, one gated and one reported

So that a basis confusion can never hide again, two quantities are registered:

- **(i) GATED — `T_total / T_open` at EQUAL POWER.** Ideal `(2 sigma)^(1/3)`;
  band `[1.05, 1.2599]` at sigma = 1.0. Requires the open-disk reference solve (§7).
- **(ii) REPORTED, NEVER GATED — `T_total / T_disk`.** Ideal `2 sigma`. This costs
  **no extra solve**: §2.6 already computes `T_disk = delta_p * A_disk` as an input.

**1.26 and 2.0 are BOTH correct, on their own bases. Conflating them is the exact
failure mode this two-ratio structure exists to prevent.** A report carrying only
one of them invites a reader to check it against a published augmentation figure
computed on the other basis, and the numbers differ by up to 79%.

**A stronger statement this lane derived, which the ruling did not claim and which
makes the structure airtight** (§12 proves it symbolically): for an open disk at
static conditions, `T_open == delta_p_open * A` *identically*. Therefore at equal
`delta_p`, `T_open == T_disk` exactly, and **ratio (ii) is not merely a sibling of
the equal-delta_p augmentation — it IS the equal-delta_p augmentation, exactly, and
it is available for free.** Registering (ii) is registering the equal-delta_p arm of
the comparison at zero compute cost. The two arms of §2.7(a) are therefore *both*
delivered, which is closer to the directive's evident intent than either alone.

### 2.3 DEPARTURE 3 — the matched power is `P_disk = delta_p * Q`, and the open-disk reference is a ROOT-FIND

§2.6 defines two powers and asks for both:
`P_ideal = mdot (V_e^2 - U_inf^2) / 2` and `P_disk = delta_p * Q`.
With real duct losses **these diverge**; "equal power" is undefined until one is named.

**REGISTERED: the matched power is `P_disk = delta_p * Q`**, the volume-flow work
done by the source. Reasons, in order:

1. It is a **volume integral at the disk**, computed from the imposed `delta_p` and a
   `surfaceFieldValue` volumetric flow through the disk plane. It requires **no
   far-slipstream sampling**, and therefore does not inherit the `V_e` definition
   problem that OPEN-1 turned on (§14, resolved in §9.6/§9.6a).
2. **The two powers coincide EXACTLY in the ideal limit on BOTH arms** — verified
   symbolically in §12, for the ducted arm and the open arm separately. So the choice
   between them **does not perturb the theory constant `(2 sigma)^(1/3)` at all**;
   their divergence in the simulation is a pure measure of loss, not a basis change.
   This was not obvious in advance and is the fact that makes the choice safe.
3. Geldenhuys p.7's source (Black et al. 1968) is quoted at *"the same **ideal**
   power"*. Because of (2), matching `P_disk` reproduces the same ideal constant;
   the difference is second-order in the losses.

**REPORTED alongside, not gated:** the ratio `P_ideal / P_disk` measured on **both**
arms. That ratio is the honest bound on how much the basis choice could have moved
the gated number, and it is published whether it is flattering or not.

**The open-disk reference is a ROOT-FIND over `delta_p_open`, not a single solve.**
Registered fully in §7 with tolerance, bracket, iteration cap and cost. *A gate whose
reference cannot be produced inside the registered budget is not a gate.*

### 2.4 DEPARTURE 4 — `volumeMode` is registered explicitly, because the directive's units are correct in only one of two modes

**Directive §2.3:** *"`injectionRateSuSp = delta_p / t` (N/m^3)"*.

Read in the v2606 source on this box,
`/usr/lib/openfoam/openfoam2606/src/fvOptions/sources/general/semiImplicitSource/SemiImplicitSource.C`:

- `volumeMode` is a **required** dictionary entry — `read()` at `:534` calls
  `volumeModeTypeNames_.get("volumeMode", coeffs_)`, a `get`, not a lookupOrDefault.
- `:537-540`: mode `absolute` sets `VDash_ = V_`, the **cell-zone volume**;
  mode `specific` leaves `VDash_ = 1`.
- `:348`, `:357`, `:367`: the supplied value is **divided by `VDash_`**.

Therefore the supplied number is a **total over the zone** under `absolute` and a
**per-unit-volume density** under `specific`. **`delta_p / t` in N/m^3 is correct
under `specific` and wrong by a factor of the zone volume under `absolute`** — here
about `5.9e-4 m^3` on the 5-degree wedge, i.e. **roughly three to four orders of
magnitude of under-loading**. The case would still mesh, still run, still converge,
and still produce a smooth, plausible, entirely wrong map. The class-C constructor
default is `vmAbsolute` (`:224`).

**REGISTERED: `volumeMode specific;` appears verbatim in the frozen `fvOptions`.**
A second, independent reason: `specific` is **wedge-invariant** — a per-unit-volume
density is the same number whatever the wedge angle, whereas `absolute` would have to
be rescaled by 5/360 and is one silent factor-of-72 away from being wrong.

The type name is confirmed present in this build:
`semiImplicitSources.C:34` — `makeFvOption(SemiImplicitSource, vector)` registers
`vectorSemiImplicitSource`.

### 2.5 DEPARTURE 5 — the thrust sign convention is fixed, because §2.3's parenthetical is ambiguous

§2.3 reads *"in +x (thrust direction pointing upstream ...)"*. With the freestream
entering at the upstream boundary and flowing in +x, a source that adds +x momentum
to the fluid produces a reaction on the duct in **-x**. "+x" and "thrust pointing
upstream" are both true, of two different vectors. Registered explicitly:

- Freestream and bulk flow: **+x**. Upstream is **-x**.
- Momentum source on cellZone `disk`: **+x** (accelerates the fluid downstream).
- **Thrust is positive in -x.** `T_disk`, `T_duct` and `T_total` are all reported as
  **positive when propulsive**. Every reported force is the -x component, times -1.
- **`T_duct` changing sign** (§2.7 report item) means the duct has become net drag —
  `T_duct` goes negative under this convention.

### 2.6 DEPARTURE 6 — the wedge scale factor is registered as a named constant

The domain is a **5-degree wedge**, i.e. `5/360 = 0.01388889` of the annulus. The
`forces` function object integrates over the wedge patches only and returns
`5/360` of the full annular force. **Every thrust reported by this case is the wedge
force multiplied by the registered constant `WEDGE_SCALE = 72.0` (= 360/5).**

This is a classic axisymmetric error and it is silent: a factor-72 error produces a
map that is smooth, monotone and self-consistent. It is caught by the planted control
in §6, which computes `T_disk` two independent ways.

### 2.7 DEPARTURE 7 — the compute cap is raised to 400 core-min, UPWARD and DISCLOSED

**Directive §2.8 states a cap of 320 core-min. This registration registers 400.** The
departure is upward, it is disclosed here rather than taken silently, and **Sanaa may
overrule it.**

**Why her own §2.8 does not close:** §2.8 budgets the 24-solve map at "~4 core-h" =
240 core-min, and this registration costs the gates that must precede it at 144
(§10). 144 + 240 = **384 > 320**. The arithmetic in the directive is internally
inconsistent, and the only ways to satisfy 320 are to drop gates or to drop map
points.

**Why dropping map points is the wrong answer**, and this is the operative reason:
Sanaa's cost-lift directive, **verbatim, recorded at `docs/LAB_STATE.md:712`**, dated
**2026-08-25**:

> *"I want the three teams to forget about cost constraints for now. We originally had
> them when thelab did not have discipline, but the lab does now. So no team stops
> anything in the name of saving compute. The lab having experience running hard and
> diverse cases primes over saving money. Besides, we have two instances running rn.
> So ample ressources."*

*(Quoted byte-exact, including `thelab` and `ressources`; the board records that her
typos are deliberately preserved as provenance and are not to be normalised.)*

**This case is squarely inside that lift and does not rely on any inference.** "The
three teams" are `cfd`, `ansys-verification` and `heat-transfer` — the three she then
addresses by name in the same directive, `cfd` first. **`cfd` is named by her, not
extended to by a chief's reading.** (The board separately marks the extension of the
lift to `dafoam` as the chief's inference and correctable; that clause is irrelevant
here and is not leaned on.)

Deliberately dropping 7 of 24 map points would save roughly **$0.05** and is exactly
"stopping something in the name of saving compute". **Registered cap: 400 core-min.**
Basis: 144 gates + 240 map + ~4% margin. **$0.342 DERIVED NOT MEASURED** at the
owner-stated $0.0513/core-h — far below the $25 pre-authorisation.

**Attribution, kept straight because two different voices are involved:** the words
above are Sanaa's. The operational reading that the directive *"overrides `CLAUDE.md`
rule 12's 'an overrun stops the run' clause, FOR BUDGET REASONS ONLY"* and that
**"caps become RUNAWAY GUARDS, not stop conditions"**, with a crossing *reported to
the supervisor* who *extends by dated amendment* or *stops it*, is **the chief's
reading at `docs/LAB_STATE.md:718-724`, which that page marks "recorded as
correctable"**. This registration adopts the chief's reading and says whose it is.

**Two clauses that survive the lift untouched, and the second is the one most likely
to be misread:**

1. **Costing and calibration continue unchanged** — she lifted *constraints*, not
   *measurement* (`:725-729`). §10.3's `COST_CALIBRATION.md` row is still owed.
2. **THE 15,000-ITERATION CAP IN §8 IS NOT A BUDGET CAP AND IS NOT TOUCHED BY THIS
   LIFT.** It is a **rigor** clause: a run that has not converged in 15,000 iterations
   has not converged, and its verdict is `NOT A RESULT` for that reason and not for a
   financial one. The board's own reading says so — *"RIGOR IS UNCHANGED ... the
   completion rule ... stand exactly as written. No refusal made on evidence is
   reopened by this directive"* (`:730-733`). **"Caps are runaway guards now" applies
   to the COMPUTE cap in §10 and to nothing else in this document.** Registered
   explicitly so that no later reader extends the lift into a gate.

*Ruled by `cfd-supervisor` after this lane declined to widen the ceiling on a
supervisor's assertion; the citation was then verified by this lane at the line given,
and the date corrected from 2026-08-28 to 2026-08-25.*

### 2.8 Departures NOT taken

- The band `[1.05, 1.26]` is **kept as Sanaa wrote it**, with the upper edge stated
  to its verified precision, `1.2599`, and it applies **at sigma = 1.0 only**. The
  secondary sigma sweep (0.85, 1.2) has a **different ideal on every point** and is
  therefore **REPORTED, NEVER GATED** under this registration; it is also outside the
  cost cap (§10). Gating a sigma sweep against a sigma=1.0 band would be a
  manufactured failure of the same species as Departure 1.
- **The 5% band on §2.7(b) is kept exactly as Sanaa wrote it.** What changed under
  OPEN-1 is the **quantity** the band is applied to, not the band — see §9.6. The
  directive's literal quantity survives as a reported number in §9.6a, so nothing she
  asked for is discarded; one reading is gated and the other is published beside it.

---

## 3. Theory: the constant, derived and verified THREE ways

### 3.1 This lane's own symbolic derivation

Static conditions, ideal (inviscid, uniform, no losses), disk area `A`, exit area
`sigma A`, ambient static pressure at the exit plane.

```
continuity      A V_d = sigma A w              =>  V_d = sigma w
mass flow       mdot  = rho A V_d = rho sigma A w
thrust          T_total = mdot w = rho sigma A w^2
Bernoulli       delta_p = (1/2) rho w^2
disk input      T_disk  = delta_p A = (1/2) rho A w^2
                  =>  T_total / T_disk = 2 sigma
open disk (sigma_d = 0.5, V_d = w_o/2):
                T_open  = (1/2) rho A w_o^2 == delta_p_open * A     (identity)
ideal power     P = mdot w^2 / 2 ;   P_disk = delta_p Q     (equal, both arms)
equal power     sigma w^3 = 0.5 w_o^3   =>  w_o = (2 sigma)^(1/3) w
                  =>  T_total / T_open |_equal power = (2 sigma)^(1/3)
                  =>  T_total / T_open |_equal delta_p = 2 sigma
```

Equivalent closed form: `T_duct / T_open = 4^(2/3) sigma^(1/3) / 2 = (2 sigma)^(1/3)`.
At sigma = 1: `4^(2/3)/2 = 1.2599210498948732`.

Machine-checked with SymPy; the script is registered in §12 and lands beside the case
at freeze. Nothing in this section is quoted from memory.

### 3.2 Chew, Gan & Hesse (2021) — printed p.5, PDF p.6

`docs/papers/powered_lift_and_ducted_propulsion/chew_gan_hesse_2021_shrouded_rotor_rapid_design.pdf`
(sidecar `.txt` alongside). Filed at commit **`1ae12da5`**.

Printed p.5 carries, verbatim:

> `P_i = T^(3/2) / sqrt(4 sigma_d rho A)`  — numbered **(6)**
>
> where the expansion ratio `sigma_d` is `sigma_d = A_e / A` — numbered **(7)** —
> *"which can be predicted as 0.5 for open rotor configurations using simple
> momentum theory. For a shrouded rotor, the expansion ratio is the shroud exit
> area `A_e` over the throat area `A_t`."*

Inverting eq (6) at fixed `P_i` and fixed `A`:
`T = P_i^(2/3) (4 sigma_d rho A)^(1/3)`, so
`T_duct / T_open = (sigma / 0.5)^(1/3) = (2 sigma)^(1/3)`. **Independent confirmation
of §3.1, and confirmation that the basis is power.**

**TWO DISCLOSURES ON THIS SOURCE, made here rather than discovered later:**

1. This is the **University of Glasgow Enlighten ACCEPTED-VERSION deposit**
   (eprints.gla.ac.uk/227960/), not the AIAA version of record. Its own cover page
   warns: *"There may be differences between this version and the published version.
   You are advised to consult the publisher's version if you wish to cite from it."*
   Disclosed, not hidden. The relation is corroborated independently by §3.1 and §3.3.
2. **The paper numbers two different equations "(6)".** The mass-flow relation
   `mdot = rho A_e w` and the ideal-power relation `P_i = T^(3/2)/sqrt(4 sigma_d rho A)`
   both print as **(6)** on p.5. The equation cited above is the **second** one, the
   ideal-power relation; it is identified by its content, not by its number. A citation
   of "eq (6)" in this document without that qualifier would be ambiguous. Recorded so
   that a later reader checking the page does not think the citation is wrong.

Title page verified by reading the PDF's own cover (rule 15), not by filename or hash.

### 3.3 Geldenhuys (2015) — printed p.7, PDF p.23

`docs/papers/powered_lift_and_ducted_propulsion/geldenhuys_2015_contrarotating_shrouded_rotor_thesis.pdf`
(sidecar `.txt` alongside). Filed at commit **`1ae12da5`**.

Printed p.7, verbatim (the page number `7` prints immediately after this passage):

> *"The theoretical ideal thrust produced in static conditions by a shrouded propeller
> with an expansion ratio of unity is 26% more than for the same isolated propeller,
> with the thrust produced by the rotor and the shroud being approximately equal. With
> larger expansion ratios, the ideal static thrust growth increases as the cube root
> of the ratio."*

Three separate confirmations in one sentence:

- **"26% more"** = 1.26 = `(2 x 1)^(1/3)` at sigma = 1 — ratio **(i)**, equal power.
- **"rotor and shroud ... approximately equal"** = the duct carries half the total,
  i.e. `T_total / T_disk = 2` at sigma = 1 — ratio **(ii)**.
- **"increases as the cube root of the ratio"** = the `^(1/3)` exponent, in words.

And the surrounding text establishes the basis: the immediately preceding sentence
attributes Black et al. (1968)'s *"up to 67% increase in thrust for the **same ideal
power**"*. **Both registered ratios appear in the same published sentence, on their
two correct bases** — which is exactly why registering only one of them would be a
trap. Title page verified by reading the PDF's own title page (rule 15).

**Consistency note this lane checked rather than assumed:** the 50/50 split and the
1.26 augmentation are simultaneously true and do not contradict. The split is an
*internal* property of the ducted flow at a given exit velocity; the 1.26 is an
*external* comparison at matched power. §12 confirms both hold at once at sigma = 1.

---

## 4. Geometry — registered numbers (§2.2)

Axisymmetric, single 5-degree wedge, one cell thick, `wedge` patches `front`/`back`.

| Quantity | Symbol | Value |
|---|---|---|
| Duct inner diameter | `D` | 0.25 m *(eQ250-class scale; **chosen for scale, not as their geometry**)* |
| Duct length | `L` | 0.8 D = 0.200 m |
| Inlet lip | elliptical | `r_lip/D` = 0.06 (primary); 0.03 / 0.10 secondary, ungated |
| Exit-area ratio | `sigma` | **1.0 (primary, gated)**; 0.85 / 1.2 secondary, ungated |
| Disk axial position | | `x = 0.35 L` from the lip highlight = 0.070 m |
| Disk thickness | `t` | 0.02 D = 0.005 m |
| Tip gap band | | 1% D = 0.0025 m — **declared and disclosed** |
| Disk outer radius | `r_tip` | D/2 - 0.01 D = **0.12250 m** |
| Hub diameter | `D_hub` | 0.3 D = 0.075 m, so `r_hub` = **0.03750 m** |
| **Disk area (full annulus)** | `A_disk` | **0.0427257 m^2** = pi (r_tip^2 - r_hub^2) |
| Wedge scale | `WEDGE_SCALE` | **72.0** (= 360/5) |
| Farfield radius | | 15 D = 3.75 m |
| Upstream / downstream extent | | 10 D = 2.5 m / 25 D = 6.25 m |
| Axis patch type | | `empty` — the v2606 wedge+empty-axis pattern; **recorded** |

Centerbody: hub of diameter 0.3 D with a rounded nose ahead of the disk and a tail
cone behind. The exact profile is **registered as an artifact at freeze**
(`case/geometry/centerbody_profile.csv`, produced by the parametric script), not
described in prose here — a profile described in words is not reproducible.

**`A_disk` is annular, not circular. The hub occupies exactly 9.00% of the duct
frontal area, the tip-gap band a further 3.96%, so the disk annulus covers 87.04%.
The theory of §3 is derived for a HUBLESS disk.** Resolved in **§7.1**: the centrebody
is present in **both** arms of the theory-gate ratio, so the departure from the hubless
ideal falls in the same direction on both and the comparison stays controlled. The
blockage fractions are a **disclosed departure** and are reported beside the gated
ratio every time it is reported.

Fluid: air, `rho` = 1.2 kg/m^3, `nu` = 1.5e-5 m^2/s, incompressible. Registered check
on **every** run: `max|U| < 100 m/s`; any run whose local Mach exceeds 0.3 is
**DISCLOSED** in the record. Ideal exit velocities at the registered loadings are
18.3 / 28.9 / 40.8 / 57.7 m/s, all subcritical, but **static lip suction peaks are
local and are not bounded by these figures** — hence the per-run check rather than an
argument.

---

## 5. Mesh ladder (§2.4) — ONE parametric script, never hand-edited

`case/mesh/make_mesh.py` takes a single level argument and emits the whole
`blockMeshDict` / `snappyHexMeshDict` set. **No level is ever produced by editing
another level's dictionary**, and the script's sha is recorded per level in the
birth certificate.

| Level | Target cells | Role |
|---|---|---|
| L1 | ~30,000 | map, controls, coarsest triple member |
| L2 | ~55,000 | middle triple member |
| L3 | ~100,000 | finest triple member |

**Refinement ratios**, computed from the targets on the wedge's effective 2-D
scaling `r = (N_fine / N_coarse)^(1/2)`:

- `r_21 = (100000/55000)^(1/2) = 1.3484` (L3 -> L2)
- `r_32 = (55000/30000)^(1/2) = 1.3540` (L2 -> L1)

Both exceed the required 1.3. They are **not equal**, so the **non-constant-ratio
Roache formulation is used** and the constant-`r` shortcut is **registered as
forbidden here**, even though the ratios differ by only 0.4%.

**The targets above are targets. The ACTUAL cell counts and the ACTUAL ratios
recomputed from them are recorded in each birth certificate and are what the
comparator uses.** A registration that grades against a target it did not achieve is
grading against a wish.

Registered mesh requirements: first-cell `y+ <= 1` on duct inner and outer surfaces
and on the hub; `>= 40` cells around the lip radius on L1, scaled with `r` above;
`>= 4` cells across the disk thickness `t` on L1; slipstream refinement to 5 D
downstream.

**checkMesh gates, per level, all three required:** max non-orthogonality `< 65`;
max skewness `< 4`; **zero negative volumes**. A level failing any one of these is
`NOT A RESULT` and **no solve is launched on it**.

**Birth certificate per level** (`case/mesh/BIRTH_L<n>.json`): actual cell count,
recomputed refinement ratio against the next-coarser level, the three checkMesh
values, the `y+` histogram after the first solve, the mesh script sha, and the
generating command line.

---

## 6. THE PLANTED CONTROL — runs on L1 BEFORE any gated solve (§2.3, §2.7 V(a))

Per Sanaa's control-birth directive of 2026-08-28, verbatim:

> *A control defined in terms of the thing it controls is not a control. A planted
> control must travel the real production path — written by the real producer's code,
> read through the real reader — and prove the instrument sees a non-zero the same way
> reality would deliver one.*

and its companion rule: *"was this reader ever shown able to see a non-zero through
the real code path?"* is the **birth requirement** for every reader here.

### 6.1 What the control is, and what it is NOT

**It is NOT a hand-computed check.** The control is a **full L1 simpleFoam solve**
through the **real `fvOptions` path**, with the **real `vectorSemiImplicitSource`**,
read back by the **real function objects and the real comparator** that will grade the
gated runs. Nothing about it is a special code path.

### 6.2 Registered control conditions and refusals

Run: L1, `delta_p = 1000 Pa`, `U_inf = 0` (static), `sigma = 1.0`.

| # | Registered assertion | Refusal if violated |
|---|---|---|
| C1 | Area-averaged static pressure rise across the disk zone, read from the written `p` field by the comparator, equals `delta_p` within **2%** | `NOT A RESULT`; no gated solve is launched |
| C2 | Mass flow through the disk plane is **positive and increased** over the `delta_p = 0` baseline | `NOT A RESULT` |
| C3 | `T_disk` computed two independent ways agrees within **0.5%**: (a) `delta_p * A_disk * 1` analytically = 42.7257 N, and (b) the disk-zone momentum source integrated from the solved fields and multiplied by `WEDGE_SCALE` | `NOT A RESULT` — **this is the clause that catches the factor-72 wedge error and the `volumeMode` factor of §2.4** |
| C4 | **NEGATIVE LIMB — the control must be shown able to FAIL.** The same L1 case is re-run with `delta_p` deliberately mis-set by a factor of 2 (2000 Pa in `fvOptions`, 1000 Pa asserted in the comparator). C1 **must** refuse. **If the mis-set run passes C1, the instrument is blind and the entire case is `NOT A RESULT`** | `NOT A RESULT` for the case, not for the run |

**C4 is one-way** (rule 5's direction): it can only withdraw confidence, never grant
it. It is registered before any gated solve so it cannot be added, dropped or
softened after an answer is in hand.

C3 is the **plant** in rule 3's sense: a known non-zero (`delta_p = 1000 Pa` producing
a predictable 42.7257 N) delivered **the way reality delivers it** — through the
solver, into the written fields, out through the same reader — and the reader must
see it. **A zero from a reader not shown able to see a non-zero is not evidence.**

### 6.3 The second V control — empty-duct pass-through (§2.7 V(b))

L1, `delta_p = 0`, `U_inf = 30 m/s`. Registered assertion:

> `|T_total|` is drag-only and `< 2%` of the loaded-case thrust at
> (`delta_p = 1000 Pa`, `U_inf = 20 m/s`, L1).

and its **sign** must be **negative** under §2.5's convention — a duct with no source
must produce net **drag**. **A positive `T_total` here means the case generates thrust
from nothing and is `NOT A RESULT` regardless of magnitude.** Registering the sign as
well as the magnitude closes a hole the directive's "small" leaves open.

---

## 7. The open-disk reference — a registered ROOT-FIND (Departure 3)

The gated ratio needs an open actuator disk at **the same `P_disk`** as the ducted
arm. `P_disk` is not a control input; `delta_p_open` is. So the reference is produced
by root-finding, and the search is registered here in full.

- **Objective:** `f(delta_p_open) = P_disk,open(delta_p_open) / P_disk,duct - 1 = 0`,
  where `P_disk,duct` is measured on the ducted static gate run at `delta_p = 1000 Pa`.
- **Method:** secant in `log(delta_p)`, because `P_disk ~ delta_p^(3/2)` for a fixed
  geometry, so the objective is near-linear in log-log and the secant is close to exact.
- **Registered initial guess, from the ideal scaling:**
  `delta_p_open,0 = delta_p_duct * (2 sigma)^(2/3) = 1000 * 2^(2/3) = **1587.401 Pa**`.
  Second point `delta_p_open,1 = 1.15 * delta_p_open,0 = 1825.5 Pa`.
- **Registered bracket:** `[200, 4000] Pa`. An iterate outside the bracket
  **terminates the search**; the gate is then `NOT A RESULT`, never widened.
- **Registered tolerance:** `|P_disk,open - P_disk,duct| / P_disk,duct <= 0.5%`.
- **Registered maximum iterations: 6.** Expected 3.
- **Hitting 6 iterations without meeting tolerance -> `NOT A RESULT`, never
  "close enough".** No extra iterations are granted; §10's cap is the second stop.
### 7.1 REGISTERED geometry of the open arm — the centrebody stays in BOTH arms

**The open reference is the same annular disk (same `r_tip`, same `r_hub`) with the
SAME CENTREBODY — hub, nose and tail cone — in the same wedge domain, with the DUCT
REMOVED.** Correspondingly, `A_exit` in `sigma = A_exit / A_disk` is the **annulus** at
the exit plane, with the tail cone terminating **at** the exit plane, so both areas in
the ratio are measured the same way.

**Why, and it is the reason to write down: this makes the comparison CONTROLLED. The
duct is then the ONLY thing that differs between the arms**, which is the single change
the ratio exists to isolate.

**The honest cost of that choice, registered rather than discovered later.** Both arms
now depart from the hubless ideal that `(2 sigma)^(1/3)` describes:

- The hub occupies **exactly 9.00%** of the duct frontal area (`r_hub/r_duct = 0.3`,
  squared).
- The tip-gap band removes a further **3.96%**, so the disk annulus covers **87.04%**
  of the duct frontal area.
- The tail cone occupies part of the slipstream in both arms.

**The departure is in the SAME DIRECTION on both arms, so the RATIO is less affected
than either arm alone — but it is NOT zero, and this registration does not pretend it
is.** The theory band has only **17 percentage points of headroom** between 1.05 and
1.2599, and **this hub uncertainty eats into that headroom.** The blockage fractions
above are reported beside the gated ratio, every time it is reported.

**The rejected alternative, and why it is worse:** comparing a hub-having ducted arm
against a **hubless** open arm would buy nominal fidelity to the hubless theory by
making the ratio measure **two changes at once** — the duct *and* the centrebody. A
ratio that moves for two reasons cannot attribute its own value. Nominal
theory-fidelity is not worth an uncontrolled comparison.

*Ruled by `cfd-supervisor`, adopting this lane's §7 recommendation; the blockage
fractions were computed by this lane.*

Remaining open-arm conditions:
- The static open disk draws from rest through a farfield `totalPressure`/`inletOutlet`
  pair with `p_0 = 0`, exactly as §2.3 specifies for the ducted static case.
  **Feasibility risk, disclosed: an open disk at static conditions in a finite domain
  entrains from the farfield and is the slowest-converging configuration in this
  case.** It is the first thing to hit the iteration cap. Registered outcome if it
  does: `NOT A RESULT` for the theory gate; the map and the Roache triple are
  unaffected and still stand.

---

## 8. Numerics (§2.5) — and every criterion has an absolute bound beside it

- Solver **simpleFoam**, steady, incompressible, **OpenFOAM v2606**.
- Turbulence **kOmegaSST**, low-Re wall treatment (`y+ <= 1`); the `nut` wall
  treatment is chosen once and **held fixed across all three levels** — a wall
  treatment that changes between levels destroys the Roache triple.
- Schemes as Case 1 §1.4: `Gauss linear` gradients; `bounded Gauss linearUpwind
  grad(U)` for `div(phi,U)`; `bounded Gauss limitedLinear 1` for `div(phi,k)` and
  `div(phi,omega)`; `Gauss linear corrected` laplacians. **Second order throughout on
  every gated level. A first-order run is permitted for feasibility only and is
  LABELLED as such and never graded.**
- SIMPLE: `consistent yes`; relaxation `p 0.3` / `U 0.7`. **The static cases may need
  `U 0.5` (§2.5); whichever is used is RECORDED per run and held fixed across the
  triple.**
- `nNonOrthogonalCorrectors 1`.

**Convergence — residuals AND absolute bounds, all required together:**

| Channel | Criterion |
|---|---|
| Residuals `p, Ux, Ur, k, omega` | `< 1e-6`, **all channels at the same order** — no channel tightened relative to its siblings |
| Thrust stationarity | `|dT_total| < 0.1%` over the last **2000** iterations |
| Disk mass flow stationarity | `< 0.1%` over the last **2000** iterations |
| Continuity | max continuity error `< 1e-8` |
| Blow-up guard | `max|U| < 100 m/s`; Mach > 0.3 anywhere is **DISCLOSED** |

**Iteration cap: 15,000. HIT CAP -> `NOT A RESULT`, NEVER "CLOSE ENOUGH".**
Registered in those words. The 2000-iteration stationarity window means a run
converging in fewer than 2000 iterations has not demonstrated stationarity and is
also `NOT A RESULT`.

---

## 9. Gates

### 9.1 Verdict vocabulary — the only vocabulary this case may use

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.
No synonyms, no hedging prose, no adjectives. `PENDING` is a queue state and is
**never** used to soften a `GATE FAIL`.

### 9.2 V — the two controls

§6.2 (planted `delta_p`, with its negative limb) and §6.3 (empty-duct pass-through).
**Both must pass before any gated solve is launched.** Either failing is
`NOT A RESULT` for the case.

### 9.3 G — Roache triple on `T_total`

At `delta_p = 1000 Pa`, `U_inf = 20 m/s`, `sigma = 1.0`, levels L1/L2/L3.
`Fs = 1.25`. Registered bands: **observed order `p` in [1.3, 2.5]`**;
**`GCI_fine < 3%`**.

The rule-5 order is registered explicitly and is one-way:

1. Any level not iteratively converged (§8) or not plateaued -> **`NOT A RESULT`**.
2. Triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` -> **`NOT A RESULT`**,
   with the value, **both** triples and **both** orders printed beside it.
3. Only `CONVERGING` reaches a band: inside -> `PASS`, outside -> `GATE FAIL`, with
   the GCI printed.

**The gate can only turn a `PASS` or a `GATE FAIL` INTO `NOT A RESULT`. It can never
turn a `NOT A RESULT` into a `PASS` or a `GATE FAIL`.** Registered here in those terms.

**No GCI is quoted when the three values are not monotone.** Registered as a refusal
in the comparator, not as guidance.

### 9.4 THEORY GATE — static augmentation, EQUAL POWER

At `U_inf = 0`, `sigma = 1.0`, `delta_p = 1000 Pa`, on L1 (the level the map runs on).

- **Ideal:** `(2 sigma)^(1/3) = 1.2599210498948732`.
- **Band, registered before compute: `T_total / T_open` in `[1.05, 1.2599]`.**
- Reference produced by the §7 root-find at matched `P_disk`.
- **The upper edge is the ideal, and exceeding it is a `GATE FAIL`, not a triumph.**
  A real duct has losses; a simulated augmentation above the inviscid ideal is
  evidence of an instrument error (force integration, `volumeMode`, `WEDGE_SCALE`,
  or a root-find that did not converge) and the gate says so in that direction.
- The **shortfall below 1.2599 is reported as duct loss**, per §2.7(a).
- Registered choice, disclosed: **the gate point is `delta_p = 1000 Pa`**, matching
  the Roache triple's loading. §2.7(a) does not name a loading; this one is chosen so
  the gated point and the graded triple share a loading and the GCI band is
  transferable. Other loadings at static are **reported, never gated.**

### 9.5 REPORTED, NEVER GATED — the second ratio

`T_total / T_disk`, ideal `2 sigma` = **2.0000** at sigma = 1.0. Costs no solve.
Reported at **every** map point. **Identically equal to the equal-delta_p
augmentation** (§2.2, proved in §12).

Also reported and never gated: `P_ideal / P_disk` on **both** arms (§2.3).

### 9.6 GATED — forward-flight momentum balance, proper control volume

**Evaluated at `delta_p = 1000 Pa`, `U_inf = 20 m/s`, `sigma = 1.0`, L1** — the **same
state as the Roache triple of §9.3**, so the consistency gate and the triple share one
converged solution and the GCI band of §9.3 applies to both. **§2.7(b) names no state;
this state is `cfd-supervisor`'s choice and is recorded as theirs, not Sanaa's.** It
also means this gate costs **zero additional solves** — it is post-processing on a
solution stage 4 already buys.

**GATED quantity — momentum flux plus the pressure term over a downstream plane `S` at
`x = 3 D`, integrated to the farfield radius `R = 15 D` and multiplied by
`WEDGE_SCALE`:**

```
T_momentum = WEDGE_SCALE * [ integral_S rho u_x (u_x - U_inf) dA
                           + integral_S (p - p_inf) dA ]
```

**Registered band, as Sanaa wrote it: `|T_momentum - T_total| / T_total <= 5%`.**
Outside -> `GATE FAIL`.

This form **needs no point sampling and no `V_e` at all**, which is precisely why it
is the gated one: the quantity that made the literal reading unsafe does not appear in
it. `T_total` is the force integration of §2.6; the gate tests the two against each
other, which is what §2.7(b) says in prose it exists to do — *"forces vs momentum
balance — if it fails, the control-volume integration is wrong before the physics is
questioned."*

**Companion refusal, registered because the balance above neglects the lateral
control-surface term.** The form is exact only if the lateral boundary at `r = R`
carries negligible momentum flux. That is asserted, not assumed:

> The control volume's **mass** imbalance — mass flux at `S` minus mass flux at the
> inlet plane minus lateral inflow — is computed and reported as a percentage of the
> disk mass flow. **If it exceeds 1%, the control volume is not closed, its momentum
> statement cannot be trusted, and this gate is `NOT A RESULT`** — never a `GATE FAIL`,
> because a `GATE FAIL` would blame the physics for an integration that did not close.

### 9.6a REPORTED, NEVER GATED — the literal reading, with its caveat attached

The directive's own form is computed and published beside the gated one:

```
T_literal = mdot_disk * (V_e - U_inf)
```

with **`V_e` registered as a MASS-FLUX-WEIGHTED MEAN, not a point maximum and not an
on-axis value**: at the plane `x = 3 D`, let `r_s` be the radius satisfying
`integral_0^{r_s} rho u_x dA = mdot_disk` — the streamtube that actually carries the
disk mass flow — and

```
V_e = integral_0^{r_s} rho u_x * u_x dA  /  integral_0^{r_s} rho u_x dA
```

**The hub-wake caveat travels with this number wherever it is reported**, in these
terms: *this case has a 0.3 D hub and a tail cone, so the axis at 3 D lies in the hub
wake — the slowest part of the slipstream. A `V_e` read as an on-axis or point-maximum
value would sample a near-minimum of the slipstream and call it the maximum. The value
reported here is a mass-flux-weighted mean over the disk streamtube and is not
comparable to a point reading.*

**Same two-quantity structure as §2.2, and for the same reason:** two plausible
readings of one published requirement exist, both are registered before compute, and
neither can be quietly substituted for the other once the answer is known.

### 9.7 Physicality — required on every run

Continuity closure (§8); no reversed flow at the farfield boundary; `k` and `omega`
realisable and positive; `max|U|` bound.

### 9.8 Reported, not gated

The thrust-vs-airspeed map at four loadings with GCI bands (**disclosed: the band is
measured at ONE point, `delta_p = 1000 Pa` / `U_inf = 20 m/s`, and applied to all —
a stated approximation, per §2.8's own economics, until per-point triples are
affordable**); the airspeed at which `T_duct` changes sign; lip-separation onset
across the map; exit velocity profiles; `P_ideal / P_disk` per point.

---

## 10. Cost — core-minutes, per rung, with a registered cap and a registered STOP ORDER

Rule 12: the unit is **core-minutes** (wall s x ranks / 60). **A proposal with no cost
is disqualified.**

**Registered cap: 400 core-minutes**, departing upward from §2.8's 320. The full
basis, the verbatim directive it rests on, and the attribution of which sentence is
Sanaa's and which is the chief's are in **§2.7**. Under that directive the compute cap
is a **RUNAWAY GUARD, not a stop condition**: a crossing is **reported to the
supervisor**, who extends by dated amendment if the work is sound or stops it if the
run is genuinely stuck. **This applies to the compute cap in this section and to
nothing else in this document — the 15,000-iteration cap of §8 is a rigor clause and
is untouched (§2.7).**

Per-solve estimates from §2.8:
L1 ~ 10, L2 ~ 15, L3 ~ 25 core-min (§2.8 gives 5-15 per solve; 10 is taken for L1,
and L2/L3 scaled by cell count).

| Stage | Content | Solves | Est. core-min | Running |
|---|---|---|---|---|
| 0 | Mesh + checkMesh, all three levels (no solve) | 0 | 4 | 4 |
| 1 | **Controls** — §6.2 planted (1) + §6.2 C4 negative limb (1) + §6.3 pass-through (1) | 3 | 30 | 34 |
| 2 | **Theory gate arms** — ducted static (1) + open-disk root-find (up to 6) | 7 | 70 | 104 |
| 3 | **Roache triple** — L2 + L3 at (1000 Pa, 20 m/s); L1 comes from the map | 2 | 40 | 144 |
| 4 | **Map** — 4 loadings x 6 airspeeds at L1, minus points already run | 24 | 240 | 384 |
| | **PROJECTED TOTAL** | | **384** | vs cap **400** |

The §9.6 momentum-balance gate and §9.6a add **no solve**: they are post-processing on
the (1000 Pa, 20 m/s) L1 solution that stage 4 already buys and that stage 3's triple
already uses. Sharing that one state across three gates is deliberate.

### 10.1 THE FULL MAP RUNS. THE ORDERING BELOW IS A RUNAWAY GUARD, NOT THE PLAN.

**All 24 map points are budgeted and all 24 are expected to run.** 384 against a cap of
400 leaves ~4% margin. The earlier draft of this document proposed truncating the map
to fit §2.8's 320; **that truncation is withdrawn**, because dropping 7 of 24 points to
save roughly $0.05 is precisely what the cost-lift directive quoted in §2.7 forbids —
*"no team stops anything in the name of saving compute."*

**What is retained, and it is retained for a different purpose:** a **frozen execution
order**, registered before compute so that if the cap is ever approached the
degradation is deterministic and was chosen blind rather than after seeing a result.

1. Stages 0-3 (**144 core-min**) are the gates and they run first, in the order above.
2. Stage 4 runs the full map in this **frozen order**: all six airspeeds at
   `delta_p = 1000` first, then all six at 500, then 2000, then 200. Within each
   loading, ascending `U_inf`. This ordering yields **complete airspeed curves loading
   by loading** rather than a ragged grid, so any interruption — cap, stall, session
   loss — leaves usable curves.
3. **If the running total reaches 400**, the crossing is **reported to the supervisor**,
   who extends by dated amendment or stops the work. It is **not** an automatic kill:
   under the directive in §2.7 a cap crossing is no longer by itself a reason to stop a
   sound run.
4. **If work is stopped at a crossing, the map degrades and the gates never do** — the
   gates are already complete by construction, since they run first. Unrun map points
   are **`PENDING`**, named individually in the results record. `PENDING` is a queue
   state, never a softened verdict.

Any run exceeding **3600 wall s** is a **stall**, is reported as such, and its spend
is stated **gross**, with waste **named separately and never absorbed** into the
estimate-vs-actual ratio.

### 10.2 Dollars, and what may not be claimed

Derived at the owner-stated **$0.0513/core-h** for c7a.4xlarge: 400 core-min = 6.67
core-h = **$0.342, DERIVED NOT MEASURED**. **The box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so `cost_basis` states reported-by-owner, never
measured. This is a CPU run and sits inside the under-$25 pre-authorisation; **a
blanket is not a per-item read** (rule 9), and the per-item cost is registered above
regardless.

### 10.3 Owed at completion, and not optional

Rule 12's estimate-versus-actual calibration: at every process completion this case
compares the pre-registered estimate against actual incurred core-minutes from the
logs, states the **ratio actual/predicted**, attributes the gap (contention, waste,
misprediction — **waste named separately**), and lands **a row in
`docs/COST_CALIBRATION.md`** under that file's append rules, the rule-10 private-index
protocol, and `scripts/append_block.py` (L-405: no heredoc in the write path).
**A completion report without this row is incomplete.**

### 10.4 Provenance of the cost-lift, and how it was established

Recorded because the route to it matters more than the conclusion.

The drafting brief cited the lift to `etc/sessions/2026-08-28T1701Z_...md`. **It is not
there** — that file carries three directives (lesson assigned, re-grade sweep,
freeze-ahead amendment) and none concerns cost. This lane therefore **declined to widen
the ceiling** and registered the 320 cap as a binding stop, on the ground that no
agent's statement is Sanaa's consent (rule 9) and that a supervisor's assertion is not
a citation.

The supervisor then supplied the correct location and **this lane verified it at the
line rather than accepting the correction**: `docs/LAB_STATE.md:712`, quoted verbatim in
§2.7, dated **2026-08-25** — not 2026-08-28 as both the brief and the correction stated.
`cfd` is one of the three teams she names, so the lift reaches this case **directly**
and no chief-side inference is relied on.

**The refusal was correct and the outcome is correct, and they are not in tension.**
Rule 9 asks for a citation, not for obedience and not for obstruction; when the citation
arrived and checked out, the ceiling moved. A cap raised on a verified quotation is a
different object from a cap raised on a message.

---

## 11. Execution discipline — registered as refusals, not as intentions

### 11.1 Strict completion rule (CLAUDE.md rule 4), in full

A run is done **only if every clause holds**. Any one failing means it is not done,
and the comparator **refuses (exit 2) rather than degrades**:

1. `rc = 0`;
2. an `End` line in the solver log;
3. **last time == `endTime`**;
4. fields present at `endTime`: `U p k omega nut` (this case is non-thermal; the
   thermal-family list does not apply and the substitution is registered here);
5. `ExecutionTime` count == `endTime`;
6. **THE AGE GUARD — every field at `endTime` is NEWER than the case's own `0/U`.**
   `0/U` is touched last at launch and so dates the run that was allowed to produce
   the answer. A field older than it is a field from a previous run.

**A guard refuses a case where `0` or any time directory already exists.** No run in
this case is ever started on top of an existing time directory.

### 11.2 Determinism

- **`decomposePar` method and seed are both RECORDED as required fields** in every
  run record. A decomposition whose seed is absent is not reproducible and the record
  is incomplete.
- Rank count recorded per run (it is half of the core-minutes figure).
- The same decomposition is used across all three levels of the triple.

### 11.3 rc and STATUS

- **`rc` is captured INSIDE the detached wrapper, never around the `setsid` line.**
  `setsid timeout cmd` exits 0 for every outcome, including a solver that died; an
  `rc` taken outside reads 0 and certifies a corpse as a completion.
- **`STATUS` is written at exit, by the wrapper, and records the SOLVER rc** — kept
  distinct from any launcher rc, which is an infrastructure record and is never
  offered as evidence of a solve.

### 11.4 STATUS-path choice — a path the queue runner CANNOT occupy

`scripts/queue_runner.py` `launch()` builds, in the case `cwd`:

- `STATUS.<case_id>` and `launcher.queue.out`, **both written with unconditional
  shell `>` truncation**, and the `launcher.queue.out` redirection **truncates at
  argv start, not after the argv completes**.

Consequently **two cases sharing a `cwd` destroy each other's records silently.**

**REGISTERED:** every rung of this case has its **own** `cwd`, of the form

```
verification/runs/F28_runs/<rung_id>/
```

with `<rung_id>` unique per solve (`L1_dp1000_U20`, `OPEN_iter3`, `CTRL_PLANT`, ...).
Verified at drafting time by this lane: **no `launcher.queue.out` exists anywhere
under `verification/runs/F28_runs/`** — the directory does not exist — and none of
the ten existing `launcher.queue.out` files on the box is under a path this case
would claim. **No rung of this case ever uses the repository root, `cases/`, or a
shared parent as its `cwd`.**

*(The run root is registered here. It is NOT created — see the freeze notice at the
top of this document.)*

### 11.5 Filing

- Pre-registration: **this file**, `verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`
  (FILING_CHARTER R7, `<RUNG>_<PURPOSE>.md`).
- Run outputs: `verification/runs/F28_runs/` (R6 — **never** beside the prose).
- Helper code inside the campaign directory: `lower_snake.py` (R7).
- Papers already filed correctly under `docs/papers/powered_lift_and_ducted_propulsion/`
  with matching `.txt` sidecars (R8).
- `scripts/check_filing.py` is run on this path before freeze.

### 11.6 Comparator freeze

The grading path is **fixed at the pre-registration commit**. Before grading, the
frozen comparator on disk is **hashed against its committed blob** and must match;
`scripts/check_comparator_freeze.py` enforces. After first compute, gates, thresholds,
caps and labels are closed; changes land only as dated addenda that cannot alter any
of them. **Originals are struck, never rewritten.**

### 11.7 Disclosure required on every surface

*"Actuator-disk representation; no rotor"* — §2.1, on every figure, table and record
this case produces.

---

## 12. The derivation script — registered artifact

`verification/campaign/f28_derive_theory_constant.py` (to land at freeze; drafted and
run at `.../scratchpad/cfd_case2/derive.py`). It is symbolic, not numeric fitting, and
it prints, all verified by this lane:

```
ideal vs disk power coincide (duct): True
ideal vs disk power coincide (open): True
T_open == dp_open*A                : True
T_tot/T_disk                       = 2*sigma
w_o at equal power                 = 2**(1/3)*sigma**(1/3)*w
T_tot/T_open |equal power          = 2**(1/3)*sigma**(1/3)
T_tot/T_open |equal delta_p        = 2*sigma
  sigma=0.85  equalPower=1.1935  equalDeltaP=1.7000  ratio=1.4244
  sigma=1.0   equalPower=1.2599  equalDeltaP=2.0000  ratio=1.5874
  sigma=1.2   equalPower=1.3389  equalDeltaP=2.4000  ratio=1.7926
  sigma=0.5   equalPower=1.0000  equalDeltaP=1.0000  ratio=1.0000
4^(2/3)*sigma^(1/3)/2 at sigma=1   = 1.2599210498948732
```

The `sigma = 0.5` row is the **self-check**: at the open-rotor expansion ratio both
bases give exactly 1.0, which is the only value they can give, and it independently
confirms Chew p.5 eq (7)'s `sigma_d = 0.5` for an open rotor.

---

## 13. Registered outcomes — every way this case can end

| # | Condition | Verdict |
|---|---|---|
| 1 | Any checkMesh gate fails on any level | `NOT A RESULT`; no solve on that level |
| 2 | Planted control C1/C2/C3 fails | `NOT A RESULT` for the case |
| 3 | Negative limb C4 passes when it must fail | `NOT A RESULT` for the case — instrument blind |
| 4 | Empty-duct pass-through fails magnitude or **sign** | `NOT A RESULT` for the case |
| 5 | Any run hits the 15,000 iteration cap | `NOT A RESULT` for that run — never "close enough" |
| 6 | Any run fails any clause of §11.1 | `NOT A RESULT`; comparator refuses exit 2 |
| 7 | Triple not `CONVERGING`, or values not monotone | `NOT A RESULT`; no GCI quoted |
| 8 | Triple `CONVERGING`, `p` outside [1.3, 2.5] or GCI_fine >= 3% | `GATE FAIL` |
| 9 | Triple `CONVERGING`, `p` in band and GCI_fine < 3% | `PASS` on G |
| 10 | Root-find exceeds 6 iterations or leaves the bracket | `NOT A RESULT` for the theory gate; G and the map stand |
| 11 | `T_total/T_open` in [1.05, 1.2599] | `PASS` on the theory gate |
| 12 | `T_total/T_open` outside that band, **either edge** | `GATE FAIL` |
| 13 | §9.6 control-volume mass imbalance > 1% | `NOT A RESULT` for the balance gate — never `GATE FAIL` |
| 14 | §9.6 balance outside 5% with the CV closed | `GATE FAIL` |
| 15 | Cost reaches the 400 core-min cap | crossing **reported to the supervisor**, who extends by dated amendment or stops; if stopped, remaining map points `PENDING`, named individually — gates already complete by construction |
| 16 | This document is not frozen by the supervisor | `PENDING` — the current state |

---

## 14. THE THREE OPEN QUESTIONS — ALL RULED. RECORD OF WHO RULED WHAT.

All three items this lane raised and declined to decide have been ruled by
`cfd-supervisor`. Each ruling is recorded **with its author**, because a registration
that does not say whose choice a gate embodies cannot later be audited for whether the
gate was chosen to fit an answer.

**None of the three was decided by the lane that raised it, and none was decided after
seeing any result — no compute has been run.**

| Item | Ruling | Where it now lives | Ruled by |
|---|---|---|---|
| **OPEN-1** — §2.7(b) ill-posed: `V_e` ambiguous, and the axis at 3 D sits in the **hub wake**, the slowest part of the slipstream | Adopt the **proper control-volume balance including the pressure term** as the GATED quantity; **report** the literal reading with `V_e` redefined as a **mass-flux-weighted mean over the disk streamtube**, never a point maximum or an on-axis value, with the hub-wake caveat attached | **§9.6** (gated, + CV-closure refusal) and **§9.6a** (reported) | `cfd-supervisor`; diagnosis by this lane |
| **OPEN-1a** — §2.7(b) named no state | Evaluate at **`delta_p` = 1000 Pa, `U_inf` = 20 m/s** — deliberately the same state as the Roache triple, so both share one converged solution and the GCI band covers both. Costs **zero extra solves** | **§9.6** | `cfd-supervisor` — **explicitly recorded as their choice, not Sanaa's** |
| **OPEN-2** — "open disk of the same area" under-specified against a 9% hub; `sigma` under-specified by the tail-cone termination | **Centrebody present in BOTH arms**, duct removed from the reference; `A_exit` annular with the tail cone terminating **at** the exit plane. Makes the duct the only difference between arms. Hub blockage disclosed as a departure eating into the band's 17 points of headroom | **§7.1**, and **§4** | `cfd-supervisor`, adopting this lane's recommendation |
| **OPEN-3** — §2.8's own arithmetic does not close (144 + 240 = 384 > 320) | Cap raised to **400 core-min**, disclosed as an **upward** departure Sanaa may overrule; the **full 24-point map runs**; the gates-first ordering is retained as a **runaway guard, not a truncation plan** | **§2.7** and **§10** | `cfd-supervisor`, on Sanaa's cost-lift at `docs/LAB_STATE.md:712` — citation verified at the line by this lane |

### 14.1 What each ruling changed, stated so the change is visible

- **OPEN-1** turned one gate that would have failed on its own formulation into one
  gate that tests what §2.7(b) says in prose it tests, plus one reported number that
  preserves the directive's literal form without letting it decide anything. The
  neglected lateral term is now bounded by a registered **mass-closure refusal**
  (§9.6), so a control volume that does not close returns `NOT A RESULT` rather than
  blaming the physics with a `GATE FAIL`.
- **OPEN-2** chose a **controlled** comparison over a nominally theory-faithful one,
  and paid for it in disclosure: both arms now depart from the hubless ideal, in the
  same direction, and the blockage fractions ride alongside the gated ratio.
- **OPEN-3** removed a self-inflicted scope cut. The earlier draft's truncation is
  **withdrawn** and named as withdrawn in §10.1 rather than quietly deleted.

### 14.2 One item remains open, and it is NOT a gate — **DISPOSED AT FREEZE, 2026-08-31**

> **⚠ SUPERVISOR'S DISPOSITION, 2026-08-31, added at the freeze commit. The item below
> is CLOSED and it was never a blocker. The lane was right to raise it and right about
> where it would lead.**
>
> **The directive has already been actioned, and it was actioned by this team.** The
> title-page verification the lane correctly demanded was performed by the cfd
> supervisor personally on **2026-08-25** and is committed at
> **`docs/standards/High_order_grid_convergence_PROVENANCE.md`**. Its finding, in one
> line: **the filename is false.** The document is **Ekaterinaris, J.A. (2005),
> "High-order accurate, low numerical diffusion methods for aerodynamics", Progress in
> Aerospace Sciences 41 (2005) 192–300**, DOI `10.1016/j.paerosci.2005.03.003` — a
> 109-page review of high-order discretisation schemes.
>
> **It contains no grid-convergence verification apparatus at all.** Discriminated
> (`\b…\b`) counts over the full 66,033-word extraction: **Roache 0, GCI 0,
> Richardson 0, grid refinement 0, mesh refinement 0, verification 0.** The naive
> `grep -i` count of 17 for "Roache" is **17 instances of the substring inside
> "app-roache-s"** — every one. Had that count been believed, the record would have
> reported a paper citing Roache seventeen times, which is the exact opposite of the
> truth **and in the exact direction that would have justified writing GCI lessons
> into the mesh standard.**
>
> **THE CONSEQUENCE FOR THIS REGISTRATION, WHICH IS THE ONLY QUESTION §14.2 ASKED:
> NONE.** F28's Roache triple (§9.3), its observed-order band `p in [1.3, 2.5]`, its
> `GCI_fine < 3%` and its `Fs = 1.25` owe **nothing** to that paper and could not have.
> They come from `CLAUDE.md` rule 5, `MESH_STANDARD.md` §9 and Roache himself. There is
> no unactioned grid-convergence directive bearing on this document, and **the paper
> the directive names could not have borne on it in any case.**
>
> **Standing prohibition, restated here because this registration is exactly the kind
> of document that would tempt someone to cite it:** any clause of the form *"the
> grid-convergence literature says X, per `High_order_grid_convergence.pdf`"* is a
> **fabrication** and is struck on sight, in this file or any other.
>
> **What remains genuinely open is a different and smaller thing, and it is not F28's:**
> the paper *is* valuable to cfd — WENO 160, shock 89, numerical diffusion 6, tip
> vortex 5 — and bears on **F1/ONERA M6's η = 0.99 tip-vortex Cp row** and on F2/F12's
> shock rows, through the **scheme and numerical-diffusion** rows of
> `docs/NUMERICS_KNOWLEDGE.md`. That mining is tracked separately from this case and
> **blocks nothing here.**

**Not blocking this registration; raised for the supervisor's disposition.**

The same board section that carries the cost-lift also carries a standing directive to
this team: Sanaa's `docs/LAB_STATE.md:712` continues, in her own words, that the `cfd`
team *"can also read the High_order_grid_convergence.pdf in docs/standard"*, and the
chief's reading at `:743-745` sharpens that to **"`cfd` reads it FIRST, before
continuing its tasks"**, on the ground that `cfd` did bump into numerical convergence
issues — with the lessons then to be recorded into this team's own charters and, if
`ansys-verification` has not already done so, into the lab's charters, numerics
knowledge and the mesh/verification standards.

**This bears on this registration**, which rests on a Roache triple, an observed order
and a GCI. **And the board attaches a rule-15 warning to that very file:** commit
`01fcb3d8` records that this same PDF was previously found to be **Ekaterinaris 2005 on
high-order low-diffusion schemes — zero Roache, zero GCI, zero Richardson** — while two
teams were about to write its "lessons" into the mesh and verification standards.
**Whoever reads it verifies the title page, never the filename.**

This lane has **not** read it and does not claim to have. It is flagged here because a
supervisor deciding whether to freeze a grid-convergence registration should know an
unactioned directive touching grid convergence is outstanding — and should know it may
point at a paper about something else entirely.

---

## APPENDIX A — DRAFT `N`-ENTRY FOR `docs/NUMERICS_KNOWLEDGE.md` (NOT FILED)

**`NOT FILED`.** This appendix is a **draft** held here so it is not lost. It has **not**
been appended to `docs/NUMERICS_KNOWLEDGE.md`, which is a **lab-wide** document outside
this team's territory. **This lane does not unilaterally edit lab-wide records**, and the
id below is a placeholder: a real id is derived at append time from the tail, as the
**maximum existing number, never a count** (rule 11), in the same shell invocation as the
append, through `scripts/append_block.py` so no heredoc is ever in the write path (L-405).

> ### N-XXX — An OpenFOAM `fvOptions` source can be wrong by the cell-zone volume, silently, and the case still converges
>
> **Class:** converged-but-wrong. **Applies to:** every team using `fvOptions`
> `semiImplicitSource` / `vectorSemiImplicitSource` (and any `cellSetOption` source
> sharing the `volumeMode` mechanism). **Measured in:** OpenFOAM v2606 on this box.
>
> `volumeMode` is a **required** dictionary entry, and it silently rescales the number
> you supply. In
> `src/fvOptions/sources/general/semiImplicitSource/SemiImplicitSource.C`:
>
> - `:534` — `volumeModeTypeNames_.get("volumeMode", coeffs_)`. A `get`, not a
>   defaulted lookup.
> - `:537-540` — `absolute` sets `VDash_ = V_`, the **cell-zone volume**; `specific`
>   leaves `VDash_ = 1`.
> - `:348`, `:357`, `:367` — the supplied value is **divided by `VDash_`**.
> - `:224` — the class constructor's own default is `vmAbsolute`.
>
> So the same number means a **total over the zone** under `absolute` and a
> **per-unit-volume density** under `specific`. A source written in `N/m^3` and run
> under `absolute` is under-applied by the zone volume — on the case that found this,
> a zone of ~5.9e-4 m^3, i.e. **three to four orders of magnitude**.
>
> **Why it is dangerous rather than merely wrong: the case still meshes, still runs,
> still converges to tight residuals, and produces a smooth, monotone, entirely
> plausible map.** There is no crash, no warning and no residual signature. Nothing in
> the completion rule catches it, because every clause of the completion rule is
> satisfied.
>
> **Aggravating factor on axisymmetric wedges:** `specific` is **wedge-invariant** — a
> per-unit-volume density is the same number at any wedge angle — while `absolute`
> must be rescaled by the wedge fraction, one further silent factor (72, for a
> 5-degree wedge).
>
> **The remedy is a control, not care.** State `volumeMode` explicitly in every frozen
> `fvOptions`, and prove the source magnitude through the **real production path**: a
> planted control that computes the imposed quantity **two independent ways** — once
> analytically from the registered inputs, once integrated from the solved fields with
> any geometric scale factor applied — and refuses on disagreement. Then a **negative
> limb**: deliberately mis-set the source by a known factor and require the control to
> **refuse**. A control that has never been shown able to fail has certified nothing
> (Sanaa's control-birth directive, 2026-08-28).
>
> **Found by:** cfd, while drafting `F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`, by
> reading the v2606 source rather than trusting the units written in the brief. **No
> run of this lab is known to be affected; no sweep for affected cases has been done,
> and this entry does not claim one.**

**Owed if this is landed:** a sweep of existing `fvOptions` dictionaries in the repo for
a missing or `absolute` `volumeMode` where the value is dimensionally a density. **That
sweep has NOT been run and nothing here should be read as saying it has.**

---

## 15. What this registration does NOT claim

- **Nothing about a real ducted fan.** There is no rotor, no swirl, no blade loading,
  no tip vortex. The actuator disk is a uniform momentum source and the case says so
  everywhere.
- **Nothing about eQ250 or any product.** `D = 0.25 m` and the loadings 200-2000 Pa
  are **chosen for scale and for the physics**, and are **not** anyone's operating
  points. §2.2 and §2.3 require this statement and it is made.
- **Nothing about the published AIAA version of Chew et al.** The filed copy is the
  accepted-version deposit and its own cover warns it may differ (§3.2).
- **No result.** Not one solve has been run under this document.

---

*Drafted by a `lab-lane` for `cfd-supervisor`, 2026-08-30. **UNFROZEN. `PENDING`.**
The supervisor's `SUPERVISION_CHARTER.md` §3 check 4 — pre-registration committed
before compute — is theirs and has not been performed. Do not launch.*
