# T8 re-registration — **DRAFT. NOT A REGISTRATION. NOT FROZEN. NOTHING HERE BINDS.**

**STATUS: DRAFT ONLY.** This file registers nothing, freezes nothing, gates
nothing and authorises no compute. It is the material a re-registration would
need, written so that the decision can be taken on evidence — **the decision
itself is Sanaa's and the chief's.** Re-registering a rung after first compute
is not a supervisor's call and is emphatically not a lane's.

**No rung id is claimed here.** Whoever authorises this assigns it. "T8-next"
below is a placeholder, not a name.

**Nothing in this file has been sent, filed, submitted, uploaded, registered or
posted outside this box (`CLAUDE.md` rule 7).**

---

## 1. Why the frozen T8 is dead, on two independent grounds

**Ground 1 — the extrapolation precondition is false.** §12 S3 registers the
axis extrapolation `(9f₁ − f₂)/8`, whose precondition is `r₂ = 3·r₁`.
Measured on the real, completed level-c mesh, with geometry written by
OpenFOAM: **`r₂/r₁ = 2.333313`**, against the exact wedge-centroid value
`7/3 = 2.333333`. `resolve_planes` refuses. **No T8 row can be graded.**

**Ground 2 — the ladder never had a gradeable triple anyway.** `CLAUDE.md`
rule 5 order (1) fires before any triple is classified: level `c` finished at
`endTime` with a `T` initial residual of **7.32e-04**, four decades above the
registered `1e-6`, and level `m` **crashed** and wrote no fields. Even with
correct weights, every row was **`NOT A RESULT`**.

**These are separate findings and both belong on the record.** Fixing only the
first would produce a comparator that runs and still cannot grade.

## 2. THE INSTRUMENT CHANGE — weights computed from cell centres READ FROM DISK

**The rule this encodes: do not assert what the mesh does. Measure it.**

Registering `7/3` in place of `3` would repeat the identical mistake one step
smaller — a hard-coded constant asserting a geometric fact about a mesh the
code has not looked at. **That is exactly what just failed.**

For a field quadratic in `r`, `f(r) = a + b·r²`, sampled at the two
axis-adjacent cell centres with `k = r₂/r₁`:

```
a = w1*f1 + w2*f2,    w1 = k**2/(k**2 - 1),    w2 = -1.0/(k**2 - 1)
```

**Proposed instrument:**

- read `r₁` and `r₂` from the `Cx`/`Cy` OpenFOAM wrote at `endTime`, per plane;
- **assert `r₂ > r₁ > 0`** — a structural fact — and **never assert a ratio**;
- compute `k`, `w1`, `w2` from those radii;
- refuse if `k` is not consistent across planes to a registered tolerance
  (a uniform-`dr` first block implies one `k` for every plane; a departure means
  the mesh is not the registered one).

This is immune, **in one stroke**, to wedge-versus-arithmetic centroids, to a
changed `nz`, to radial grading, and to the flat-sided wedge correction — the
last of which **never needs answering, because a measured centroid already
contains it.**

**Sanity of the magnitude, so nobody thinks this is chasing noise.** The
flat-sided correction is `k_measured = 2.333313` against `k_exact = 7/3`;
`Δw₁ = 4.73e-06`, which on a 20 K field difference is **9.5e-05 K** — utterly
negligible against ±0.05 bands. **This change is not about numerical necessity.
It is about deleting an assumption class.**

## 3. THE FIXTURE CHANGE — a fixture that can only produce the ratio the code assumes is not a control

The amendment-A1 fixture `make_synthetic_field_case` places cell centres at
`(j+½)·dr`, which makes `r₂ = 3r₁` **true by construction**. The fixture and
the instrument agreed **because they shared one wrong assumption** — the L-321
shape. 69 selftest checks passed and **not one could have caught this.**

**Proposed:**

- the fixture places cell centres at **annular centroids**,
  `r̄ = (2/3)(r_b³ − r_a³)/(r_b² − r_a²)`, so it reproduces `7/3` naturally
  rather than being told to;
