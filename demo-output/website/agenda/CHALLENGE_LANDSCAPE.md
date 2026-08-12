# Every public challenge this lab could enter, and whether it could send

**Swept 2026-08-02.** Clock verified before any deadline was called past or
future: `date -u` reads `Sun Aug 2 05:36:13 UTC 2026`.

**Nothing found is sendable.** Every live route ends at one of four gates — an
account, an organiser-issued participant identifier, a pull request, or an email
to a person. All four are on this lab's forbidden list, so the sweep's result is
not a shortlist of entries. It is a map of which walls stand where, and it is
worth having before any compute is spent on the far side of one.

**The one finding that changes a decision: the closure challenge is one email
away, and nothing else is close.** Its entry already exists, already scores, and
its entire submission mechanism is a message to the steward. Every other live
item needs an account or an identifier as well.

> **Provenance.** The sweep was run by a scouting agent that fetched and read
> each page; the rows below carry the wording it read. **Two load-bearing dates
> were re-fetched independently before being written here** — AutoCFD5's
> submission deadline and the RealPDE phase table — because they are the two
> that would drive a decision. Rows that could not be fetched are marked
> UNKNOWN with the reason, not guessed.

---

## 1. Live, with a future deadline or no deadline

| Challenge | Deadline | May a company enter? | To send an entry you need | Verdict | Cost of a credible entry |
| --- | --- | --- | --- | --- | --- |
| **The Closure Challenge** (steward Ryley McConkey, MIT) | **None.** *"Submissions are accepted anytime!"*; *"This is an **ongoing** challenge."* | No eligibility clause of any kind exists in the README, the package or the preprint | **An email**, and nothing else. README step 3: *"Send your `test` subdirectory to Ryley McConkey: rmcconke@mit.edu."* No account, no identifier, no pull request | **PREPARABLE, NOT SENDABLE** — one forbidden act, the smallest one in the sweep | **Zero. The entry exists**, scores 0.0654, and the eight CSVs are written and hashed |
| **AutoCFD5**, 5th Automotive CFD Prediction Workshop | **21 August 2026**, *"Results data submission deadline"* — 19 days out. **Re-verified from `autocfd.org/dates/` by this agent** | No restriction on company type stated | Three gates at once: a submission identifier *"allocated to you by the organisers"*, a dashboard login the organisers provide, and an email to `admin@autocfd.org` | **PREPARABLE, NOT SENDABLE** | **Does not fit this box.** Minimum entry is the baseline **g2 grid, 37M cells**; against the lab's own measured memory law that extrapolates to ~58 GiB on a 30.6 GiB host. The coarse g1 at 6.3M cells would fit at ~10.6 GiB and does not meet the stated minimum. The deliverable also wants force and base-pressure **time histories** and PIV **RMS** — eddy-resolving, not steady RANS |
| **NeurIPS 2026 RealPDE**, Tracks 1 and 2 | **Registration 20 August 2026.** Main development phase `2026-07-20 → 2026-09-27`, status Current. **Re-verified from the Codabench API by this agent** | **Yes, explicitly.** Rules table: *"Open to all individuals and academic/industrial teams worldwide."* But the terms also read *"provided for **non-commercial** research and competition participation"* | A Codabench account **and** a separate registration form: *"Joining the Codabench competition alone does not count as registration"* | **PREPARABLE, NOT SENDABLE**, and the non-commercial clause is a second problem for us | **No CFD at all.** Paired PIV and CFD on NACA4418 at Re 5025, AoA 5°. Pure PyTorch supervised learning. 207 participants and 518 submissions already on Track 1; a 2-core box with no GPU is the binding constraint, not the physics |
| **AIAA HLPW-6** | None stated; milestone-based toward Aviation 2027 | Open, but *"their results will not be included in any summary presentations"* if not on a technology focus group | GitHub account, an identifier from the focus-group leads, and a pull request | **PREPARABLE, NOT SENDABLE** — all three forbidden gates. Independently re-confirms `hlpw6/SUBMISSION_GATE.md` | 6,390 core-min at 14 ranks for the 2.66M-cell coarse grid, plus an unpriced 8-view rendering deliverable |
| **CYPHER 2025**, ML for turbulent combustion | Final phase open, no end date | No restriction stated | Codabench account; second route is an email | **PREPARABLE, NOT SENDABLE** | No CFD; sub-filter closure for LES of hydrogen flames. **Off-domain** — reacting flow is not in this lab's stack |
| **CYPHER 2026 hackathon**, ROM for combustion | Development phase to 2026-09-12 | Not stated | Codabench account **plus manual organiser approval** (`registration_auto_approve: false`) | **PREPARABLE, NOT SENDABLE** | Off-domain |
| **AIAA Weapons Bay Store Separation** | Workshop 3–4 June 2028; no submission deadline published | *"government, industry, and academia"* | **Not published.** A GitHub org is its only stated home | **UNKNOWN** — mechanics not published, and that is stated rather than inferred from the GitHub pattern | Unsteady cavity aeroacoustics with 6-DoF coupling. Not stood up here |
| **FluidsBench** | Not open. *"More details coming soon"*, dated 28 February 2026 | — | Mailing-list signup or email | **UNKNOWN, not yet open** | — |
| **4th ERCOFTAC ML for Fluid Dynamics** | 7–9 April 2027, *"More information will be provided in due course"* | — | No call yet | **UNKNOWN, nothing to enter** | — |

