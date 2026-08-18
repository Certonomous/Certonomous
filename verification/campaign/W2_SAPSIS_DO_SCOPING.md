# W2 scoping — dynamically orthogonal field equations, and whether they belong anywhere near our uncertainty line

Date: 2026-08-05 (UTC). **Zero compute.** One thesis fetched, two chapters read
end to end, three availability checks recorded.

Katie named dynamically-orthogonal field equations as one of the alternatives
to be scoped alongside Dow's Monte Carlo propagation. This is that scoping. It
ends in a recommendation to **not** propose it, with the reason stated as a
property of our problem rather than as an opinion about the method.

---

## 0. The artifact, and why it is a thesis and not the paper

**The primer Katie named is closed.** T. P. Sapsis and P. F. J. Lermusiaux,
*Dynamically orthogonal field equations for continuous stochastic dynamical
systems*, **Physica D 238, 2009**, doi `10.1016/j.physd.2009.09.017`. Unpaywall
and OpenAlex both checked 2026-08-05 17:13 UTC: `is_oa: false`, `oa_status:
closed`, zero open-access locations, the Elsevier landing page its only
location. Semantic Scholar returns an empty `openAccessPdf.url`. A PDF is
advertised at the first author's group server; **that host does not resolve
from this box at all** — three attempts, connection refused or no route, on
both HTTP and HTTPS, and a fetch through the other available route returned
`ECONNREFUSED`. Recorded as an availability failure, not as a paywall.

**What was read instead, and it is a primary source rather than a substitute.**
Themistoklis P. Sapsis, *Dynamically orthogonal field equations for stochastic
fluid flows and particle dynamics*, **PhD thesis**, MIT Department of
Mechanical Engineering, submitted 31 October 2010, degree February 2011,
thesis supervisor Pierre F. J. Lermusiaux. DSpace handle `1721.1/65282`, 253
pages, held at `docs/papers/sapsis_mit_phd2011_dynamically_orthogonal.pdf`,
md5 `8f4ac263ca6c4b2a9064e84b63674014`. Its chapter 3 opens: *"The material
presented in the chapter is part of the article Sapsis and Lermusiaux, 2009"* —
so the chapter **is** the primer, by the author's own statement.

**Tier, stated precisely because the artifact is long.** Chapters 3 and 4 were
**READ IN FULL** this session: chapter 3 (the DO condition, the DO evolution
theorem and its proof, and the reductions to polynomial chaos and to proper
orthogonal decomposition) and chapter 4 sections 4.1 to 4.3 (cost scaling with
stochastic dimensionality and the adaptive-dimension criteria). **Nothing is
asserted here from any other part of the thesis**, and where a claim would need
chapter 5's numerical experiments it is marked as not read rather than
inferred.

---

## 1. Claim, source, where it applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| **The DO representation is `u(x,t;w) = ū(x,t) + sum_{i=1..s} Y_i(t;w) u_i(x,t)`, with every one of the three parts time-varying**, unlike proper orthogonal decomposition (fixed modes) and polynomial chaos (fixed stochastic coefficients). | Chapter 3 equation (3.10) and section 2 closing; READ IN FULL. | The whole point of the method: the stochastic subspace is *evolved*, not chosen a priori. | It is a representation of a field that **evolves in time**. Every quantity in it is a function of `t`. |
| **The DO condition is `<partial u_i / partial t, u_j> = 0` for all i, j** — the basis is only allowed to move normal to the stochastic subspace, because motion inside the subspace is already expressible as a rotation of the coefficients. It removes the redundancy of the representation and it preserves orthonormality automatically. | Chapter 3 section 3.3, equation (3.11); READ IN FULL. | The single idea the method rests on, and it is one line. | Nothing in it is specific to fluids or to uncertainty in a closure; it is a statement about redundancy in a time-dependent expansion. |
| **The DO evolution equations are one PDE for the mean, `s` PDEs for the modes, and an `s`-dimensional system of SDEs for the coefficients**, derived from the original stochastic PDE with no closure assumption. | Chapter 3 Theorem 10, equations (3.12) to (3.14), proof read; READ IN FULL. | Exact and closed for a given `s`. This is a genuinely strong result and the derivation is short. | It requires the governing stochastic PDE **and the ability to modify the solver to march these coupled equations**. It is intrusive by construction. |
| **Imposing polynomial chaos's fixed coefficients recovers the polynomial chaos equations; imposing proper orthogonal decomposition's fixed modes recovers the POD equations.** Both reductions are shown. | Chapter 3 sections 3.5.1 and 3.5.2; READ IN FULL. | The clean way to describe DO to Katie: it is the generalisation that contains both of the alternatives she named, and it degenerates to each of them under an extra assumption. | It is a statement about the *equations*, not a claim that DO is cheaper or more accurate than either on any particular problem. |
| **Cost scaling: DO storage grows linearly in the stochastic dimension `s`, and its operation count grows as `O([Ns]^q)` where `q` is the order of nonlinearity of the operator** (`q = 2` for Navier-Stokes), independent of `s` in the exponent. Polynomial chaos storage grows as `O(Ns^p)` with `p` the polynomial order, and its cost as `O([Ns^p]^q)`. Direct sampling of `s` dimensions is `O(N^s)`. | Chapter 4 section 4.2; READ IN FULL. | The honest reason anyone reaches for DO: it removes the curse of dimensionality from the *representation*, which polynomial chaos does not. | These are scalings, not measured costs, for everything except the one figure below. |
| **The one measurement**: for a stochastic lid-driven cavity, wall-clock time against the number of modes fits a log-log slope of **1.986** against a theoretical 2. | Chapter 4 figure 4-1 and its caption; READ IN FULL, value read from the caption text and not digitised from the plot. | It confirms the exponent on a Navier-Stokes case. | **It is a slope, not a cost.** No absolute time, no mesh size and no comparison against a Monte Carlo run appears in the two chapters read. Nothing here says DO was cheaper than sampling on that case. The underlying experiment is chapter 5, which was not read. |
| **The stochastic dimension is adapted at runtime** from the eigenvalues of the coefficient covariance, with stated criteria for contracting and expanding the subspace; realistic ocean applications are said to need `s` of order 10 to 1000. | Chapter 4 sections 4.1 and 4.3.1; READ IN FULL. | This is what makes DO practical for transient problems where the uncertainty dimension itself changes. | The order-10-to-1000 figure is quoted from the group's own ocean work, cited to reference 82, which was not read. Tier: it is their citation, not our reading. |

