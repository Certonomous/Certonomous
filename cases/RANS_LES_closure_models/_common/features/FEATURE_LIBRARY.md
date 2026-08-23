# FS1 maximal feature library

**Generated** by `make_feature_library.py`. Built by `build_features.py`; audited by
`fs2_audit.py`; invariance measured by `invariance_check.py`. **Start maximal, select
nothing** - no feature here has been chosen or discarded on any performance grounds.

**110 features** on **40 benchmark cases** (641,652 cells). One `.npz` per case in
`/home/ubuntu/closure-data/features/` (outside the repo), plus `manifest.json`.

## Blocks

| block | count | what | source |
|---|---|---|---|
| **A** | 47 | minimal integrity basis of `{S, Omega, A_p, A_k}`, normalisation **A** | Wu, Xiao & Paterson 2018, Table B.4, arXiv:1801.02762v4 preprint, caption **p. 36** (Appendix B opens p. 35); mapping `A = -I x v` their Eq. (B.1a,b) **p. 35** |
| **B** | 47 | the same 47 invariants, normalisation **B** | normalisation VARIANT, not new physics |
| **C** | 11 | scalar flow markers `q1..q11` | Wu Table 2 **p. 10** (q1-q3); Kaandorp & Dwight 2020 Table 1 **p. 25** (q4-q6, q8, q9); Wang, Wu & Xiao 2017 Table 1 **p. 10** (q10); q7/q11: Ling & Templeton 2015, **NOT ON DISK** (PENDING-MIT) |
| **D** | 5 | Pope's five invariants of `(s, r)` | Pope 1975, JFM 72(2), **p. 335** |

## Normalisation, and the two variants

Raw tensors are normalised by Wu et al.'s bounded scheme (their Eq. 8, **p. 9**), which
keeps every normalised component in `[-1, 1]`:

```
alpha_hat = alpha / (|alpha| + |beta|)
```

with `beta` from their Table 1 (**p. 9**): `eps/k` for `S`, `||Omega||` for `Omega`,
`rho |DU/Dt|` for `grad p`, `eps/sqrt(k)` for `grad k`.

| variant | time scale used for `S` | carries `nu`? |
|---|---|---|
| **A** | `beta = eps/k`, i.e. `T = k/eps` | no |
| **B** | `T = max(k/eps, 6 sqrt(nu/eps))` (Durbin bound) | **yes** |

> **Reynolds-similarity note, required by lesson L-184/D2.** Variant **B** contains the
> molecular viscosity through the Durbin bound. A normaliser carrying `nu` is **not**
> Reynolds-similar: two geometrically identical flows at different `Re` do not map onto the
> same normalised feature value. Variant B may therefore not be transferred across a
> Reynolds-number change without an explicit note, and any model selecting B features must
> report that it has done so. Variant A carries no `nu` and is Reynolds-similar. Both are
> shipped precisely so the choice is visible and testable rather than buried.

Block D also uses the Durbin-bounded scale and is **unbounded** - `|lam3|` reaches 1.5e11
and `|lam5|` 1.5e14 on this data. That is recorded in `FS2_DEGENERACY_REPORT.md` sec. 5;
it makes block D dominant in any unstandardised distance metric.

## Wall distance: recomputed, and validated

`q1_wallRe` needs a wall distance. The 29 parametric hills and the NASA hump ship
`walldist`; the ducts, `PHLL10595` and `CBFS13700` do not. `wall_distance.py` recomputes it
for every case as the nearest distance from each cell centre to any face centre on a patch
of type `wall`, read from `constant/polyMesh`.

**Validated against a shipped field** on `alpha_05_4071_2024` (a hill that ships `walldist`):
**median relative difference 1.1e-14**, **p95 3.1e-3**, **relative L2 2.2e-3**. It is exact in
the median and departs only in the near-wall cells where a face-centre distance is a lower
bound on the true normal distance. `q1` saturates at 2, which bounds the consequence.

## Invariance, measured not asserted

Charter section 6 check on `CBFS13700`: Galilean boost and rigid rotation applied to the
raw fields, all features and normalisers recomputed. Tolerance `1e-12`.

* **Rotation invariant: all 110** (max relative change 6.9e-06, and the three above tolerance are roundoff on algebraically-zero features - see the report).
* **NOT Galilean invariant: 58 of 110.** Every one either contains `A_p` (whose normaliser `|DU/Dt|` reduces to `|U.grad U|` in a steady solve, which shifts under a boost) or uses the raw velocity `U`.

