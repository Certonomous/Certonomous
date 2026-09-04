# T19b results — fully developed laminar forced convection between parallel plates, EXACT tier; the successor that made T19's registered experiment possible

**Document version 1.0.** Rung `T19b`, pre-registration
`docs/campaigns/T-family/T19b_PREREGISTRATION.md`, frozen at commit
**`b52ed93be3e8937ca9e99823822d3b883abad0b9`** (2026-08-31T15:36:51Z). Run root
`verification/runs/T-family/T19b_runs/`. Graded by the frozen `analyse_t19b.py`;
gate artifact `gate_t19b.json` written **2026-08-31T16:41:23.842Z** and closed at
commit **`74a9141dc7a266c169c06cdd369da218454e26f9`** (16:47:46Z). Drafted by a
heat-transfer `lab-lane` 2026-09-04 on the heat-transfer supervisor's brief;
decisions `[lab-attributed]`.

**THE DECLARED VERDICT — T19b rows G1, G2 and G3: `PASS`.**

**And the rung's registered ceiling is `GATE REACHED`, not higher.**
`T19b_PREREGISTRATION.md:205`–`:208` and `gate_t19b.json:15` both record, before
compute, *"GATE REACHED at best -- the reference is EXACT/derived, so this rung
scores V and never P; it can never reach HOLDS."* **The three `PASS` rows are
gate verdicts against a derived analytic referent; they are not a capability
claim**, and §1 below bounds what may be read from them.

**This record was written 2026-09-04 for a rung graded 2026-08-31.** Until it
existed, T19b's verdict lived only as JSON: `T_FAMILY_INDEX.md` §5.4 filed the
rung under *"REGISTERED, NOT REPORTED — a pre-registration exists and no results
record does"*, under that section's standing instruction that *"None of these
carries a verdict, and none should be cited as a capability."* That instruction
was true of T19b when it was written and is false of T19b now. **Nothing in this
document grades, re-grades or moves anything; it reports a verdict that already
existed and re-derives its grounds from the artifacts.**

---

## 0. SCOPE — stated first, because it bounds everything below

`gate_t19b.json:14` carries the scope the registration fixed, before compute:

> **"FORCED CONVECTION, LAMINAR, 2-D: fully developed parallel-plate channel;
> NOT turbulent, NOT 3-D, NOT conjugate; the entrance region is solved but not
> graded."**

### 0.1 What T19b measures

Laminar flow and heat transfer between two parallel plates, solved with
`buoyantBoussinesqSimpleFoam` at `simulationType laminar`, `beta = 0` and
`g = (0 0 0)` — the configuration that decouples momentum from `T` and makes the
solver a pure incompressible forced-convection solver. **The full gap is meshed;
no symmetry plane is imposed**, so the symmetry of the answer is a *witness*
rather than an assumption (control `C_SYM`, §3).

| quantity | value | source |
|---|---|---|
| full gap `b` / hydraulic diameter `Dh` | 0.02 m / 0.04 m | `T19_PREREGISTRATION.md:108`; `T19_registered.json` `physics` |
| channel length `L` | 1.2 m (30 `Dh`) | same |
| **graded station `x_s`** | **0.8 m (20 `Dh`)**, `x+ = x_s/(Dh·Re·Pr)` = **0.28169014084507044** | `gate_t19b.json:18`–`:19` |
| `nu` / `Pr` / `Re_Dh` / `U0` | 1.5e-05 m²/s / **0.71** / **100** / 0.0375 m/s | `gate_t19b.json:16`–`:17`; `T19_registered.json` `physics` |
| inlet | uniform `U0`, uniform `T_in` = 300 K | `T19_PREREGISTRATION.md:112` |
| walls, `Ts` arm | `fixedValue` **400 K** on BOTH walls | `:113` |
| walls, `q` arm | `fixedGradient` **500 K/m** on BOTH walls | `:114` |
| `endTime` / `deltaT` / `writeInterval` | **30 000 iterations** / 1 / 2 000 | `system/controlDict` of each case |
| ranks / decomposition | **1 / serial, no decomposition** | `T19_registered.json` `cases.*` |

`endTime = 30000` is an **iteration count**, not a physical time — `deltaT` = 1
with steady `ddtSchemes`.

The grid ladder, refinement ratio **`r` = 2 exactly in both directions**:

| level | `nx` × `ny` (full gap) | cells | `dy` (m) |
|---|---|---:|---:|
| `c` | 120 × 20 | 2 400 | 1.0e-03 |
| `m` | 240 × 40 | 9 600 | 5.0e-04 |
| `f` | 480 × 80 | 38 400 | 2.5e-04 |

**The station lies on a cell FACE at every level** (0.8/dx = 80, 160, 320), so
the reader's axial interpolation is the mean of the two straddling columns and is
**the same operation at every level**; `build_t19b.py --check-levels` refuses a
station that is not, and refuses a ladder that is not `r` = 2.

### 0.2 WHAT T19b DOES NOT ESTABLISH — stated as plainly as its result

**A reader who over-reads this record does so against its own face.** Each limit
below is registered, not conceded after the fact.

- **Laminar only.** The registered closure is `simulationType laminar`, which
  instantiates no turbulence model and writes no `nut`, no `k`, no `omega` and no
  `epsilon`. **Nothing turbulent is earned.**
- **ONE Reynolds number.** `Re_Dh` = 100, and only 100. No statement is made or
  implied about any other `Re`, laminar or otherwise.
- **ONE Prandtl number.** `Pr` = 0.71, and only 0.71. Nothing for liquid metals,
  oils, water or any other fluid property set.
- **ONE station.** `x_s` = 0.8 m, `x+` = 0.28169. **The entrance region is solved
  but NOT graded** — no developing-flow quantity is earned anywhere in this rung.