---

## 2. The scoping verdict, and the reason is a property of our problem

**Recommendation: do not propose dynamically-orthogonal propagation for the
uncertainty line, and record why so the question does not get re-opened by
enthusiasm.** Three reasons, in decreasing order of how hard they are to argue
with.

**1. Our propagation problem has no time in it.** DO is a set of evolution
equations. Every one of its three components — the mean PDE, the mode PDEs and
the coefficient SDEs — is a `partial / partial t`, and the DO condition itself
is a statement about how the basis is allowed to *move*. The band the lab wants
is over a **steady** RANS solution: a discrepancy field is drawn, a steady
solve is run, a quantity of interest comes out. There is no stochastic
evolution to track, so the machinery whose entire value is tracking one
efficiently has nothing to do. This is not a limitation of DO; it is an
observation that our problem is the wrong shape for it, and it is ours, not a
claim from the thesis.

**2. It is intrusive, and our solver is a container we do not own.** The DO
equations are marched *instead of* the original equations. Adopting DO means
implementing `s + 1` coupled field equations inside the solver. The lab's
current standing capability is a single patched turbulence-model term inside a
vendor image, and landing even that is an open item with an unmeasured build
time. The gap between those two is not a rung, it is a different project.

**3. Where DO's advantage is largest, our sampling cost is already small.**
DO's cost argument is against the curse of dimensionality in the *stochastic*
dimension. Dow's propagation draws from a Karhunen-Loeve expansion in which
"the full expansion can be approximated quite well with very small `N_KL`"
because the log-discrepancy varies smoothly. A handful of modes propagated by
plain Monte Carlo is exactly the regime where an intrusive reduced-order method
buys least.

**What would change this verdict**, stated so the decision is falsifiable
rather than permanent: an unsteady quantity of interest with a propagated band
— a shedding frequency, a cycle-to-cycle statistic, a transient load — where
the uncertainty has to be carried through time rather than sampled at a
converged state. The lab has unsteady families on the record. If a banded
unsteady statistic ever becomes the deliverable, this scoping should be
re-read, starting from chapter 5 of this thesis, which was deliberately not
read here.

**What we take from it anyway, at zero cost.** The reduction proofs of section
3.5 are the cleanest available statement of how polynomial chaos and proper
orthogonal decomposition relate to each other and to a general Karhunen-Loeve
expansion, and the lab can cite that relationship correctly now instead of
describing the three as unrelated alternatives.

---

## 3. Charter section 6 — which trigger fired

- **Trigger 1, a number on a case we can build: did not fire.** The two
  chapters read contain one measured quantity, a log-log slope of 1.986 on a
  stochastic lid-driven cavity whose configuration is in a chapter that was not
  read. There is no case definition here to build.
- **Trigger 2, admissibility as thresholds: did not fire.** Nothing in the DO
  formulation is a threshold on a physical field.
- **Trigger 3, disagrees with one of our results: did not fire.**
- **Trigger 4, limit case at zero compute: FIRED and was checked, by reading.**
  The stated limit cases are the two reductions: freeze the stochastic
  coefficients and DO becomes polynomial chaos; freeze the modes and it becomes
  proper orthogonal decomposition. Both are proved in section 3.5 and both were
  followed through. A third limit is the one that decides this scoping: with no
  time derivative there is no DO system at all.

**No proposal is filed from this reading, and the trigger that did not fire is
named rather than the closing being "interesting but not actionable".** The
actionable output is the recommendation in section 2 and the falsifier attached
to it.

---

## Related

- `docs/papers/sapsis_mit_phd2011_dynamically_orthogonal.pdf` and `.txt`.
- `demo-output/website/campaign/W2_DOW_STRUCTURAL_UQ_READING.md` — the reading
  this was scoped alongside.
- `demo-output/website/campaign/W2_DOW_STRUCTURAL_UQ_PROGRAM.md` — the program,
  whose propagation step this scoping decides the method for.
- `demo-output/website/agenda/LIBRARY_ACCESS_LIST.md` — where the closed
  Physica D primer is filed.
