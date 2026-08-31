# VMFL029 IS DECLINED — not registered, not run as a graded case

**Ruled by `ansys-verification-supervisor`, 2026-08-31.** VMFL029 (Anisotropic Conduction Heat Transfer, VM2026R1 **p. 109**) was this team's sole remaining candidate for a clean `PASS` under the exact-PDE rule. **It is declined.** Three grounds, each independently sufficient, each measured rather than argued.

## 1. The gate cannot reach asymptotic range at any affordable cost

`p_obs` = **0.62** at 160/320/640 and **0.69** at 320/640/1280 against a formal order of 2, with pointwise Cauchy orders repeatedly **negative** (−1.31 at y = 0.200, −0.95 at y = 0.800). A declared triple returns **`OSCILLATORY` → `NOT A RESULT`** under CLAUDE.md rule 5 step 2. Asymptotic range needs **~3015 cells/side**; a triple sitting inside it costs **≈6.3e+05 core-min = 10,500 core-hours ≈ $538.65 DERIVED** at the owner-stated $0.0513/core-h — **21.5× the $25/run pre-authorisation**, for one row.

*Provenance:* orders above N=160 are from the lane's independent Python instruments; `solidFoam` was **not** run beyond N=160 and no order is claimed as measured from the production solver there.

## 2. §12.2 answers **DIFFERENT**, so `PASS` was never available

The solver discretises `div(K grad T) = 0` with a **constant SPD** `K`. The only closed form is the exact solution of the **rank-one, non-elliptic** `∂²T/∂s² = 0`. **Ellipticity is not a small parameter**: the two differ by up to **2.07e-01 K** on the gate profile itself. Under the exact-PDE rule (`VERIFICATION_CHARTER` §2h.6.1, v1.27) a reference that is exact for a *different* model **caps at `GATE REACHED`** however clean the algebra. §2h.4's five conditions are therefore not declared — they are the conditions for seeking `PASS`.

The recovered tensor is why. `VMFL029_aniso.cas:2628` gives `(matrix 0.25 −0.433 0 / −0.433 0.75 0 / 0 0 1)`; **I computed its eigenvalues: 1.1000121e-05 and 0.999989, condition number 9.09e+04.** Those digits are a four-place truncation of an *exactly* singular matrix — with 1/4, −√3/4, 3/4 the eigenvalues are [2.8e-17, 1.0]. **The only thing making the archive's tensor non-singular is the rounding of √3/4 to 0.433.** The archive also **contradicts itself**: its orthotropic block names the near-zero direction as (0,1,0) while the matrix's zero eigenvector lies at −150°, along (0.866, 0.5).

## 3. The feasibility work spent the registration, and this is the one that generalises

Establishing whether the gate was *gradeable at all* required computing candidate gate quantities — the conservation-identity test could not be answered any other way. **The measurement therefore contaminated the band.** Rule 2 makes the freeze's entire evidentiary content the claim that the gate could not have been fitted to the answer, and no VMFL029 document written after those runs can make that claim. **The lane wrote no band at all and disclosed this against its own work; that was correct.**

> **THE GENERAL LESSON, and it is a real tension rather than a mistake:** where a gate quantity's *viability* is itself in question, feasibility and registration pull against each other — you cannot show the gate is gradeable without computing it, and computing it forfeits prediction-first on any band chosen afterwards. **The escape is a band fixed by an a-priori argument before any field exists**, as VMFL038-R2's 2 % was, or as its limb-B 0.5 % was — set by what a *known past defect* does to it, not by what the run did.

## What is NOT owed

**No register row.** The run root `verification/runs/ansys_verification/VMFL029/` does not exist; nothing was graded, so there is no verdict and none is invented. Feasibility spend **≈0.7 core-min MEASURED** (~$0.0006 DERIVED). Both artifacts are committed and both say **NOT THE FREEZE COMMIT** in their first line: `49d95bbf` (analytical reference module), `0025400c` (pre-registration draft, no band).

## What was gained, and it is not nothing

- **`solidFoam` + `constAnIso` genuinely does anisotropic conduction, proved by manufactured solution rather than by reading a dictionary:** two 60×60 runs differing *only* in the `coordinateSystem` rotation gave max errors **2.604e-05 K** (rotated) vs **1.067e-01 K** (unrotated) — **4,100×** — so heat flows at an angle to the gradient at the right magnitude and sign. A general SPD tensor is representable because `constAnIso` + `coordinateSystem` *is* the eigendecomposition `R diag(k) Rᵀ`. A rank-one projection is not, and could not be by any elliptic solver.
- **The conservation-identity check fired again, and it was right to demand it.** NET wall heat flux is pinned to the solver floor on every mesh — `|NET|/scale` = 6.48e-13 / 2.61e-12 / 1.04e-11 at N = 40/80/160 — **carrying zero mesh information, exactly the VMFL038 `τ_w` shape.** Single-wall flux refines at `p_obs` 1.02; T at x = 0.5 refines at 0.93. **That is twice in one day that a gate quantity was pinned by conservation, and it is now a standing pre-freeze check for this team.**

## Scope ruling on the constructive alternative

The draft's §11 proposes a **well-conditioned SPD tensor** whose exact solution *is* of the same PDE — genuinely `SAME` and genuinely `PASS`-capable. **That is good verification work and it is NOT this team's mandate.** Our charter is the Ansys manual's cases; a manufactured-solution case of our own design produces no Ansys-manual credential. **Referred to `verification`, not absorbed here.** And if it is ever built, it must be frozen **before any compute** — today's runs cannot serve as its feasibility, for exactly the rule-2 reason above.

## Open, and stated rather than filled in

Which tensor the case actually is (the archive contradicts itself and the manual prints nothing); what model Ansys called "the analytical solution". **One cheap lead:** the manual lists **`3d.csv`** among `VMFLGPU004`'s inputs (p. 233) — the same physics on the GPU solver. If it carries the curve plotted in Figure .29.2 it settles the §12.2 classification. **It could never be a gate value.**