**Watch items, and why they are worth watching.** FluidsBench and the ERCOFTAC
2027 workshop are organised by the same circle as the closure challenge and
AutoCFD — Ashton, Cinnella, Dwight, Vinuesa among them. The next round of the
benchmark this lab already has an entry for is more likely to land there than
anywhere else on this page.

## 2. Closed, verified past rather than assumed

Six, each with the operative wording read off its own page: **AIAA Ice
Prediction Workshop 3** (results *"due by 1 July 2026"*, 32 days past);
**AIAA LFC Transition-Prediction Workshop** (*"All Cases due by 20 March
2026"*, and worth noting for its wording *"AIAA membership is not required to
submit results"*); **AIAA Propulsion Aerodynamics Workshop 7** (*"kindly
requested by December 1, 2025"*); **DPW-8 / AePW-4** (workshop held June 2026,
and not sendable regardless — email plus GitHub plus an assigned participant
identifier); **ML4PhySim / ML4CFD** (*"The competition is already finished"*);
**ERCOFTAC Milton van Dyke 2026** (deadline 1 February, and gated on ERCOFTAC
membership besides).

## 3. Verified to have no open call at all

Fetched and read, not assumed: **NASA/AIAA Turbulence Modeling Resource and the
TMBWG** — the whole resource moved to GitHub in February 2026 and there is no
competition, no leaderboard and no deadline on it, only an email to a page
curator; **AIAA Stability and Control Prediction Workshop** (content stops at
December 2024); **AIAA High-Fidelity CFD Verification Workshop** (still
advertising SciTech 2024); **AIAA Geometry and Mesh Generation Workshop** — the
domain `gmgworkshop.com` **does not resolve**, NXDOMAIN; **AIAA Sonic Boom
Prediction Workshop** (latest content 2022); **ASME VVUQ challenge problems**
(both results pages read *"Coming Soon!"*).

**Two platform-wide enumerations, so the absence is measured rather than
inferred.** All **25** currently-approved public EvalAI challenges were
enumerated: **zero** relate to fluids, CFD, turbulence, PDEs or aerodynamics.
Codabench was searched on fifteen terms (turbulence, fluid, CFD, aerodynam,
flow, PDE, Navier, RANS, combustion, physics, simulation, airfoil, scientific,
wind, mesh) and the only fluids or physics hits are the four already in the
table above plus two concluded ones. **Kaggle could not be enumerated** — its
API returns HTTP 401 without an account and the web listing is JavaScript only.
That is recorded as UNKNOWN, though it is moot: a Kaggle entry needs a Kaggle
account, so it is not sendable by construction.

## 4. The one genuinely new opening, and it is inside an item we already hold

**HLPW-6 has an AI/ML technology focus group, and it is a zero-CFD route into a
workshop this lab had priced only as a 6,390 core-minute solve.** Its key
question 6 asks *"Can data-driven turbulence models improve the predictive
accuracy of lower-fidelity solvers (e.g., RANS or coarse LES)"*, trained on the
open **HiLiftAeroML** dataset — 1,800 samples, 180 geometry variants at 10
angles of attack, CC-BY-4.0. That is this lab's actual competence, it needs no
mesh and no solve, and the docket currently carries the high-lift entry only in
its expensive form. **The focus group's own page currently reads "More coming
soon", so there is nothing to enter yet and no deadline to miss** — which is
exactly why it is worth knowing now rather than in January.

## 5. Two corrections to numbers that were repeated back at us