This independently reproduces Kaandorp & Dwight's own annotation: *"Features marked with
dagger are rotationally invariant but not Galilean invariant"* (Table 1 footnote, **p. 25**).
Their table daggers **four** rows - `q2`, `q4`, `q8`, `q9` in this library's numbering
(`q10` is not in their table; it is Wang, Wu & Xiao 2017's streamline curvature) - and the
measurement here flags all four, plus `q10`, as the five raw-velocity scalar markers.
(Dagger count read from a two-column pdftotext extraction of p. 25; a marker lost by the
extractor would not be visible. Corrected from an earlier five-dagger claim, 2026-08-23;
`CLOSURE_MODELLING_CHARTER.md` sec. 6 agrees on four.)

## Every feature

`G` = Galilean invariant, `R` = rotation invariant, `dead` = algebraically zero on all
pooled data (`max|v| < 1e-12`).

| # | feature | definition | normaliser | G | R | dead | source |
|---|---|---|---|---|---|---|---|
| 1 | `I1_trS2__A` | `I1_trS2` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 2 | `I2_trS3__A` | `I2_trS3` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 3 | `I3_trW2__A` | `I3_trW2` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 4 | `I4_trP2__A` | `I4_trP2` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 5 | `I5_trK2__A` | `I5_trK2` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 6 | `trW2S__A` | `tr(W2S)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 7 | `trW2S2__A` | `tr(W2S2)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 8 | `trW2SWS2__A` | `tr(W2SWS2)` | variant **A** | yes | no | **DEAD** | Wu Table B.4 p. 36 |
| 9 | `trP2S__A` | `tr(P2S)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 10 | `trP2S2__A` | `tr(P2S2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 11 | `trP2SPS2__A` | `tr(P2SPS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 12 | `trK2S__A` | `tr(K2S)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 13 | `trK2S2__A` | `tr(K2S2)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 14 | `trK2SKS2__A` | `tr(K2SKS2)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 15 | `trWP__A` | `tr(WP)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 16 | `trPK__A` | `tr(PK)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 17 | `trWK__A` | `tr(WK)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 18 | `trWPS__A` | `tr(WPS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 19 | `trWPS2__A` | `tr(WPS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 20 | `trW2PS__A` | `tr(W2PS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 21 | `trP2WS__A` | `tr(P2WS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 22 | `trW2PS2__A` | `tr(W2PS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 23 | `trP2WS2__A` | `tr(P2WS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 24 | `trW2SPS2__A` | `tr(W2SPS2)` | variant **A** | yes | yes | **DEAD** | Wu Table B.4 p. 36 |
| 25 | `trP2SWS2__A` | `tr(P2SWS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 26 | `trWKS__A` | `tr(WKS)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 27 | `trWKS2__A` | `tr(WKS2)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 28 | `trW2KS__A` | `tr(W2KS)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 29 | `trK2WS__A` | `tr(K2WS)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 30 | `trW2KS2__A` | `tr(W2KS2)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 31 | `trK2WS2__A` | `tr(K2WS2)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 32 | `trW2SKS2__A` | `tr(W2SKS2)` | variant **A** | yes | yes | **DEAD** | Wu Table B.4 p. 36 |
| 33 | `trK2SWS2__A` | `tr(K2SWS2)` | variant **A** | yes | yes |  | Wu Table B.4 p. 36 |
| 34 | `trPKS__A` | `tr(PKS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 35 | `trPKS2__A` | `tr(PKS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 36 | `trP2KS__A` | `tr(P2KS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 37 | `trK2PS__A` | `tr(K2PS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 38 | `trP2KS2__A` | `tr(P2KS2)` | variant **A** | no | yes | **DEAD** | Wu Table B.4 p. 36 |
| 39 | `trK2PS2__A` | `tr(K2PS2)` | variant **A** | no | yes | **DEAD** | Wu Table B.4 p. 36 |
| 40 | `trP2SKS2__A` | `tr(P2SKS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 41 | `trK2SPS2__A` | `tr(K2SPS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 42 | `trWPK__A` | `tr(WPK)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 43 | `trWPKS__A` | `tr(WPKS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 44 | `trWKPS__A` | `tr(WKPS)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 45 | `trWPKS2__A` | `tr(WPKS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 46 | `trWKPS2__A` | `tr(WKPS2)` | variant **A** | no | yes |  | Wu Table B.4 p. 36 |
| 47 | `trWPSKS2__A` | `tr(WPSKS2)` | variant **A** | yes | yes | **DEAD** | Wu Table B.4 p. 36 |
| 48 | `I1_trS2__B` | `I1_trS2` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 49 | `I2_trS3__B` | `I2_trS3` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 50 | `I3_trW2__B` | `I3_trW2` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 51 | `I4_trP2__B` | `I4_trP2` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 52 | `I5_trK2__B` | `I5_trK2` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 53 | `trW2S__B` | `tr(W2S)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 54 | `trW2S2__B` | `tr(W2S2)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 55 | `trW2SWS2__B` | `tr(W2SWS2)` | variant **B** | yes | no | **DEAD** | Wu Table B.4 p. 36 |
| 56 | `trP2S__B` | `tr(P2S)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 57 | `trP2S2__B` | `tr(P2S2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 58 | `trP2SPS2__B` | `tr(P2SPS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 59 | `trK2S__B` | `tr(K2S)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 60 | `trK2S2__B` | `tr(K2S2)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 61 | `trK2SKS2__B` | `tr(K2SKS2)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 62 | `trWP__B` | `tr(WP)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 63 | `trPK__B` | `tr(PK)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 64 | `trWK__B` | `tr(WK)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 65 | `trWPS__B` | `tr(WPS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 66 | `trWPS2__B` | `tr(WPS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 67 | `trW2PS__B` | `tr(W2PS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 68 | `trP2WS__B` | `tr(P2WS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 69 | `trW2PS2__B` | `tr(W2PS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 70 | `trP2WS2__B` | `tr(P2WS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 71 | `trW2SPS2__B` | `tr(W2SPS2)` | variant **B** | yes | yes | **DEAD** | Wu Table B.4 p. 36 |
| 72 | `trP2SWS2__B` | `tr(P2SWS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 73 | `trWKS__B` | `tr(WKS)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 74 | `trWKS2__B` | `tr(WKS2)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 75 | `trW2KS__B` | `tr(W2KS)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 76 | `trK2WS__B` | `tr(K2WS)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 77 | `trW2KS2__B` | `tr(W2KS2)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 78 | `trK2WS2__B` | `tr(K2WS2)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 79 | `trW2SKS2__B` | `tr(W2SKS2)` | variant **B** | yes | yes | **DEAD** | Wu Table B.4 p. 36 |
| 80 | `trK2SWS2__B` | `tr(K2SWS2)` | variant **B** | yes | yes |  | Wu Table B.4 p. 36 |
| 81 | `trPKS__B` | `tr(PKS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 82 | `trPKS2__B` | `tr(PKS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 83 | `trP2KS__B` | `tr(P2KS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 84 | `trK2PS__B` | `tr(K2PS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 85 | `trP2KS2__B` | `tr(P2KS2)` | variant **B** | no | yes | **DEAD** | Wu Table B.4 p. 36 |
| 86 | `trK2PS2__B` | `tr(K2PS2)` | variant **B** | no | yes | **DEAD** | Wu Table B.4 p. 36 |
| 87 | `trP2SKS2__B` | `tr(P2SKS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 88 | `trK2SPS2__B` | `tr(K2SPS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 89 | `trWPK__B` | `tr(WPK)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 90 | `trWPKS__B` | `tr(WPKS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 91 | `trWKPS__B` | `tr(WKPS)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 92 | `trWPKS2__B` | `tr(WPKS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 93 | `trWKPS2__B` | `tr(WKPS2)` | variant **B** | no | yes |  | Wu Table B.4 p. 36 |
| 94 | `trWPSKS2__B` | `tr(WPSKS2)` | variant **B** | no | yes | **DEAD** | Wu Table B.4 p. 36 |
| 95 | `q1_wallRe` | wall-distance Reynolds number: `min(sqrt(k) d / (50 nu), 2)` | none (already dimensionless) | yes | yes |  | Wu Table 2 p. 10 / Kaandorp Table 1 p. 25 |
| 96 | `q2_turbIntensity` | turbulence intensity: `k / (k + 0.5 U.U)` | 0.5 U.U | no | yes |  | Wu Table 2 p. 10 / Kaandorp Table 1 p. 25 (dagger) |
| 97 | `q3_timeScaleRatio` | turbulent : mean-strain time scale: `(k/eps) / (k/eps + 1/||S||)` | 1/||S|| | yes | yes |  | Wu Table 2 p. 10 |
| 98 | `q4_pgradAlongStreamline` | pressure gradient along streamline: `U.grad p / (|U.grad p| + |U||grad p|)` | |U||grad p| | no | yes |  | Kaandorp Table 1 p. 25 (dagger) |
| 99 | `q5_excessRotation` | excess rotation rate: `(||W||-||S||)/(||W||+||S||)` | ||W||+||S|| | yes | yes |  | Kaandorp Table 1 p. 25 |
| 100 | `q6_stressRatio` | total : normal Reynolds stress: `||tau|| / (||tau|| + k)` | k | yes | yes |  | Kaandorp Table 1 p. 25 |
| 101 | `q7_viscRatio` | eddy : molecular viscosity ratio: `nu_t / (nu_t + 100 nu)` | 100 nu | yes | yes |  | Ling & Templeton 2015 (NOT ON DISK - PENDING-MIT; no on-disk printed source; absent from Kaandorp Table 1 p. 25, which was miscited here until 2026-08-23) |
| 102 | `q8_kConvection` | TKE convection : production: `U.grad k / (|U.grad k| + |tau:S|)` | |tau_ij S_ij| | no | no |  | Kaandorp Table 1 p. 25 (dagger) |
| 103 | `q9_nonOrthogonality` | streamline non-orthogonality: `|U_i U_j S_ij| / (. + |U|^2 ||S||)` | |U|^2 ||S|| | no | yes |  | Kaandorp Table 1 p. 25 (dagger) |
| 104 | `q10_streamlineCurv` | streamline curvature marker: `|U_i A_ij U_j| / (. + |U|^2 ||grad U||)` | |U|^2 ||grad U|| | no | yes |  | Wang, Wu & Xiao 2017 Table 1, arXiv:1606.07987v2 p. 10 (NOT in Kaandorp Table 1 p. 25 - their nine scalars are Wang's ten minus curvature) |
| 105 | `q11_turbReynolds` | turbulent Reynolds number: `(sqrt(k)/(nu omega)) / (. + 50)` | 50 | yes | yes |  | Ling & Templeton 2015 (NOT ON DISK - PENDING-MIT; no on-disk printed source; absent from Kaandorp Table 1 p. 25, which was miscited here until 2026-08-23) |
| 106 | `lam1` | Pope integrity-basis invariant: `tr of the 1-th Pope invariant of (s, r)` | Durbin-bounded time scale T = max(k/eps, 6 sqrt(nu/eps)) | yes | yes |  | Pope 1975 JFM 72(2) p. 335 |
| 107 | `lam2` | Pope integrity-basis invariant: `tr of the 2-th Pope invariant of (s, r)` | Durbin-bounded time scale T = max(k/eps, 6 sqrt(nu/eps)) | yes | yes |  | Pope 1975 JFM 72(2) p. 335 |
| 108 | `lam3` | Pope integrity-basis invariant: `tr of the 3-th Pope invariant of (s, r)` | Durbin-bounded time scale T = max(k/eps, 6 sqrt(nu/eps)) | yes | yes |  | Pope 1975 JFM 72(2) p. 335 |
| 109 | `lam4` | Pope integrity-basis invariant: `tr of the 4-th Pope invariant of (s, r)` | Durbin-bounded time scale T = max(k/eps, 6 sqrt(nu/eps)) | yes | yes |  | Pope 1975 JFM 72(2) p. 335 |
| 110 | `lam5` | Pope integrity-basis invariant: `tr of the 5-th Pope invariant of (s, r)` | Durbin-bounded time scale T = max(k/eps, 6 sqrt(nu/eps)) | yes | yes |  | Pope 1975 JFM 72(2) p. 335 |

## Reproducing

```bash
cd cases/RANS_LES_closure_models/_common/features
/home/ubuntu/closure-venv/bin/python build_features.py     # -> /home/ubuntu/closure-data/features/*.npz
/home/ubuntu/closure-venv/bin/python invariance_check.py   # -> invariance_check.json
/home/ubuntu/closure-venv/bin/python fs2_audit.py          # -> fs2_audit.json
/home/ubuntu/closure-venv/bin/python make_feature_library.py
/home/ubuntu/closure-venv/bin/python make_fs2_report.py
```

