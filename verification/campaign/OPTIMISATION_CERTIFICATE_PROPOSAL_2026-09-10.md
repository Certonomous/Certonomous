# PROPOSAL — **NOT ADOPTED** — the CASE PROTOCOL §5 certificate for the OPTIMISATION-CONVERGENCE class, which has no grid family by construction

**Status: PROPOSAL, DRAFTED FOR SANAA'S WEEKLY. Nothing here is in force.** Held per CASE PROTOCOL §8 (*nothing reaches her during the day; only in the weekly, a spend beyond the envelope, or a frozen-gate change*). **No gate, threshold, cap, band or label is moved by this document, and no certificate is issued under it.**
**Drafted by:** verification-supervisor, as standards owner. **Routed by:** the chief, from dafoam (`719640ce`). **Date:** 2026-09-10. **Cost: 0 solver core-min, $0.00.**

---

## 1. THE PROBLEM, AND dafoam WAS RIGHT NOT TO SOLVE IT THEMSELVES

`D8R` — the A6 CRM twist optimisation — holds a **banked two-row `PASS`** and **cannot produce a §5 certificate.** §5 requires *"the gates, then the family"*: medium and fine levels, observed order, GCI, and iterative error ten times below the level difference. **`D8R` registered no grid family, deliberately**, and its own grade record says so rather than papering over it:

> `no_gci = "no grid family; standing rule 5 has no row; NO GCI IS QUOTED"`

**dafoam declined to invent a carve-out**, on the ground that changing what a certificate requires is outside §9. **That is the correct call and it is why this is a proposal and not a ruling** — §9 binds this team exactly as it binds them, and a standards owner drafting a reading is not a standards owner adopting one.

## 2. WHY THE CLASS IS GENUINELY DIFFERENT — AND THE HALF THAT CUTS THE OTHER WAY

A grid family answers **"is the discretisation error controlled?"** An optimisation run answers **"has the optimiser reached a stationary point?"** These are different questions, and the second does not become the first by adding meshes.

**But the honest caveat must be stated first, because it is the reason option (b) is not free:** an optimum computed on **one** mesh carries an **uncontrolled discretisation error**, and **the optimum itself can move under refinement** — the design variables that are optimal on a coarse mesh need not be optimal on a fine one. **So §5's family leg is not ceremonial for this class. It asks a real question, and any reading that drops it drops that question rather than answering it.**

## 3. OPTION (a) — BUILD A GRID FAMILY FOR OPTIMISATION CASES

**What it certifies:** that the **optimum** is mesh-converged — the objective and the design variables at the optimum converge under refinement. **This is the strong claim, and it is the one a reader of a certificate would assume.**

**Cost class:** **one full optimisation per level.** `D8R`-class optimisations are among the most expensive items this lab runs, so three levels is **at least** 3×, and plausibly worse: a coarse level may need different step control to converge at all, which is additional registered work rather than a cheaper copy. **No number is invented here** — this team holds no `D8R` cost figure and will not derive one it cannot cite (rule 12: a cost is never called measured unless a record backs it). **The cost must come from dafoam's own record before this option is priced.**

**The technical risk, and it is not a formality:** a coarse-mesh optimisation may converge to a **different local stationary point**. The three optima are then **incommensurable**, and a Roache triple over incommensurable states is `NOT A RESULT` under rule 5 whatever its numbers look like — the same hazard §3's ladder rule already names for a mesh repair applied to one level of a graded family. **Option (a) can therefore fail to produce a certificate after paying three optimisations for one**, and a registration choosing it must pre-register what happens when the optima diverge.

## 4. OPTION (b) — A §5 READING WHERE THE FAMILY LEG IS REPLACED BY A REGISTERED OPTIMISER-CONVERGENCE LEG

**What it would require, pre-registered before the run:** an optimiser-convergence criterion with a two-way gate — a KKT or gradient-norm bound, an objective plateau, and a step-size floor — each with its metric, threshold and direction fixed at registration.

**`§2bd` binds that plateau directly and is not optional here:** a plateau is measured over a **trailing window declared before the run**, and **a two-point difference between the last two iterates may not be gated on.** An optimiser's objective history is exactly the monotone-drift shape §2bd exists to catch, so this option inherits that clause rather than needing a new one.

**What it certifies, and this is the whole of the objection to it:** that the **optimiser** converged. **It certifies NOTHING about discretisation error.**

**Consequence under `§2bg`:** it creates a certificate class whose claim is **narrower than the word "certificate" implies**, and a headline travels alone. So a certificate issued this way must carry its exclusion **on its face** — not in a footnote, not in the record behind it — because *"a sentence whose narrower truth is disclosed somewhere the reader does not go"* is the family this lab has spent the day cataloguing.

## 5. RECOMMENDATION — HERS TO ACCEPT OR REFUSE

**(b), with two conditions, and (a) left available.**

1. **The certificate states on its face that the discretisation error is UNMEASURED**, names the single mesh the optimisation ran on, and does not use an unqualified "certified".
2. **The optimum's mesh-sensitivity is recorded as an open question against the case**, not silently absent — so the lab's own inventory shows which optimisation results have never been refined, rather than that fact being invisible.

**Why (b) over (a):** option (a) buys the stronger claim at three optimisations and **may still fail to produce a certificate** if the optima diverge (§3). Option (b) is honest, cheap, and its narrower claim is the claim the case actually supports. **(a) remains available to any optimisation case that wants the stronger claim and can pay for it**, and nothing here forecloses it.

**What this team does NOT propose:** that §5 be amended. **A reading for a class is not an amendment to the clause**, and if Sanaa judges that this needs the clause changed rather than read, that is hers and this document should be refused rather than narrowed.

## 6. NOT CLAIMED

No certificate is issued, withheld or invalidated by this document. **`D8R`'s banked two-row `PASS` stands as it is** — a `PASS` that cannot yet be certified is not a `PASS` withdrawn, and nothing here changes its verdict. No existing certificate is re-opened.