The sweep reported the closure entry as **0.0676** and as leading **five of
eight** cases. **Both are superseded and neither may be used.**

> **Superseded 2026-08-07 (family supervision review F3).** The entry of
> record is now **round 5: overall 0.0566, rank 1 of 5 scored locally at
> benchmark commit `deb91557`** — a local scoring, not an official
> placement, carrying the seed qualifier of
> `CLOSURE_CHALLENGE_STATUS.md` §0f — and best-on-board is **4 of 8**.
> The §1 row's "scores 0.0654" and the bullets below stand as this sweep's
> dated 2026-08-02 record; per this section's own rule, the superseded
> numbers may not be used.
>
> **Rank-1 companion (MANDATORY, ~~2026-08-10~~ — RECOMPUTED 2026-08-11 against a
> SIX-entry board).** **P(rank 1) = 50%** — 50.2% over a 400,000-draw case-level
> bootstrap — and an eight-case sample cannot pin it tighter than **0–97% at 95%**
> (double bootstrap). **Frame:** the **six**-entry LIVE board fetched
> 2026-08-11T23:33Z by two routes; eight cases; our 0.056647191704213645 from
> `closure_challenge_round5_qcr.json` at commit `07a7fe9e`.
> ~~**P(rank 1) = 68%**, 2–100% at 95%~~ — **STRUCK 2026-08-11: computed
> 2026-08-10 against a FOUR-entry board that no longer exists.** The board now has
> six entries and a new leader, Yang at 0.0580; our margin over the leader is
> **0.001365**, not 0.002878 (`campaign/BOARD_MOVED_2026-08-11.md`).
> **Four leads are now not statistically decided** — Yang (t = −0.19), Reissmann
> (t = −0.50), Wu & Zhang (t = −0.95) and Tian, Buchanan, Hickel & Dwight
> (t = −1.03); the leads over Liu and Montoya are decided (98.7%, 99.8%).
> **The standing is three deletions wide** (~~two cases wide~~) — deleting any of
> `alpha_15_13929_4048`, `alpha_15_13929_2024` or `alpha_05_4071_4048` drops the
> point rank to 2, 3 and 2; delete `NASA_2DWMH` and P(rank 1) rises to 78.5%.
> **`AR_1_Ret_360` and `AR_3_Ret_360` are ties below published precision** (0.00003
> and 0.00008) and are not per-case wins or losses. Source:
> `campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`; the superseded four-entry
> computation is kept, not deleted, at `campaign/PROBABILITY_OF_RANK_2026-08-10.md`.
> The figure may never appear without its interval **and its board**.

* The entry of record is **0.0654**, not 0.0676, since round 4's duct change
  (`closure_challenge_trained_entry_round4_duct.json`). 0.0676 is the round-3
  figure.
* **"Best on five of eight" was withdrawn by this lab on 2026-08-01** and must
  not come back. Two of those five were the organisers' own unmodified baseline
  field, which the decline gate correctly withheld our model from; they rank the
  baseline, not us. The honest count is two clear leads, one nominal lead of
  0.00003, two rows that are the baseline, and three behind. See
  `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §8.2.

**A superseded number does not stop being wrong because an outside search
repeated it back.** Both are recorded here so the next sweep does not
re-import them.

## 6. What this sweep decides

1. **The closure challenge stays the lab's best public position by a wide
   margin, and the whole distance to it is one email Katie sends.** No account,
   no identifier, no pull request, no deadline, no submission limit. Everything
   the lab can do without her is done: the CSVs exist and are hashed, the
   compliance audit is written, and as of 2026-08-02 every quotation in the
   draft resolves to a source somebody here has read.
2. **AutoCFD5 should be recorded as scouted and declined rather than left
   open.** It is the only live item with a near deadline, and it fails on
   physical grounds before the forbidden list is even reached: a 37M-cell
   minimum against a 30.6 GiB host, and an unsteady time-history deliverable.
   Nineteen days would not be enough even if the memory fitted.
3. **The AI/ML focus group of HLPW-6 is worth a docket item and the high-lift
   solve is not the only way in.** Nothing to enter yet; that is a reason to
   file it, not a reason to forget it.
4. **Scouting has now been run to the bottom of the landscape.** Two whole
   platforms were enumerated rather than sampled, and six workshops were
   confirmed to have no open call. **The next sweep should be triggered by a
   date, not by curiosity** — FluidsBench and the ERCOFTAC 2027 call are the
   two that will change, and both come from the circle that runs the benchmark
   we already have an entry for.
