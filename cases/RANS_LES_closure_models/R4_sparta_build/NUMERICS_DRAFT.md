# NUMERICS_DRAFT — R4 SpaRTA-class build lane

For `docs/NUMERICS_KNOWLEDGE.md`. Every entry is measured in this lane and cites
the artefact it came from. Numbering is assigned by the supervisor at commit.

---

**N-R4a. The k-corrective-frozen-RANS extraction reproduces bit for bit, and the
reproduction is the check that the rebuild is sound.** Rebuilt independently
from the benchmark's own fields, `PHLL10595` and `CBFS13700` return
`0/{U,k,tauij,omega,nut}` **byte-identical** to
`verification/runs/W2_sparta_runs/{ph,cbfs}_frozen`, settle at the W2 record's
own iterations, and write `bijDelta`, `kDeficit`, `bijData`, `U`, `k`, `omega`
and `nut` **byte-identical** at `1492/` and `354/`. A rebuild that differed in
any input, boundary condition or dictionary could not do that.
Source: `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §2.1.

**N-R4b. The frozen `omega` equation carries an explicit source divided by
`nu_t`, and the shipped hills carry `nu_t` down to 5.55e-12.**
`kOmegaSSTFrozen.C` builds `gamma*(PkLim + Rterm)/max(nut, 1e-12)`. Where `nu_t`
is at that floor the source is amplified by up to **1e11**, `omega` is driven
negative, and `bound(omega, omegaMin)` replaces those cells with a local average
**every iteration**. Consequence, measured on the 21 `Parm_PH_29` training
hills: **13 sit in a limit cycle** whose residual is identical to fifteen
significant figures at iteration 5000 and at iteration 20000
(`initRes = 4.21656145422043e-04`, `max rel domega = 0.105158858322751`), so
**extending the backstop is useless**; **2 report a false convergence** after
being clipped flat; **6 converge and never bound `omega` once**. The four ducts,
`PHLL10595` and `CBFS13700` never bound it either.
Repairs tested and **all four failed**: flooring `k_LES <= 0` cells at
`1e-4 x mean k_LES` with isotropic `tau`; the same at `1e-2 x mean k_LES`;
inserting the `div(phi,omega) Gauss linearUpwind grad(U)` scheme the hills alone
omit; and quadrupling the backstop.
Source: `R4_sparta_build/RESULTS.md` §2.3.

**N-R4c. The 21 `Parm_PH_29` hills are the only benchmark family whose
`system/fvSchemes` declares no `div(phi,omega)`.** It falls through to
`default Gauss linear` — unbounded central differencing on the `omega`
convection term — while `PHLL10595` uses `bounded Gauss linearUpwind grad(U)`,
`CBFS13700` uses `Gauss linearUpwind grad(U)` and the ducts use
`bounded Gauss linearUpwind limited`. The hills also declare `div(phi,epsilon)`,
a k-epsilon leftover, which no `kOmegaSST` run reads. **Inserting the missing
scheme does not by itself fix the frozen extraction** (N-R4b), so it is recorded
as a defect in the shipped cases, not as the cause.

**N-R4d. Every one of the 21 hills carries cells with `k_LES <= 0`; no other
training family does.** 7 to 51 cells per hill, 0.045 %–0.33 % of the mesh,
minimum `k_LES` from −2.5e−04 to −6.8e−03; the ducts, `PHLL10595` and
`CBFS13700` carry none. **The trap is that `bound(k, kMin)` inside the model
replaces them with a small POSITIVE number**, so a `k > 0` mask on the field the
solver *writes* cannot find them, and `b^Delta` there reaches `O(1e5)` — an RMS
`||b^Delta||_F` of **35,478** on `alpha_10_12000_4048` against ~0.3 on every
other case. The mask must be taken on the **shipped** `0/k`.
Source: `R4_sparta_build/RESULTS.md` §2.3, §3.3.

**N-R4e. The exact duct tensor-basis degeneracy is a property of the linear-EVM
RANS field, not of the frozen field a SpaRTA regression fits.** On
`AR_1_Ret_180`, over all 2,209 cells:

| field | `\|\|T3+T4\|\|/\|\|T3\|\|` median | p99 | `\|I1+I2\|/\|I1\|` median | per-cell rank of `{T1..T4}` |
|---|---|---|---|---|
| baseline RANS | 2.7398e-17 | 6.4084e-16 | 0.000e+00 | **3.000** (2209/2209 at rank 3) |
| frozen (`U = U_LES`) | 1.2779e-02 | 4.6889e-01 | 7.0405e-05 | **3.965** (2132/2209 at rank 4) |

Frozen per-cell rank on all four training ducts: 3.965, 3.977, 3.978, 3.977. A
linear EVM produces no duct secondary flow, so `S^2 + Omega^2` is isotropic and
the deviatoric parts cancel exactly (the same fact L-219 states from the
anisotropy side); the DNS mean flow has secondary motion and they do not.
Source: `R4_sparta_build/RESULTS.md` §3.2.

**N-R4f. `R` spans eight orders of magnitude across the training families, so a
pooled fit on the raw quantity is a duct fit.** RMS `kDeficit`: **0.0066**
(`CBFS13700`), 0.0346–0.0625 (hills), 0.0588 (`PHLL10595`), **1.61e+06–1.70e+06**
(the four ducts, whose bulk velocity is ~37.5 m/s on a 1 mm half-height). The
non-dimensionaliser used here is the case median of `k*omega`, a physical scale
of the same dimensions taken from the frozen fields and not from the target; one
positive constant per case leaves every fitted coefficient unchanged.
Source: `R4_sparta_build/RESULTS.md` §3.4.

**N-R4g. `kOmegaSSTSparta` implements T1–T3 only and a term registered with
`n = 4` silently evaluates as T3.** `kOmegaSSTSparta.C` builds `T1 = S`,
`T2 = SW − WS`, `T3 = S² − I tr(S²)/3` and dispatches
`n == 1 ? T1 : n == 2 ? T2 : T3`. There is no bounds check and no warning.
**Reported to the owner of `sdk/`.** Any writer of `RTerms`/`bDeltaTerms` should
assert `n in (1,2,3)` before the dictionary is written; `build_aposteriori.py`
does.

**N-R4h. On this training set the T1–T3 restriction costs nothing.** The
`b^Delta` model fitted on T1–T3 generalises **better** across families than the
unconstrained T1–T4 fit — leave-one-family-out MSE **0.0156199** against
**0.0158092** — the two agreeing exactly on `T2` and `I2 T2` and differing only
by `+5.0391 T3` against `−6.7275 T4`.
Source: `R4_sparta_build/MODEL.md`.

**N-R4i. IC1: the symbolic model the solver evaluates is the one the record
states.** An independent Python evaluation of the frozen term sets against
`kOmegaSSTSparta`'s own `writeInitialCorrections` fields agrees to **5.08e-13**
relative L2 on `bijDelta` and **3.97e-12** on `kDeficit`, over all 12 cases —
the ascii `writePrecision 15` round-trip floor.
Source: `R4_sparta_build/artefacts/ic1_discovered.json`.