- **a selftest arm at a THIRD ratio** — neither `3` nor `7/3`, e.g. a graded
  radial block giving `k ≈ 1.9` — on which the disk-read weights must still
  recover the analytic axis value exactly;
- the existing planted-zero arms re-derived from the **computed** `w1`, `w2`:
  a both-column plant shifts the axis value by `(w1 + w2)·PLANT` and an
  innermost-only plant by `w1·PLANT`, **for any `k`**. Note that
  `w1 + w2 = 1` identically, so **the both-column arm returns `PLANT` at every
  ratio and is therefore blind to a weight error at every ratio** — the finding
  from amendment A1.3, now general rather than specific to `(7f₁−f₂)/6`.
  **The innermost-only arm is the load-bearing one and must be registered as
  such, not left supplementary.**

## 4. What is NOT yet decided, and must be before anything is frozen

**These are open questions, not proposals. A lane does not settle them.**

1. **The `epsilon` divergence.** Setup is byte-identical across levels
   (measured — §5 below), so this is numerical, not a case error. Whether the
   answer is a relaxation ramp, a `limitT`/bounded-`epsilon` fvOption, a
   different initial `epsilon`, or `kOmegaSST` instead, is a **modelling
   decision with a registered prediction attached** (§9 P1 of the dead document
   made `kEpsilon` a testable claim). Changing the closure changes what the
   rung tests.
2. **`endTime` and the convergence criterion.** `c` ran 8000 steps and was four
   decades from `1e-6`. The registered `endTime` values were **not sufficient
   for the registered tolerance**, and re-registering them unchanged would
   re-run into the same wall.
3. **Whether any existing solve can be reused.** Under rule 2 a re-registration
   is **fresh**; the completed `c` fields and whatever `f` produces are
   **evidence about the case**, not gradeable data for a new registration.
4. **The cost calibration** owed for the dead rung is owed regardless
   (`CLAUDE.md` rule 12) and belongs in `docs/COST_CALIBRATION.md`.

## 5. The measurement that refutes the level-specific-setup hypothesis

Reported in full at §APPENDIX 3 of `T8_LANE_STATUS_2026-08-25.md`. In short:
**every field in `0.orig/`, every file in `constant/`, `fvSchemes` and
`fvSolution` are BYTE-IDENTICAL across `c`, `m` and `f`**; `controlDict`
differs **only** in `endTime` and `writeInterval`; and the three
`blockMeshDict`s are **byte-identical once the hex division counts are
normalised** (same md5). **There is no level-specific initialisation or
boundary difference in `m`.** The defect class the builder audit showed to be
invisible (B7–B11) is **refuted as the cause here** — it remains a real blind
spot in the instruments, but it is not what happened to `m`.

## 6. A control the dead document did not have, and should

The builder audit found **five surviving mutations** — `R_STATIONS` on one
level, source `w0`, source `dT0`, outlet patch type, outlet `U` BC — because
**every structural instrument is geometric or bookkeeping and none reads back
what was initialised or what the boundaries do.**

`CASE.txt` already carries `w0`, `dT0`, `T_source`, `F0`, `k0`, `epsilon0` and
`Prt`. **A re-registration should register a control that reads the `0/` fields
and the boundary types back off disk and checks them against those constants**,
and refuses on disagreement. That closes four of the five survivors and costs
no compute.

## 7. Cost

No compute is proposed by this file. Any re-registration carries its own
`cost_basis` in core-minutes per `CLAUDE.md` rule 12, and the dead rung's
estimate-versus-actual — level `c` came in at **3.817 core-min against 7.13
predicted, ratio 0.54** — is a calibration datum the new estimate should use
instead of the cross-mode PIMPLE rate that over-predicted it.

---

**DRAFT. NOT A REGISTRATION. NOT FROZEN. Authorisation is Sanaa's and the
chief's.**
