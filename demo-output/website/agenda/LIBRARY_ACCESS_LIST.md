# Papers this box cannot open

`w2-mit-access-list`. Opened 2026-08-01. **A list Katie can act on, in one
sitting, with what each item unblocks stated beside it.**

The standing permission covers open access and routes paywalled work to her
library, and until now there was no list, so a paywalled paper stalled a
reading instead of being handed over. This is that list. It is ordered by what
it unblocks, not by how interesting the paper is.

Every entry states: the exact identifier, what was tried, the one section
needed, and **what changes on the record depending on what the paper says.**
An entry with no consequence stated does not belong here.

---

## 1. Secco et al. 2021. The one that can overturn a published claim.

**Ney R. Secco, Gaetan K. W. Kenway, Ping He, Charles A. Mader, Joaquim R. R. A.
Martins**, *Efficient Mesh Generation and Deformation for Aerodynamic Shape
Optimization*, **AIAA Journal 59(4), 1151 to 1168, 2021**,
doi `10.2514/1.J059491`.

**Tried and failed:** HTTP 403 on three separate URLs, no open-access copy
found. Recorded at `demo-output/website/dafoam/ROOTCAUSE_getRotationMatrix3d.md`
line 220 and `demo-output/website/dafoam/UPSTREAM_BUG_REPORT_mesh_warpDeriv.md`
line 188, in both cases as a disclosed gap rather than a silent one.

**Re-attempted 2026-08-02, harder, and the failure is now established rather
than merely repeated.** Four new routes were tried and the entry is upgraded
from "none found" to "none exists, per two independent indexes":

* **The authors' own lab hosts a PDF link and the link is dead.** The MDO Lab
  bibliography page `https://mdolab.engin.umich.edu/bibliography/Secco2021a`
  returns HTTP 200 and offers `http://www.umich.edu/~mdolaboratory/pdf/Secco2021a.pdf`.
  That URL returns **HTTP 403 and redirects to `websites.umich.edu/errors/404.html`**.
  The same 403 is returned for the `websites.umich.edu/~mdolaboratory/pdf/` form.
  This is the fourth and fifth umich URL to fail, and it is the one the authors
  themselves point at.
* **OpenAlex**, on the DOI: `"is_oa": false`, `"oa_status": "closed"`,
  `"oa_url": null`, `"any_repository_has_fulltext": false`, and exactly one
  location, the AIAA landing page.
* **Semantic Scholar**, on the DOI: `openAccessPdf.url` is the empty string.
* **A search of every OpenAlex work by an author named Secco with "mesh" in the
  title** returns one open-access hit, and it is a different paper
  (*Component-based Geometry Manipulation…*, 2017 conference version, on Deep
  Blue). Secco's 2018 dissertation is indexed and is **not** open access, and it
  is a different work in any case.

**Verdict: this is genuinely paywalled, and no further unpaid route is worth
trying from this box.** The entry stays on this list, and it stays first.

**The one section needed:** whatever the paper says about the mesh-deformation
**derivative**, `warpDeriv`, and specifically whether it describes that
derivative as exact or as an approximation.

**What changes.** The lab's root-cause document states that no documentation,
docstring, release note or source comment qualifies `warpDeriv` as approximate.
That claim carries weight, because **an undocumented defect and a documented
approximation are two different things to report upstream**, and the report is
written to be sent. Today the claim rests on code and docs alone. One paragraph
of this paper either upholds it or withdraws it, and it is the single sentence
in the whole finding a reader with library access could overturn.

**Priority: first.** It is the only item on this list that can change something
the lab has already written down.

---

## 2. Pope 1975. The foundation under two unstarted reproductions.

**S. B. Pope**, *A more general effective-viscosity hypothesis*, **Journal of
Fluid Mechanics 72(2), 1975**.

**Status:** Cambridge University Press, not confirmed open. Not yet attempted
from this box, and that is stated rather than implied.

**The one section needed:** the derivation of the ten-tensor integrity basis
and the conditions under which it is complete.

**What changes.** The tensor-basis network and the sparse-regression method the
lab is about to reproduce both build on this basis, and the lab has read
neither it nor any substitute. The taxonomy already ranked those two methods
against each other before either paper had been read. Reproducing a method
while treating its representation as a black box is how a subtle misuse of the
basis goes unnoticed and is then defended.

**Priority: second, and only if the open-access route fails.** JFM articles of
this age are sometimes reachable; that should be tried before her library is
spent on it.

---

## 3. Conditioned field inversion. An author list nobody has verified.

*Development of a Generalizable Data-Driven Turbulence Model: Conditioned Field
Inversion and Symbolic Regression*, **AIAA Journal**, doi `10.2514/1.J064416`.

