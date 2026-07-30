import json, pathlib, sys
sys.path.insert(0, "sdk")
from chief_engineer import agenda
DOCKET = pathlib.Path("demo-output/website/agenda/docket.json")
NOW = "2026-07-30T04:05:00Z"
NEW = [{
    "id": "r8-how-often-does-convergence-reporting-mask-divergence",
    "objective": (
        "Establish how often a solver's convergence reporting can mask a run that did "
        "not converge, by classifying every run this lab holds with an automated checker "
        "and separately auditing what a sample of published papers on our own validation "
        "cases actually state about convergence"
    ),
    "rationale": (
        "In a single night this lab found SIX published numbers of its own resting on "
        "runs that never met their convergence criterion, including one inside the "
        "correction that fixed the first two. They hid in four distinct ways: a "
        "normalised residual collapsing to a tiny fixed value while raw statistics "
        "showed a blow up; a solver exiting zero having printed a success message over a "
        "residual that underflowed to denormal range; a run reaching its iteration cap "
        "with no convergence statement while a plausible residual was quoted anyway; and "
        "a final residual quoted where the gate tests the initial one. A seventh form "
        "was found in the case configuration rather than the log, where the convergence "
        "gate named fields the turbulence model does not transport and therefore could "
        "never fire. Every instance was found by somebody looking at something else. "
        "Two observations make this worth studying rather than merely fixing. First, an "
        "automated sweep of 92 run logs classified 55 as not converged, and although the "
        "large majority were already known and disclosed, nobody had ever counted. "
        "Second, the literature review found that the best known reproduction of one of "
        "our validation cases never states a convergence tolerance anywhere in the "
        "paper, and that its closest agreement with experiment is attributed by its own "
        "authors to a coarse mesh numerical viscosity accident rather than to a "
        "modelling result. If a defect this easy to hide occurs six times in one lab's "
        "own work in one night, the reasonable prior is that it is widespread, and "
        "nobody appears to have measured how widespread."
    ),
    "citations": [
        "Certonomous convergence audit and automated checker, validated against 13 "
        "known answer cases, 2026-07-30",
        "Certonomous literature reproduction review, on convergence tolerances absent "
        "from published reproductions",
        "ASME V and V 20 on solution verification",
    ],
    "est_core_min": 30.0,
    "cost_basis": (
        "measured, the existing checker classifies 92 logs in minutes; the remaining "
        "cost is reading papers, not compute"
    ),
    "expected_knowledge_gain": (
        "A measured answer to a question the field appears not to ask: how much "
        "published computational fluid dynamics rests on runs whose convergence was "
        "never established. Our own rate is the uncomfortable part of the evidence and "
        "makes the study credible rather than accusatory, since we found it in "
        "ourselves first. It also converts a piece of internal tooling into a "
        "contribution, because the checker is the instrument the study needs and it "
        "already exists."
    ),
    "source_kind": "measurement",
    "status": "proposed",
    "created_at": NOW, "decided_at": None, "decision_note": None,
}]
d = json.loads(DOCKET.read_text())
have = {p["id"] for p in d["proposals"]}
added = [p for p in NEW if p["id"] not in have]
bad = [(p["id"], agenda.proposal_violations(p)) for p in added]
bad = [(i, v) for i, v in bad if v]
if bad:
    for i, v in bad: print(f"  VIOLATION {i}: {v}")
    raise SystemExit(1)
d["proposals"].extend(added); d["generated_at"] = NOW
DOCKET.write_text(json.dumps(d, indent=1) + "\n")
for p in added: print(f"  + {p['id']}  {p['est_core_min']:.0f} core-min")
print(f"  docket now {len(d['proposals'])}, all passing text rules")
