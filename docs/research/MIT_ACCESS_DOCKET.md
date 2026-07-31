# MIT-access docket — papers this lab could not fetch itself

**For Katie, to route to Sanaa's MIT access.** Opened 2026-07-30 (UTC) during well W2
of the Perpetual Research Engine order.

Each row is a paper the lab tried to fetch and could not, with the availability check
that was actually run and its actual answer. Per the literature charter section 2,
"availability checks are reported, never assumed" — a row here means a machine-checked
refusal, not a guess that something is probably behind a paywall.

**Nothing on this list is cited anywhere in the lab's records for anything beyond its
title, authors, venue and year as read off a metadata artifact.** No claim about any of
these papers' contents appears in any lab document sourced to this docket.

---

## 1. Parish & Duraisamy (2016) — field inversion and machine learning

| Field | Value | Where it came from |
| --- | --- | --- |
| Title | A paradigm for data-driven predictive modeling using field inversion and machine learning | CrossRef record for the DOI, fetched 2026-07-30 |
| Authors | Eric J. Parish; Karthik Duraisamy | CrossRef |
| Venue | *Journal of Computational Physics*, volume 305, pages 758-774 | CrossRef |
| Issued | 2016-01 | CrossRef |
| DOI | `10.1016/j.jcp.2015.11.012` | CrossRef |

**Why it matters.** It is the method paper behind roadmap item 4A Stage 1. It is the
highest-priority item on the W2 seed list.

**Availability checks run, and their answers:**

- **Unpaywall** on `10.1016/j.jcp.2015.11.012` (2026-07-30): `is_oa: false`. Zero OA
  locations returned.
- **OpenAlex** on the same DOI (2026-07-30): `oa_status: "closed"`,
  `any_repository_has_fulltext: false`, `oa_url: null`. The single location OpenAlex
  holds is the publisher landing page with `pdf_url: null`.
- **Semantic Scholar** graph API on the same DOI (2026-07-30): reports
  `isOpenAccess: true` with `openAccessPdf.status: "BRONZE"` pointing at the
  ScienceDirect accepted-manuscript path `article/am/pii/S0021999115007524`. **A direct
  fetch of that URL returned HTTP 403.** Semantic Scholar's "bronze" flag is therefore
  wrong in practice here, and this disagreement between two metadata services is
  recorded rather than resolved in favour of the optimistic one.
- **arXiv** full-text search for `all:"field inversion and machine learning"`
  (2026-07-30): eight hits returned, none of them this paper. There is no arXiv
  preprint of it.
- **UMich Deep Blue** institutional repository: the search endpoint returned a
  Cloudflare interstitial rather than results, so this check is **inconclusive, not
  negative**. Worth one manual look from an MIT or UMich session before buying access.

**What the lab did instead, so the milestone was not blocked.** The FIML requirement
question (mesh size, adjoint capability, compute) was answered from open papers in the
same lineage that were read in full — see
`demo-output/website/campaign/W2_CLOSURE_LITERATURE_READING.md`. Those answers are
attributed to the papers that actually state them, never to Parish & Duraisamy.

**What full-text access would still buy.** The original derivation of the inverse
problem and its regularisation, and the model problems the paper builds its paradigm on,
at first hand rather than through the later papers' restatements of it. The literature
charter forbids citing another paper's characterisation of a third paper as the basis of
a claim, so every downstream FIML claim the lab makes currently has to be sourced to a
successor paper rather than to the origin.

---

## Closed rows — checked, and access turned out not to be needed

Kept so the docket shows what was checked, not only what failed.

**Ling, Kurzawski & Templeton (2016).** *Reynolds averaged turbulence modelling using
deep neural networks with embedded invariance*, DOI `10.1017/jfm.2016.615`, *Journal of
Fluid Mechanics* (CrossRef, 2026-07-30). Unpaywall reported `is_oa: true` with a
repository copy at OSTI. The Sandia accepted manuscript **SAND2016-7345J** was fetched
and read in full. **No MIT access required.** Full text read into the knowledge store
2026-07-31, `demo-output/website/campaign/W2_TBNN_SPARTA_READING.md` section 1.

**Schmelzer, Dwight & Cinnella (2020).** *Discovery of Algebraic Reynolds-Stress Models
Using Sparse Symbolic Regression*, DOI `10.1007/s10494-019-00089-x`, *Flow, Turbulence
and Combustion* 104:579–603. Checks run 2026-07-31: **CrossRef** returns the article with
two `creativecommons.org/licenses/by/4.0` licence records; **Unpaywall** returns
`is_oa: true`, `oa_status: "hybrid"`, with four locations — the Springer published
version, an arXiv submitted version at `arxiv.org/pdf/1905.07510`, TU Delft and HAL. The
**published version of record** was fetched from Springer in preference to the preprint
and read in full, so no preprint caveat attaches to anything sourced to it.
**No MIT access required.** Read into the knowledge store 2026-07-31,
`demo-output/website/campaign/W2_TBNN_SPARTA_READING.md` section 2.

---

## How to use this docket

For each open row, what is wanted is the publisher PDF. Send it to `docs/papers/` under
the naming pattern the directory already uses, and the lab will index it and file its
reproduction proposal on the next reading well.