**Tried and failed:** the publisher page needs authentication; no open version
confirmed. Recorded at `demo-output/website/CLOSURE_CHALLENGE_PRIOR_ART.md`
section 2.5, which cites it **by title and DOI only** and says in the document
that the author list is unverified.

**The one section needed:** the author list, and the description of the shield
function that switches the correction off inside the attached boundary layer.

**What changes.** This is the nearest published relative of the lab's own
decline gate reached without a classifier, so it decides part of what the
closure entry may claim as its own. The lab's citation discipline forbids
naming authors it has not verified, so the paper is currently cited in a
deliberately impoverished form.

---

## 4. Buchanan, Lăcătuş, West and Dwight 2025. Probably free; check arXiv first.

*Data-Driven RANS Closures Using a Relative Importance Term Analysis Based
Classifier for 2D and 3D Separated Flows*, **Computers and Fluids 305, 106899,
2025**, doi `10.1016/j.compfluid.2025.106899`, **arXiv 2504.06758**.

**Do not spend library access on this one before trying the arXiv identifier.**
It is on the list because the published full text was among the two paywalled
items the prior-art search could not open, and because of who wrote it: Tyler
Buchanan and Richard Dwight are both co-authors of the closure challenge paper
itself, and Dwight is additionally a co-author of SpaRTA. **The people who will
read the lab's submission have published the nearest prior art twice.**

---

## 5. Steiner et al. 2022, error quantification. Deliberately not cited.

*Error Quantification for the Assessment of Data-Driven Turbulence Models*,
**Flow, Turbulence and Combustion**, doi `10.1007/s10494-022-00321-1`.

**Tried and failed:** the DOI resolves and the author list and abstract could
not be retrieved, so under the standing rule it **does not ship as a citation
at all**. `CLOSURE_CHALLENGE_PRIOR_ART.md` section 4 names it as the place
anyone extending that review should start.

**The one section needed:** author list, abstract, and whether the error
estimator is used to decide *whether* to apply a correction or only to report
confidence after applying one. That distinction is the lab's own contribution
claim.

---

## 6. ~~The closure challenge preprint.~~ **CLOSED 2026-08-02. Read.**

**McConkey, Buchanan, Smidt, Bodner, Dwight, Cinnella**, arXiv `2603.28884`,
*The Closure Challenge: a benchmark task for machine learning in turbulence
modelling*, submitted 2026-03-30.

It needed no library, as this entry said, and it is off the list. Retrieved
2026-08-02 05:14 UTC from `https://arxiv.org/html/2603.28884v1`, HTTP 200, full
text read end to end.

**The quotation is upheld, verbatim.** *"You can train on similar flows to the
test cases (for example, different parametric variations of the periodic hills
case)"* is in **Section 2.1, *Test cases***, directly after *"The test cases
cannot be used in any way at training time."* Both sentences match the
submission draft character for character. The permission the compliance
argument leans on exists and is granted in the words attributed to it.

**Three things came back that nobody had asked for, and one of them is a
correction to the preprint:**

1. **The preprint misstates α on two of the four periodic-hill test cases.**
   Its §2.1 list gives `\alpha=1.5` four times; the benchmark's own case names
   are `alpha_05_4071_4048` and `alpha_05_4071_2024`, i.e. α = 0.5, and the
   README's suggested-validation names `alpha_05_10071_*` / `alpha_15_7929_*`
   fix the convention beyond doubt. Nothing of ours depends on it, and it is a
   concrete instance of the README's own *"this page is the main source of
   up-to-date information"*.
2. **§2.2 confirms the submission route independently:** *"As of March 2026,
   submissions are via email."* A second source for the fact that this entry
   cannot be sent by anything on this box.
3. **§2.3 states the metric's interpretation in the authors' words** — *"a score
   of 0.05 indicates that predictions are off by approximately 5% of the mean
   velocity magnitude on average"* — which is now citable wherever the lab
   explains what 0.0654 means.

Full audit: `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §9. See also
`closure_challenge_C6_hump_decision.md` section 6.

---

## The open-access side of the same item

The proposal pairs this list with working the open-access seed list down, and
that half is not blocked on anybody. Its current state:

| Paper | Access | Read? | Proposal filed? |
| --- | --- | --- | --- |
| Ling, Kurzawski & Templeton 2016, JFM 807 | open | not yet | `w2-tbnn-sparta-readings` is open and unstarted |
| Schmelzer, Dwight & Cinnella 2020, FTaC 104 579 to 603 | open | **yes, and reproduced** | closed: form reproduced, PH coefficient to 0.66 percent, CBFS 0.54 against 0.93 shipped as the finding |
| Pope 1975 | see item 2 | no | `w2-pope-1975-integrity-basis` is open |

The rule the readings run under is that every reading yields a proposal or a
documented reason none is reproducible. Nothing on this page changes that.