- **2-D planar only.** A parallel-plate channel. Nothing 3-D; nothing
  axisymmetric (the pipe is T1c's rung, and this rung's referent module is
  *cross-checked* against T1c's pipe numbers but grades none of them); nothing in
  any other geometry.
- **Forced convection only.** `beta = 0` and `g = 0` switch buoyancy off by
  construction. **Nothing for mixed or natural convection.**
- **Not conjugate.** There is no solid, no interface and no conjugate coupling.
  Nothing is earned for a solid–fluid interface.
- **Steady only.** Nothing transient.
- **Two wall thermal conditions only** — uniform wall temperature and uniform
  wall heat flux. Nothing for a mixed/Robin wall condition.
- **This is CODE VERIFICATION against a derived analytic referent, NOT VALIDATION
  against a public primary source.** No paper is cited and none is needed; the
  referent is `exact_t19.py`, and **rule 15 is not engaged because no retrieved
  document is relied on anywhere in this rung.** No comparison against published
  experimental or benchmark data is made or claimed.
- **The registered ceiling is `GATE REACHED`.** The rung scores V and never P and
  **can never reach `HOLDS`**. Whether it is worth its ceiling is a supervisor
  ruling and is not taken here.
- **A capability-grid cell is NOT moved by this document.** T19 was registered as
  *"the first graded heat-transfer case proposed for"* the
  `forced convection × laminar × 2D` cell (`T19_PREREGISTRATION.md:4`–`:12`), and
  T19b inherits that intent unchanged (`T19b_PREREGISTRATION.md:210`–`:212`).
  **Whether the cell moves is not this record's call and is not taken in it.**

---

## 1. Freeze verification — the file that ran is the file that was frozen

`git hash-object` on the working tree against `git rev-parse
b52ed93b:<path>`, taken in one shell invocation, at HEAD 2026-09-04:

| file | worktree blob | blob at `b52ed93b` | identical | sha256₁₆ | lines |
|---|---|---|:--:|---|---:|
| `docs/campaigns/T-family/T19b_PREREGISTRATION.md` | `77939ab164791e6d…` | `77939ab164791e6d…` | **YES** | — | 694 |
| `T19b_runs/build_t19b.py` | `b687db4df4411b51…` | `b687db4df4411b51…` | **YES** | `92149d455cd6f64b` | 389 |
| `T19b_runs/analyse_t19b.py` | `32c309e112152bca…` | `32c309e112152bca…` | **YES** | `c7b1822538eb1a51` | 1041 |
| `T19b_runs/mutation_controls_t19b.py` | `663adf76059df65a…` | `663adf76059df65a…` | **YES** | `79dc0962c588382c` | 191 |
| `T19b_runs/T19b_INSTRUMENT_DIFFS.txt` | `7157db64f9cf49ce…` | `7157db64f9cf49ce…` | **YES** | `cf65a1ad9a629209` | 562 |

**All five reproduce, and all four instrument sha256 prefixes match the freeze
table the registration published at `T19b_PREREGISTRATION.md:656`–`:661`.** The
working tree **is** the frozen document, so every band and threshold cited below
by line number is the registered one. Rule 2's grading-path clause is satisfied
by hash rather than by assertion.

### 1.1 THE SHA256 PIN — why no gate could have been chosen to fit the answer

**T19b defines no gate, no threshold, no band, no floor, no cap and no label, and
it does not copy them either.** `analyse_t19b.py` loads T19's own frozen
`T19_registered.json` **by absolute path** and reads every one of them out of the
parent's file, and **pins both parent instruments by sha256 at run time,
REFUSING rather than grading if either digest fails to reproduce**
(`T19b_PREREGISTRATION.md:157`–`:160`).

`gate_t19b.json:4`–`:13` records the two pins in the artifact itself. Both were
re-taken by this lane at HEAD:

| pinned parent instrument | sha256 recorded in `gate_t19b.json` | measured today | worktree blob == HEAD blob |
|---|---|:--:|:--:|
| `T19_runs/T19_registered.json` | `84b3652a5187f04efeddb5b14cc91b2d1c5d9952b7608243bdd0078773a040b4` | **reproduces** | **YES** (`d63e8a4bf5ef8b3a…`) |
| `T19_runs/exact_t19.py` | `aeaae65c9e849c8a40d9594e412e3a1bc63ebe79274f5bc704837570cf52545d` | **reproduces** | **YES** (`053e2b50ee1d7526…`) |

**This is the mechanism by which *"no gate moved"* is a measurement rather than a
claim.** To move a gate under T19b somebody would have to alter the parent's
frozen file, which would break the pin and stop the comparator. Rule 6 is
satisfied by construction: T19b edits none of T19's six frozen files, and all six
were verified byte-identical to their HEAD blobs before the freeze
(`T19b_PREREGISTRATION.md:144`–`:155`) and reproduce again today for the two that
are pinned.

### 1.2 ANALYST BLINDNESS — the second reason the bands could not have been tuned

The registration checked, before compute and by four independent sweeps, that
**no graded T19 quantity had ever been computed by anyone, anywhere on this box**
(`T19b_PREREGISTRATION.md:288`–`:298`): `find / -name 'gate_t19*'` returned 0
hits; `git log --all -- '*gate_t19*'` returned 0 commits; `T19_runs` held 0
`DONE.*` markers, so the frozen comparator refused at its first check and had
never reached a value; and the two graded reference values appeared in exactly
two files, both of them *registrations* rather than measurements.

**So T19b's bands could not have been tuned to T19's answer, because T19 had no
answer.** That is not a claim about anybody's integrity — it is a structural fact
about what existed on disk, and it is checkable by re-running those four sweeps.

---

## 2. Completion — rule 4, six clauses, six of six cases

**The registered field tuple is `('T', 'U', 'p_rgh', 'alphat')` and it was read
from the frozen registration, not assumed.** `T19_registered.json`'s `completion`
block registers it explicitly and states in terms that it was **checked against
the closure this rung registers and not copied from T1b** — *"T1b's
thermal-family tuple `T U p_rgh alphat nut k omega` would therefore make
completion IMPOSSIBLE here — the exact defect that cost K0d its 829 core-minute
rung."*

Every clause below was re-derived by this lane **from the raw artifacts** —
`log.solve`, `system/controlDict`, the time directories and filesystem mtimes.
**The six `DONE.*` markers were NOT consulted as evidence for any clause.**

| clause | `P_q_c` | `P_q_m` | `P_q_f` | `P_Ts_c` | `P_Ts_m` | `P_Ts_f` |
|---|---|---|---|---|---|---|
| 1. `rc = 0` | 0 | 0 | 0 | 0 | 0 | 0 |
| 2. one `End` line | 1 | 1 | 1 | 1 | 1 | 1 |
| 3. last time == `endTime` | **30000 == 30000** | **30000** | **30000** | **30000** | **30000** | **30000** |
| 4. registered tuple present at `endTime` | holds | holds | holds | holds | holds | holds |
| 5. `ExecutionTime` count == `endTime`/`deltaT` | **30000** | **30000** | **30000** | **30000** | **30000** | **30000** |
| 6. **AGE GUARD**: every field at `endTime` newer than that case's own `0/T` | **+63.410 s** | **+231.467 s** | **+1450.873 s** | **+63.154 s** | **+228.757 s** | **+1413.070 s** |

**Six of six cases hold all six clauses. `capped=no`, `checkmesh_rc=0` and
`note=clean` on every case** (`STATUS.<case>`; `capped` is an infrastructure
field and never a completion conjunct, L-342, as the registration itself records).

**THE AGE GUARD IS CORROBORATED BY A SECOND, UNRELATED INSTRUMENT.** `0/T` is
touched last at launch, so the `0/T` → `30000/T` margin *is* the solve duration:

| case | margin (filesystem mtimes) | `wall_s` in `STATUS.<case>` | agreement |
|---|---:|---:|---|
| `P_q_c` | +63.410 s | 63 | < 1 s |
| `P_q_m` | +231.467 s | 231 | < 1 s |
| `P_q_f` | +1450.873 s | 1451 | < 1 s |
| `P_Ts_c` | +63.154 s | 63 | < 1 s |
| `P_Ts_m` | +228.757 s | 229 | < 1 s |
| `P_Ts_f` | +1413.070 s | 1413 | < 1 s |

The six margins come from filesystem mtimes; the six `wall_s` figures were
written by the launcher's own clock, **by a different mechanism, into a different
file**. Two unrelated instruments agree on six numbers to better than a second.
**A field inherited from an earlier run cannot produce that coincidence.**

Observed and reported rather than absorbed: each `30000/` directory holds `p`,
`phi` and `uniform` beside the registered four. These are solver-derived
write-time extras, **outside** the registered tuple, exactly as the registration
anticipated; no clause above depends on them.

**Every case wrote all sixteen registered writes** — `0`, then 2 000 through
30 000 at `writeInterval` 2 000 — so the pair C_PLATEAU needs (**28 000 and
30 000**) exists on all six. That is the whole point of the successor, and §7 is
where it is argued.

---

## 3. Gate (1) — the four controls, all inside their registered floors

`gate_t19b.json:35` records `gate1.ok = true`. Floors are read from T19's frozen
`controls` block; **the comparator defines none of them.**

| control | registered floor | worst measured over all six cases | margin |
|---|---|---|---|
| **C_PLATEAU** (`d_Nu`, `d_fRe` between the writes at 28 000 and 30 000) | **1e-06** | `d_Nu` **3.110e-12** (`Ts_f`); `d_fRe` **1.418e-13** (`Ts_c`/`q_c`) | ≳ 5 orders inside |
| **C_SYM** (mid-plane symmetry witness, full gap meshed) | **1e-06 K / 1e-09 m/s** | `T` **2.501e-12 K** (`q_f`); `U` **1.527e-16 m/s** (`Ts_f`/`q_f`) | ≳ 6 / 7 orders inside |
| **C_MASS** (bulk velocity at the station vs registered `U0`) | **1e-06** rel. | **4.626e-15** (`Ts_m`/`q_m`) | ≳ 8 orders inside |
| **C_ID** (`f·Re` from the `Ts` and `q` arms must agree; `beta = 0` makes them hydrodynamically identical) | **1e-06** rel. | **exactly 0.0** at all three levels | exact |

Worst final linear residual across all six cases: **9.978e-13** (`Ts_f`, field
`T`), at the solver tolerance. All six cases record `n_solves = 30000`.

**Rule 5's order (1) — "any level not iteratively converged or not plateaued →
NOT A RESULT" — did not fire on any row, and could not have been made not to
fire: it is evaluated from the frozen parent's floors before any value is
graded.**

---

## 4. THE THREE REFERENCES — where each one actually comes from

`analyse_t19b.py` does **not** take the reference from the registered JSON: it
derives it from the pinned `exact_t19.py` at full precision and refuses if the
derived value disagrees with the registered one beyond tolerance. The values in
`gate_t19b.json` are therefore the *derived* ones, and the registered JSON
carries the same numbers rounded to ten decimals.

`exact_t19.py` solves the parallel plate and the round pipe as **one**
one-dimensional problem with a geometry index `s` — `s` = 0 plates, `s` = 1 pipe,
`Dh = 4a/(1+s)` in both — **computes everything for general `s`, and then checks
at `s` = 1 against T1c's registered pipe numbers, which the module did not
compute.** *A route that cannot reproduce the pipe is not used for the plates.*
Measured at `s` = 1: `f·Re` **64.00000000** against T1c's 64; `Nu` uniform `q"`
**4.36363639** against 48/11; `Nu` uniform `T_s` **3.65679346** against
3.6567934.

| row | reference in `gate_t19b.json` | how it is obtained | is it a closed form? |
|---|---|---|---|
| **G1** | **96.0** exactly | closed form `f·Re = 32(s+3)/(1+s)` at `s` = 0, from `u = u_max(1 − ξ²)` with `u_max/ubar = (s+3)/2` and the force balance | **YES — exact and closed** |
| **G2** | **8.235294200908305** | **double quadrature** of the fully developed energy equation for uniform wall heat flux | **NO — a quadrature.** It is *cross-checked* against the closed form **140/17 = 8.235294117647059** and agrees to **1.0084e-08 relative** (8.3045e-12 absolute) |
| **G3** | **7.540700874069418** | **eigenvalue.** `(1/ξˢ)(ξˢψ′)′ + Λ(u/ubar)ψ = 0`, `ψ′(0) = 0`, `ψ(1) = 0`, discretised conservatively on cell centres, solved by inverse iteration with a tridiagonal Thomas solve (no third-party dependency), then **Richardson extrapolated over two ODE meshes**; the route is verified second order in its own ODE mesh (measured ratio **4.000** over M = 2000/4000/8000) | **NO — a numerically converged eigenvalue, not a closed form** |

> **⚠ A LOOSE CHARACTERISATION, CORRECTED AGAINST THE REGISTRATION RATHER THAN
> CARRIED FORWARD.** The commissioning brief for this record described all three
> references as *"exact analytic values"*, giving `Nu = 140/17` for the uniform
> heat flux row and `Nu ≈ 7.5407` for the uniform temperature row. **The
> registration is followed and the brief is recorded as loose on two of the
> three.** G1 is exact and closed. **G2's registered reference is the module's
> quadrature value 8.235294200908305, NOT 140/17** — 140/17 is an independent
> closed-form cross-check that the module meets to 1.0e-08 relative, and the
> difference is 5.3 orders below the row's own band, so nothing moves either way;
> the distinction is one of provenance, not of magnitude. **G3 has no closed form
> at all**: it is the first eigenvalue of a Sturm–Liouville problem, obtained
> numerically and Richardson-extrapolated. Calling it *analytic* overstates it.
> It is **EXACT-tier** in `T_FAMILY_INDEX.md` §1's sense — *"nothing has to be
> acquired and the reference cannot be wrong"* (`T19_PREREGISTRATION.md:38`–`:41`)
> — and that is a different claim from *closed form*.

**The NORMALISATION control on the referent.** A uniform scaling of the velocity
satisfies the ODE and the no-slip wall exactly and is invisible to both; it is
caught by requiring the bulk mean of `u/ubar` to be 1, and `exact_t19.py
--selftest` **REFUSES** a 1 % and a **1e-06** mutation. A first-order defect in
the `Nu_H` quadrature was found and fixed by driving this — the cumulative
trapezoid began from zero rather than from the integrand's value at `ξ` = 0 —
and the fix carries its measurement in a comment in the frozen file.

---

## 5. THE THREE GRADED ROWS — rule 5, verified from the values and not from the label

The triple is (c, m, f) at `ny` = 20/40/80, refinement ratio **`r` = 2 exact**,
`dim` = 2, **`Fs` = 1.25**, floors `STAGNANT_FLOOR` = 0.5 and `P_MIN` = 0.05
**imported by name** from `scripts/roache_triple.py` (`gate_t19b.json:28`–`:32`;
the comparator defines neither and refuses if the registered copy disagrees).

The artifact prints `triple_state` `"CONVERGING"` on all three rows. **That label
was not trusted.** The triples were re-analysed by this lane from
`gate_t19b.json`'s own `triple` blocks with an independent implementation of
`p = ln|d21/d32| / ln r` and `GCI = Fs·|(f−m)/f| / (r^p − 1)`.

| row | quantity | `c` | `m` | `f` |
|---|---|---:|---:|---:|
| **G1** | `f·Re`, from the **axial pressure gradient** between the two columns straddling the station (second order in `dy`) | 95.52238805969479 | 95.88014981272394 | **95.97000937207427** |
| **G2** | `Nu`, **uniform wall heat flux**, `q″Dh/(k(T_w − T_m))`, `T_w` reconstructed by the same discrete relation OpenFOAM uses (`T_w = T_cell + gradient·dy/2`), `T_m` the mass-flux-weighted bulk mean | 8.249616601410779 | 8.238914180475957 | **8.236201599861733** |
| **G3** | `Nu`, **uniform wall temperature**, `T_w` the imposed 400 K and `q″` reconstructed from the near-wall cell by the same discrete relation | 7.543378217000218 | 7.543245498691451 | **7.543209307508371** |

| row | `d21 = m−c` | `d32 = f−m` | `d21/d32` | strictly monotone? | `p` recomputed | `p` in artifact | Δ |
|---|---:|---:|---:|---|---:|---:|---:|
| **G1** | +3.577618e-01 | +8.985956e-02 | **3.981343** | **yes**, increasing | 1.9932552701411062 | 1.9932552701411062 | **0.000e+00** |
| **G2** | −1.070242e-02 | −2.712581e-03 | **3.945476** | **yes**, decreasing | 1.9801992592732367 | 1.9801992592732367 | **0.000e+00** |
| **G3** | −1.327183e-04 | −3.619118e-05 | **3.667145** | **yes**, decreasing | 1.8746572323358375 | 1.8746572323358375 | **0.000e+00** |

`d21` and `d32` carry the same sign on every row, so **no triple is
`OSCILLATORY`**; `|d21| > |d32|` on every row, so **none is `DIVERGENT`**;
`d21 ≠ 0`, so **none is `EXACT`**; and every `p` is far above both imported
floors (0.5 and 0.05), so **none is `STAGNANT`**. **The `CONVERGING` label is
earned by the values, not read off the artifact.**

The refinement ratios are the substance: **3.981 / 3.945 / 3.667** against the
theoretical **4.000** for a second-order scheme at `r` = 2.

| row | GCI recomputed at `Fs` = 1.25 | GCI in `gate_t19b.json` | Δ | `Fs` inverted out of the artifact's own `gci_pct` |
|---|---:|---:|---:|---:|
| **G1** | **0.039257873854382896 %** | 0.039257873854382896 % | 0.000e+00 | **1.2500000000** |
| **G2** | **0.013976880501152613 %** | 0.013976880501152611 % | 1.7e-18 | **1.2499999999999998** |
| **G3** | **0.00022485887874404060 %** | 0.00022485887874404062 % | −2.7e-20 | **1.2500000000000002** |

`Fs` = 1.25 is confirmed three independent ways: `factor_of_safety: 1.25` at
`gate_t19b.json:27`; `FS = 1.25` in `scripts/roache_triple.py`, imported by name
and not redefined; and — the strongest form — **inverting the artifact's own
published `gci_pct` for `Fs` returns 1.25 on each of the three rows.**
Monotonicity holds everywhere, so quoting a GCI is legitimate on all three (rule
5's last clause).

**THE FINE VALUE IS THE GRADED VALUE ON EVERY ROW.** The Richardson extrapolate
is carried under `richardson_REPORTED_ONLY` (96.00015000024814 /
8.235280668617376 / 7.543195738247674) and **no verdict is a function of it**.
This lane recomputed all three extrapolates independently and they reproduce
exactly; they are reported here only so that a reader can see they were not
graded.

---

## 6. THE BANDS — rebuilt from the frozen registration, not matched to the artifact

The failure mode that matters is a band that agrees with the artifact but not
with the frozen document, so the check ran in that direction. Registered relative
half-widths, from T19's own frozen `graded_rows.*.band_rel`: **±8.0e-04 (G1)**,
**±1.6e-03 (G2)**, **±3.5e-03 (G3)**.

| row | reference | band rebuilt as `ref × (1 ∓ band_rel)` | Δlo | Δhi | `value_fine` | inside? | half-band consumed |
|---|---:|---|---:|---:|---:|---|---:|
| **G1** | 96.0 | [95.9232, 96.07679999999999] | **0.000e+00** | **0.000e+00** | 95.97000937207427 | **yes** | **0.3905** |
| **G2** | 8.235294200908305 | [8.22211773018685, 8.248470671629759] | **0.000e+00** | **0.000e+00** | 8.236201599861733 | **yes** | **0.0689** |
| **G3** | 7.540700874069418 | [7.514308421010175, 7.567093327128661] | **0.000e+00** | **0.000e+00** | 7.543209307508371 | **yes** | **0.0950** |

**All six endpoints reproduce exactly from the frozen half-widths. Every value
sits inside less than half its registered allowance, and G2 and G3 inside a
tenth. No row is sitting on an edge.**

Relative deviations `(value_fine − reference)/reference`:

| row | measured | registered prediction | sign | magnitude |
|---|---:|---:|---|---|
| **G1** | **−3.124024e-04** | −3.12e-04 | correct | within 0.13 % of the prediction |
| **G2** | **+1.101842e-04** | +6.19e-04 | correct | **5.6× smaller** than predicted |
| **G3** | **+3.326526e-04** | +1.41e-03 | correct | **4.2× smaller** than predicted |

**BAND GROUND, RESTATED SO THE PASS CANNOT BE MISTAKEN FOR A LUCKY BAND.** The
three bands were armed from T1c's *measured* fine-level deviations on the same
three quantities, the same solver, the same `Re` and `Pr`, scaled by the
second-order factor `(51/40)² = 1.626`. **G3's band in particular is armed from a
failure, not a hope**: ±3.5e-03 is 2.5× the deviation T1c actually measured on
the one row it GATE FAILED. And the registration recorded, before compute, that
**every band is failed by the medium level** (predicted −1.25e-03 / +2.5e-03 /
+5.6e-03) and by the coarse level — **the bands discriminate the ladder rather
than accommodating it.**

---

## 7. WHY THE `PASS` IS LAWFUL — rule 5's order, walked in the only direction it runs

Rule 5 fixes the order and fixes its direction: **the gate can only turn a `PASS`
or `GATE FAIL` INTO `NOT A RESULT`, never the reverse.**

1. **Order (1) — any level not iteratively converged or not plateaued →
   `NOT A RESULT`.** `gate1.ok = true`; C_PLATEAU, C_SYM, C_MASS and C_ID are
   each five to eight orders inside their registered floors on every one of the
   six cases (§3). **The clause did not fire.**
2. **Order (2) — triple `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` →
   `NOT A RESULT`.** All three triples are **`CONVERGING` and strictly
   monotone**, with `|d21| > |d32|`, matching signs, `d21 ≠ 0` and `p` far above
   both floors — **re-derived from the values in §5, not read off the label.**
   **The clause did not fire.**
3. **Order (3) — `CONVERGING` → `PASS` inside the pre-registered band else
   `GATE FAIL`.** All three fine values lie inside, each consuming less than half
   its allowance (§6). **`PASS` ×3.**

**So the gate had no lever with which to manufacture this result.** Its only
power runs downward — toward `NOT A RESULT` — and the two clauses that exercise
that power were evaluated against floors defined in a file T19b cannot write, and
did not fire. **Combined with §1.1's sha256 pin (no gate, band, floor, threshold
or label could move without breaking the pin and stopping the comparator) and
§1.2's blindness (there was no answer to tune to), the `PASS` is a gate verdict
and not a chosen one.** Monotonicity holds on all three rows, so the GCIs quoted
in §5 are legitimate under rule 5's last clause.

---

## 8. THE SUPERSESSION — why T19b supersedes T19, and what T19's spend actually bought

`gate_t19b.json:3` carries `"supersedes": "T19"`. **The ground is a defect in
T19's own frozen builder, and it is a defect of REGISTRATION, not of physics.**

`verification/runs/T-family/T19_runs/build_t19.py:211` writes

    "    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }\n}\n"

into every emitted `system/fvSolution`, **alongside `stopAt endTime; endTime
30000;`** in the same registered case. Those two settings are mutually exclusive
with the registered completion rule:

- **A run that converges stops early**, so `last time == endTime` and
  `ExecutionTime count == endTime` **can never hold**;
- **a run that does not converge** satisfies the count and fails iterative
  convergence.

**No outcome could satisfy the rule.** Every T19 arm that ever ran converged
early and stopped: `P_Ts_c` at **541**, `P_q_c` at **828**, `P_Ts_m` at **1 929**,
`P_q_m` at **3 203**, `P_Ts_f` at **7 238**, `P_q_f` at **12 437** — every one of
them against a registered `endTime` of **30 000**, and **every one `rc = 0`,
`capped = no`, `note = clean`. They did not crash. They succeeded at the wrong
experiment.**

**AND `C_PLATEAU` — the rung's own load-bearing gate — WAS `UNEVALUABLE`, NOT
FAILED.** C_PLATEAU recomputes each graded quantity at the **previous** write
(28 000) and requires it to have moved no more than 1e-06 by the **last** write
(30 000). On T19 neither write exists on any arm. The gate T19's own registration
called *"the check that actually caught T1c's iteration-count defect"* had **no
pair to read**. A gate that has never once been computed is not yet known to be
alive.

**THE REPAIR IS TO THE CASE, NEVER TO A GATE.** `build_t19b.py` **deletes** the
`residualControl` line — not relaxes it, not makes it configurable; a tolerance
of 1e-30 or a switch would leave a lever that can be set wrong. The successor's
builder differs from its parent by **three removed lines and 42 added**, and *two
of the three removed lines are the file's own name*; the third is the defect.
Measured independently of the diff: both builders emit **72 files** with
**identical file lists**, **66 byte-identical**, and the six that differ are the
six `system/fvSolution` files, **each by exactly one deleted line with zero added
lines**. At module level, **18 module constants compared, 0 differ**, and an AST
comparison with docstrings and comments stripped shows both modules defining the
**same 18 functions** with **exactly two bodies differing** — `fv_solution` (the
repair) and `selftest` (the limb that checks the repair).

### 8.1 P0 — the ruling's own falsifiable test, and it HELD

`docs/DEAD_LEVER_AUDIT.md` §21.2 (verification's ruling, `998dc230`) diagnosed
the cause and authorised a case-level repair. **T19b carried that diagnosis
forward as a named prediction that could lose** (`T19b_PREREGISTRATION.md:465`–`:468`,
P0): *"With `residualControl` removed, both coarse cases reach `Time = 30000`,
write `28000/` and `30000/`, and C_PLATEAU evaluates. Can lose: if `P_q_c` still
stops early, verification's §21.2 diagnosis is wrong and this lane reports it as
wrong against that paragraph."*

**MEASURED: all six T19b cases reached `Time = 30000`, wrote all sixteen
registered writes including the 28 000/30 000 pair, and `C_PLATEAU` returned
`ok` on every one of them (§2, §3). P0 IS WON AND VERIFICATION'S §21.2 DIAGNOSIS
HELD** — reported as holding because it did, not as flattery.

### 8.2 The falsification specimen is PRESERVED

`verification/runs/T-family/T19_runs/P_q_c/` and `P_Ts_c/` hold `828/` and
`541/`. They are **preserved as evidence** — not cleaned, reused, rebuilt,
re-run, re-graded or deleted, by this document or under it. They are the only
artifacts on disk that demonstrate the defect. The successor's comparator
enforces this mechanically: its selftest runs under a filesystem watcher over
`T19_runs` permitting **only the two pinned parent instruments**, measured at
**0** other reads in both passes, with mutation control **M4** proving the
watcher fires when a limb does read `P_q_c/828/T`. **The specimen is measured
untouched, not asserted untouched.**

### 8.3 T19 IS NOT MOVED BY THIS RECORD

**T19's own verdict is not written here, not changed here, and not withdrawn
here.** T19 has no results record of its own; its six arms stand `NOT A RESULT`
on the board's reading, its frozen files are untouched, and `T_FAMILY_INDEX.md`
§5.4's criterion for that section — *"a pre-registration exists and no results
record does"* — is still met by T19 and so T19 stays where it is. **Supersession
is a statement about which rung carries the capability claim, not a re-grading of
the parent.**

---

## 9. THE PLANTED-ZERO CONTROLS — rule 3, two readers, both arms, seven-decade ladders

`gate_t19b.json:259`–`:296` carries a control on **both graded readers**. Neither
is unshown.

| reader | cells planted | plant | recovered | negative arm | demonstrated detection floor | status |
|---|---:|---:|---:|---:|---:|---|
| **`Nu_H`** — plant into `T`, the **single near-wall cell** of the downstream station column | **1** | 1.234e-03 | **2.0896870403710466e-03** | **exactly 0.0** | **1e-07** | **`PASS`** |
| **`fRe`** — plant into `p_rgh` across that column | **80** | 1.234e-03 | **2.808035555555485e+03** | **exactly 0.0** | **1e-07** | **`PASS`** |

**Both arms are present on each.** The negative arm requires **exactly 0.0** on
identical bytes — the comparator refuses a NOISY reader — and returned exactly
0.0 on both.

**The positive arm is a SEVEN-DECADE RECOVERY LADDER**, and both are visible at
every rung:

| plant | `Nu_H` recovered | `fRe` recovered |
|---:|---:|---:|
| 1 | 1.200012880451844 | 2.27555555555555e+06 |
| 0.1 | 0.1627272007255698 | 2.27555555555555e+05 |
| 0.01 | 0.01687337391376076 | 2.2755555555555504e+04 |
| **1.234e-03 (the registered plant)** | **2.0896870403710466e-03** | **2.8080355555555484e+03** |
| 1e-04 | 1.6942162635302793e-04 | 2.275555555555556e+02 |
| 1e-05 | 1.6942790443508216e-05 | 2.2755555555556540e+01 |
| 1e-06 | 1.6942852845147627e-06 | 2.2755555555578297 |
| **1e-07** | **1.6942851388535018e-07** | **0.22755555555617946** |

**The demonstrated detection floor is 1e-07 on both readers — four orders below
the registered plant.** Both ladders are monotone in the plant and both remain
plainly visible at the bottom rung, so neither zero anywhere in this rung is a
zero from a reader that has not been shown able to see a non-zero.

**THE `Nu` PLANT IS ONE CELL AND NOT THE WHOLE COLUMN, FOR A MEASURED REASON.**
`Nu` is built from `(T_wall − T_bulk)`, so a **uniform** plant across the station
column shifts the wall value and the bulk mean by the same amount and is
**invisible by construction** — driven, and it moved the read by **1.9e-13**,
i.e. round-off. The registration records that measurement and sizes the plant
accordingly.

**THE SIZING RULE IS RESTATED RATHER THAN INHERITED.** T14's rule *"the read must
move by at least 0.1 × the plant"* transfers only when the read carries the
plant's units. These readers return a Nusselt number and an `f·Re` while the
plant is a temperature or a kinematic pressure, so the transferable requirement —
and the one registered — is that **the registered plant must be VISIBLE (a
non-zero move) and the demonstrated detection floor must be at or below it.**
Both refusals are coded and both fire.

Containment is enforced in code: the control copies the case to `mkdtemp`,
**refuses if the copy resolves inside the case tree**, restores the original bytes
after every ladder rung, and never writes into the case.

---

## 10. THE PREDICTIONS — six registered before compute; four won, TWO LOST

The registration's own instruction is *"If a prediction loses it is reported as
wrong."* It is followed here.

| id | registered prediction | outcome | measured |
|---|---|---|---|
| **P0** | both coarse cases reach 30 000, write 28 000 and 30 000, C_PLATEAU evaluates | **WON** | all **six** did; C_PLATEAU `ok` ×6 (§8.1) |
| **P1** | G1, G2, G3 all `PASS` | **WON** | `PASS` ×3, every deviation with the predicted sign and inside its prediction's magnitude (§6) |
| **P2** | all three triples `CONVERGING` with `p` in **[1.6, 2.4]** | **WON** | `CONVERGING` ×3; `p` = 1.9933 / 1.9802 / 1.8747 — all inside |
| **P3** | C_ID better than **1e-12** — the arms should be bit-identical hydrodynamically | **WON, and more sharply than asked** | C_ID = **exactly 0.0** at all three levels |
| **P4** | wall-to-wall `Nu` asymmetry (REPORTED, never gated) below **1e-08** relative on every level | **WON** | 2.23e-13 / 2.93e-13 / 5.85e-13 |
| **P5** | the REPORTED first-order wall-shear route for `f·Re` misses 96 by roughly **1/(2·ny)** while the GRADED pressure route is second order | **⚠ LOST — on both limbs** | §10.1 |
| **P6** | each coarse case lands between **1.3 and 2.6** core-min | **⚠ LOST** | both coarse cases at **1.050** core-min — below the interval (§11) |

### 10.1 P5 LOSES, AND WHAT IT COSTS THIS RECORD IS STATED AGAINST ITS OWN INTEREST

`analyse_t19b.py:243`–`:252` computes a second `f·Re` route from the one-sided
wall shear, documented in the frozen source as *"the first-order wall-shear
route, carried beside the graded pressure route as a consistency diagnostic"*.
It is **REPORTED and never graded**. Measured, from `gate_t19b.json:254`–`:258`:

| level | `ny` | GRADED pressure route | REPORTED wall-shear route | \|diff\| | relative |
|---|---:|---:|---:|---:|---:|
| `c` | 20 | 95.52238805969479 | 95.52238805970151 | 6.72e-12 | **7.04e-14** |
| `m` | 40 | 95.88014981272394 | 95.88014981273281 | 8.87e-12 | **9.25e-14** |
| `f` | 80 | 95.97000937207427 | 95.97000937207360 | 6.68e-13 | **6.96e-15** |

| level | `ny` | wall-shear deviation from 96 | P5's predicted `1/(2·ny)` | measured / predicted |
|---|---:|---:|---:|---:|
| `c` | 20 | **−0.49751 %** | 2.5000 % | **0.199** |
| `m` | 40 | **−0.12484 %** | 1.2500 % | **0.0999** |
| `f` | 80 | **−0.03124 %** | 0.6250 % | **0.0500** |

**The REPORTED route's own observed order is `p` = 1.9932552703, against the
graded pressure route's 1.9932552701 — ten significant figures.** Its error ratio
from `c` to `f` is **15.93** against 4² = 16 for a second-order scheme over
`r` = 4. And the measured/predicted column **halves at each level**, which is
precisely the signature of a second-order error where a first-order one was
registered.

**So P5 loses on both of its limbs: the wall-shear route does not miss by
`1/(2·ny)`, and it is not first order — it is second order, and it is the same
number as the graded route to round-off.**

**MECHANISM — this lane's reading, `[DERIVED]`, not registered and not part of
any verdict.** For fully developed channel flow the streamwise momentum balance
ties the two routes algebraically: `(−dp/dx)·b = 2ν(du/dy)_w`. Substituting into
the pressure route's definition gives `f·Re = 16·b·(du/dy)_w/ubar`, and the
wall-shear route's `8·τ·Dh/ubar` with `Dh = 2b` gives **the same expression**.
A conservative finite-volume discretisation satisfies that balance *discretely*,
so the two routes are **not two independent estimates of different formal
order — they are one quantity reached two ways, and they carry the same error.**
The measured agreement to ≤9.3e-14 relative, and the identical observed order to
ten figures, are what that predicts.

> **CONSEQUENCE, RECORDED AGAINST THIS RECORD'S OWN INTEREST: the agreement of
> the REPORTED route with the GRADED route buys NO independent corroboration of
> G1.** It is a consistency check on the discrete momentum balance and on the
> reader's arithmetic, and nothing more. **Anyone who cites *"two independent
> routes agree"* as evidence for G1 is citing one route twice.** G1's evidence is
> its triple, its band, its planted-zero control and its `CONVERGING` state — not
> this diagnostic.
>
> **HONEST LIMIT ON THE MECHANISM ITSELF:** the algebra above is this lane's
> derivation from the continuous momentum balance and is *consistent with* the
> measurement to round-off. **It was not proved from the discretisation**, and it
> is offered as an explanation, not as a measurement. The measurement — the four
> figures in the two tables above — stands on its own and does not depend on the
> explanation being right.

---

## 11. COST — rule 12, actual against pre-registered

**Both calibration rows this rung owes already exist in `docs/COST_CALIBRATION.md`
and are cited, not duplicated:** `C-20260831T164745.937182Z-82edc690` (T19b stage
3) and `C-20260903T180449.568691Z-0097660a` (T19's four relaunched arms). A third
row, `C-20260831T164745.937132Z-3fc3bd39`, covers T19b stage 1.

### 11.1 T19b — the rung's own spend

Actuals are `core_min` read from each `STATUS.<case>`, basis **gross**.

| case | cells | actual core-min | POINT core-min | ratio | cap | cap used | `capped` |
|---|---:|---:|---:|---:|---:|---:|---|
| `P_q_c` | 2 400 | 1.050 | 2.952 | 0.3557 | 12 | 8.75 % | `no` |
| `P_Ts_c` | 2 400 | 1.050 | 2.952 | 0.3557 | 12 | 8.75 % | `no` |
| `P_q_m` | 9 600 | 3.850 | 12.624 | 0.3050 | 50 | 7.70 % | `no` |
| `P_Ts_m` | 9 600 | 3.817 | 12.624 | 0.3024 | 50 | 7.63 % | `no` |
| `P_q_f` | 38 400 | 24.183 | 77.952 | 0.3102 | 250 | **9.67 %** | `no` |
| `P_Ts_f` | 38 400 | 23.550 | 77.952 | 0.3021 | 250 | 9.42 % | `no` |
| **total** | | **57.500** | **187.056** | **0.3074** | **624** | 9.21 % | |

**RATIO actual/predicted = 0.3074 — a 3.25× OVER-prediction, in the conservative
direction, so no cap was ever at risk.** By case the ratio spans **0.302 to
0.356 across a 16× mesh range**, so the miss is a **systematic scale error, not
scatter**.

**ATTRIBUTION: MISPREDICTION. Not contention and NOT waste.** All six cases
completed, none was capped, none was re-run, none stalled — the longest single
case ran 1 451 wall s, well under charter §2's 3 600-s stall marker, so no row is
a stall. **Waste on T19b: 0.000 core-min.**

**The source of the miss is named rather than absorbed.** The registered POINT
rests on a rate **BORROWED** from T1c's four completed *pipe* runs — 2.46e-06 /
2.63e-06 / 4.06e-06 core-s per cell-iteration — and T19's registration disclosed
the borrow's risk in advance, though in the *opposite* direction (it predicted
under-prediction from a 1.47× mesh jump). T19b's own measured rates, re-derived
by this lane from `wall_s`, cells and 30 000 iterations, are **8.75e-07 /
8.02e-07 / 1.26e-06** — roughly a third of the borrowed values. **The
transferable finding: T1c's pipe rates do not transfer to a planar case of the
same solver and closure.**

Dollars **DERIVED, NOT MEASURED**, at the owner-stated **$0.0513/core-h**,
c7a.4xlarge, **REPORTED-BY-OWNER** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5): **actual $0.0492**, registered point **$0.1599**.

### 11.2 T19 — THE PARENT'S SPEND, AND ITS WASTE, NAMED SEPARATELY AND NEVER ABSORBED

**T19 total: 29.133 core-min**, summed by this lane from the six
`T19_runs/STATUS.P_*` files (0.033 + 0.050 + 0.517 + 0.683 + 12.033 + 15.817).

| component | core-min | dollars (DERIVED) | what it is |
|---|---:|---:|---|
| `P_Ts_c` + `P_q_c`, run 2026-08-30 | **0.083** | $0.0001 | **NOT waste.** The falsification specimen. These two runs are what exposed the unsatisfiable completion rule, and they are preserved on disk as the evidence for the ruling that authorised T19b (§8.2) |
| `P_Ts_m` + `P_q_m` + `P_Ts_f` + `P_q_f`, relaunched 2026-09-03 | **29.050** | **$0.0248** | **WASTE, ENTIRE, AND SEPARATELY NAMED** |
| **total** | **29.133** | **$0.0249** | |

> **THE 29.050 core-min IS WASTE AND IS STATED AS WASTE. IT IS NOT ABSORBED INTO
> ANY RATIO IN §11.1 AND MAY NOT BE.** The four medium and fine arms were
> relaunched from `verification/queue/heat-transfer/held/` on **2026-09-03,
> 17:27Z–17:46Z — three days after T19b had already superseded T19, graded all
> six of its own arms and closed at `PASS` ×3 on 2026-08-31T16:47Z.** They were
> spent against a completion rule no outcome could satisfy: all four converged
> early (1 929 / 3 203 / 7 238 / 12 437 against 30 000), all four returned
> `rc = 0` and `capped=no`, `mark_done_t19.py` returned rc = 1 on all four, and
> the frozen grader refused at exit 2. **No value, no triple, no observed order
> and no GCI came out of that 29.050 core-min, and none is quoted.**
>
> The already-filed row `C-20260903T180449.568691Z-0097660a` records the same
> finding and adds the honest normalisation: the four arms delivered **24 807 of
> 120 000 registered iterations = 20.67 %**, so **the estimate was not too high —
> the iteration count was truncated by the `residualControl` defect**, and the
> truncation must not be filed as estimator error.

**Combined spend on the T19 line, parent and successor: 86.633 core-min,
$0.0741 DERIVED** — of which **29.050 core-min ($0.0248) is named waste** and
**57.500 core-min ($0.0492) bought the verdict in this record.**

### 11.3 The cost channel as a detector

T19's registered POINT for `P_q_c` was 2.952 core-min against a measured 0.050 —
a ratio of **59.0×** — and `P_Ts_c` 2.952 against 0.033, **89.5×**. **Neither
ratio is an estimator error and neither may be filed as one.** The registration
priced a 30 000-iteration run and the cases stopped at 828 and 541; the iteration
ratios are 36.2× and 55.5× — same direction, same order, same two cases. **The
cost channel detected the truncation before anybody read a field.** A calibration
row recording 59.0× as "estimator error" would have buried the finding in the
ledger.

---

## 12. WHAT THIS DOCUMENT DID NOT VERIFY — stated, not glossed

- **This record did not re-run the comparator and did not re-grade anything.**
  Every value in §5, §6, §9 and §10.1 is read from `gate_t19b.json`, and every
  recomputation (`p`, GCI, Richardson, the band endpoints, the deviations, the
  wall-shear order) was performed on the artifact's own published triples by an
  independent implementation. **Agreement between the artifact and a
  recomputation from the artifact's own numbers is an arithmetic check, not a
  reproduction of the grade from the fields.**
- **The fields at `endTime` were not re-read and the readers were not re-driven.**
  §2's completion clauses were re-derived from `log.solve`, `system/controlDict`,
  the time directories and mtimes; the graded *values* were not recomputed from
  `30000/T` and `30000/U`.
- **The comparator selftest and the six mutation controls were not re-run by this
  lane.** Their results in §7 of the registration are cited as recorded there and
  as re-affirmed by the closing commit; re-running them would produce further
  side-effect artifacts.
- **`build_t19b.py`'s meshes were not re-derived.** `constant/polyMesh` stays out
  of git by design; mesh quality rests on the committed `log.checkMesh.build`
  and `BUILD.txt`, which this document did not re-read.
- **The supervisor's §3 check 1 (the successor instruments read as diffs) is
  cited, not discharged here.** This document hashed the instruments against
  their frozen blobs — **that is an identity check, not a diff read.**
- **The `CANNOT SEE` blind spot registered at `T19b_PREREGISTRATION.md:531`–`:539`
  is carried forward unrepaired and is re-stated here as due for re-read**: the
  S8b/S8c watcher covers seven call routes and does **not** cover `os.stat`,
  `os.path.getsize`, `os.walk`'s stat calls, `pathlib` or `subprocess`. Mutation
  control **M6** exploits that gap deliberately and is caught by **S8a** instead,
  which is why both detector families are registered rather than one. OWNER:
  heat-transfer.
- **P5's mechanism (§10.1) is this lane's derivation and was not proved from the
  discretisation.** The measurement stands without it.
- **Nothing was sent, filed, uploaded, registered or posted. SUBMISSIONS REMAIN
  PARKED** (`CLAUDE.md` rule 7).

---

## 13. Artifacts

| what | path |
|---|---|
| Pre-registration (frozen `b52ed93b`) | `docs/campaigns/T-family/T19b_PREREGISTRATION.md` |
| **Gate artifact — the registered grade** | `verification/runs/T-family/T19b_runs/gate_t19b.json` |
| Comparator (frozen) | `verification/runs/T-family/T19b_runs/analyse_t19b.py` |
| Builder (frozen) | `verification/runs/T-family/T19b_runs/build_t19b.py` |
| Mutation controls | `verification/runs/T-family/T19b_runs/mutation_controls_t19b.py` |
| Instrument diffs against the parent | `verification/runs/T-family/T19b_runs/T19b_INSTRUMENT_DIFFS.txt` |
| **Pinned parent registration (gates, bands, floors, caps)** | `verification/runs/T-family/T19_runs/T19_registered.json` |
| **Pinned parent referent** | `verification/runs/T-family/T19_runs/exact_t19.py` |
| Completion marker / launcher, REUSED UNEDITED | `verification/runs/T-family/T19_runs/mark_done_t19.py`, `run_one_t19.sh` |
| Per-case completion and cost records | `verification/runs/T-family/T19b_runs/STATUS.P_{q,Ts}_{c,m,f}` |
| Completion markers | `verification/runs/T-family/T19b_runs/DONE.P_{q,Ts}_{c,m,f}` |
| Run trees | `verification/runs/T-family/T19b_runs/P_{q,Ts}_{c,m,f}/` |
| **The falsification specimen — PRESERVED, do not clean** | `verification/runs/T-family/T19_runs/P_q_c/828/`, `.../P_Ts_c/541/` |
| Governing ruling | `docs/DEAD_LEVER_AUDIT.md` §21.1–§21.2 (`998dc230`) |
| Calibration rows (T19b stage 1 / stage 3 / T19 waste) | `docs/COST_CALIBRATION.md`, rows `C-20260831T164745.937132Z-3fc3bd39`, `C-20260831T164745.937182Z-82edc690`, `C-20260903T180449.568691Z-0097660a` |
