"""
AMENDED 2026-08-10 (chief ruling 7abb0ba3): this generator emits proposal text
containing claims about the B-52 ladder's "turn", which is WITHDRAWN as a claim --
see demo-output/website/campaign/B52_TURN_WITHDRAWAL_2026-08-10.md.
The published -4.055e-3 turn is max(rung 6) minus min(rung 7) of eight same-recipe
draws; re-estimated from all of them the increment is +8.2e-5 +/- 1.2e-3, opposite in
sign. A REGENERATION FROM THIS SCRIPT WOULD REINTRODUCE THE WITHDRAWN TEXT into the
docket, which is why the generator is amended alongside its output rather than after
it. The emitted strings are left byte-identical so the historical filings stay
reproducible; this header is the correction.
"""
"""File the [FILE] diagnostics of the supervisor's negative-verdict review.

Source: demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md,
written under Katie's directive of 2026-08-07. The review marks THIRTEEN
diagnostics [FILE] (the filing brief said eleven; the review's own markers
are binding and there are thirteen of them). Each is filed twice, per the
current mechanics: a JSON in demo-output/website/agenda/proposals/ so the
inbox reader can always rebuild the docket, and a full-schema entry in
docket.json itself. Five are approved on filing under Katie's standing
green light, the five the review's logic ranks first by cost against
decisiveness: the F5c inlet audit, the BEM cross-check, the S10 replay,
the QCR-on-hills arm, and the A3 sub-LU arm. Everything else is proposed.

Validation before writing: chief_engineer.agenda intake rails
(proposal_violations, which folds in the style rails, cost rail,
source_kind, hard_criterion and archive-replay rails), the advisory
premise rail, id-collision and objective-collision checks against the
whole docket and inbox, and a read_inbox round trip proving no filed
JSON is silently dropped at ingestion.
"""
import json
import pathlib
import sys

sys.path.insert(0, "sdk")
from chief_engineer import agenda  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
DOCKET = REPO / "demo-output/website/agenda/docket.json"
INBOX = REPO / "demo-output/website/agenda/proposals"
NOW = "2026-08-07T22:10:00Z"
NOTE = "supervisor review 2026-08-07 under Katie's standing green light"
USD_PER_CORE_MIN = 0.01367  # the docket's own measured pricing ratio


def usd(cm):
    return round(cm * USD_PER_CORE_MIN, 3)


NEW = [
    # ---- review section 1: F6b periodic hills, physics FAIL ----
    {
        "id": "f6b-model-form-matrix-on-the-hills",
        "well": "W3",
        "objective": (
            "Run the model-form matrix on the ERCOFTAC periodic hills, the "
            "standing batch's four closure families on the medium rung of "
            "our own verified mesh, to learn whether any closure enters the "
            "literature reattachment band and whether the inter-model band "
            "contains it"),
        "rationale": (
            "The hills closed with a physics FAIL, reattachment 72 percent "
            "long against the literature band, and the failure was verified "
            "onto the model rather than onto us: our own mesh agrees with "
            "the shipped grid to 0.043 percent with 0.097 percent grid "
            "sensitivity. What the verdict taught is that SST overpredicts "
            "separated-region length on the hills the same way it does on "
            "the hump, a two-leg pattern. The standing model-form batch "
            "already runs four closure families on other cases; extending "
            "its family set to the hills asks the two questions the verdict "
            "left open, whether any closure enters the band and whether the "
            "inter-model band contains the reference, and feeds the "
            "epistemic-uncertainty showcase directly."),
        "gate": (
            "Four solves, one per closure family, on the medium rung of the "
            "verified in-house hills mesh, each read against the published "
            "reattachment band under outcomes declared before launch. "
            "Outcome one: at least one closure lands inside the literature "
            "band, which locates the failure in closure choice rather than "
            "in the class. Outcome two: none does but the inter-model band "
            "contains the reference, which is the epistemic-uncertainty "
            "result. Outcome three: even the inter-model band excludes the "
            "reference, which is a class-level finding. No scoring call is "
            "made; the matrix reports whichever outcome the runs deliver"),
        "est_core_min": 35,
        "predicted_memory_gb": 2.0,
        "predicted_usd": usd(35),
        "cost_basis": (
            "estimate, the review's own figure: four closures at the medium "
            "rung of a ladder whose rungs this campaign has already run and "
            "logged, so the per-solve price is anchored to the family's "
            "recorded spend rather than to a guess"),
        "expected_knowledge_gain": (
            "Either a closure that works on the hills, which redirects the "
            "two-leg separated-flow finding from the class to the closure, "
            "or a measured inter-model band whose relation to the reference "
            "is exactly what the epistemic-uncertainty showcase needs from "
            "its training-class flow"),
        "source_kind": "measurement",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 1",
            "The F6b ERCOFTAC results record, including the in-house mesh "
            "verification of the failure",
            "The model-form batch design record",
            "Rapp and Breuer and Froehlich, the periodic hill reattachment "
            "band from the literature"],
        "launch_prompt": (
            "F6b periodic hills, model-form matrix. Read demo-output/website/"
            "SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md section 1 and "
            "demo-output/website/campaign/F6b_ERCOFTAC_RESULTS.md first. "
            "Extend the standing batch (sdk/scripts/model_form_batch.py) "
            "family set to the hills: four closure families on the medium "
            "rung of the in-house verified mesh under demo-output/website/"
            "campaign/F6b_runs/, same settle discipline as the batch's other "
            "cases. Pre-register the three outcomes before the first solve. "
            "Budget 35 core-min total; setsid, poll logs inline. Record: "
            "evidence file in demo-output/website/campaign/, docket update "
            "on this item, honest verdict."),
        "status": "proposed",
        "created_at": NOW,
    },
    {
        "id": "f6b-qcr2000-on-the-hills",
        "well": "W3",
        "objective": (
            "Run the untrained QCR2000 constitutive term forward on the "
            "periodic hills medium rung and rule, under a discriminator "
            "frozen before launch, whether anisotropy moves the "
            "reattachment toward the literature band or leaves the omega "
            "budget implicated"),
        "rationale": (
            "The ducts proved that the QCR2000 term resurrects missing "
            "physics cheaply, and the hills' verified failure is "
            "adverse-pressure-gradient separation, where anisotropy also "
            "matters. The review declared either outcome instructive "
            "before the run: an improvement implicates constitutive form "
            "on the second leg of the two-leg pattern, and no change "
            "implicates the omega budget instead. The failure itself is "
            "already verified onto the model on our own mesh, so whatever "
            "this arm finds lands on the closure and not on the grid."),
        "gate": (
            "One solve on the medium rung of the verified in-house hills "
            "mesh with the QCR2000 quadratic constitutive term active and "
            "nothing else changed. The discriminator is frozen before "
            "launch: a move of reattachment toward the literature band "
            "larger than the ladder's own grid-sensitivity spread "
            "implicates constitutive form and earns anisotropy a place on "
            "the hills; a change within that spread implicates the omega "
            "budget and closes the constitutive route for this leg. Either "
            "verdict is reported as the instructive result the review "
            "declared it to be"),
        "est_core_min": 12,
        "predicted_memory_gb": 2.0,
        "predicted_usd": usd(12),
        "cost_basis": (
            "estimate, the review's figure: one closure solve on the "
            "existing medium rung at the standing settings, priced beside "
            "the recorded cost of the rung it reuses"),
        "expected_knowledge_gain": (
            "A constitutive-form verdict on the second leg of the two-leg "
            "separated-flow pattern, cheap because the mesh and settings "
            "already exist: either anisotropy is the missing physics on "
            "the hills as it was on the ducts, or the omega budget is "
            "named as the place the error lives instead"),
        "source_kind": "gate",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 1",
            "The F6b ERCOFTAC results record, including the in-house mesh "
            "verification of the failure",
            "The QCR duct falsifier record, where the term resurrected the "
            "secondary flow",
            "Spalart, Strategies for turbulence modelling and simulations, "
            "the QCR2000 constitutive relation"],
        "launch_prompt": (
            "F6b periodic hills, QCR2000 arm. Read demo-output/website/"
            "SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md section 1, "
            "demo-output/website/campaign/F6b_ERCOFTAC_RESULTS.md and "
            "demo-output/website/campaign/W3_QCR_DUCT_FALSIFIER.md first. "
            "Copy the medium rung under demo-output/website/campaign/"
            "F6b_runs/, activate the QCR2000 term exactly as the duct run "
            "did, change nothing else, and freeze the discriminator (move "
            "vs the ladder's grid-sensitivity spread) before launch. "
            "Budget 12 core-min; setsid, poll logs inline. Record: "
            "evidence file in demo-output/website/campaign/, docket update "
            "on this item, honest verdict."),
        "status": "approved",
        "created_at": NOW,
        "decided_at": NOW,
        "decision_note": NOTE,
    },
    # ---- review section 2: F6a NASA hump, pass with asterisk ----
    {
        "id": "f6a-hump-qcr-arm-on-the-challenge-run",
        "well": "W1",
        "objective": (
            "Add a QCR2000 arm to the approved NASA hump "
            "challenge-conditions run when it executes, so the two-leg "
            "separated-flow pattern gets the same constitutive probe on "
            "both legs"),
        "rationale": (
            "The hump's bubble-length overprediction is the same family of "
            "failure as the hills', and the model-form matrix at challenge "
            "conditions is already approved on the docket. Attaching one "
            "QCR2000 arm to that run when it executes costs only the "
            "marginal solve, because the mesh and setup are the approved "
            "run's own, and it completes the pattern: whatever the hills "
            "arm finds about anisotropy, the hump answers with the same "
            "probe on the same terms, so the two legs become comparable "
            "instead of merely similar."),
        "gate": (
            "The arm runs only when the approved challenge-conditions run "
            "executes, on that run's mesh and settings, with the QCR2000 "
            "term the single change. Outcome one: the bubble length moves "
            "materially toward the measured reattachment, and the "
            "constitutive finding is compared leg against leg with the "
            "hills arm. Outcome two: no material change, and the "
            "constitutive route is ruled out on this leg too. The "
            "cross-leg comparison is the deliverable, so the arm reports "
            "beside the hills result rather than alone"),
        "est_core_min": 8,
        "predicted_memory_gb": 2.0,
        "predicted_usd": usd(8),
        "cost_basis": (
            "estimate, the review's marginal figure: the arm shares the "
            "approved challenge-conditions run's mesh and setup, so only "
            "one additional closure solve is priced"),
        "expected_knowledge_gain": (
            "The two-leg pattern probed identically on both legs: either "
            "anisotropy repairs separated-region length on hump and hills "
            "alike, which is a constitutive-form finding worth stating "
            "once for the class, or the legs answer differently and the "
            "difference itself localises the mechanism"),
        "source_kind": "gate",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 2",
            "The hump challenge-conditions proposal already approved on "
            "the docket",
            "The F6a epistemic case record, where the reattachment "
            "overprediction stands",
            "Spalart, Strategies for turbulence modelling and simulations, "
            "the QCR2000 constitutive relation"],
        "launch_prompt": (
            "F6a NASA hump, QCR2000 arm. This arm is contingent: it runs "
            "when the approved w1-hump-challenge-conditions run executes, "
            "on its mesh and settings. Read demo-output/website/"
            "SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md section 2 "
            "first. Add one solve with the QCR2000 term active and nothing "
            "else changed, and report the bubble length beside the "
            "baseline arm and beside the hills QCR result. Budget 8 "
            "core-min marginal. Record: evidence in the challenge-run's "
            "own results file, docket update on this item, honest verdict."),
        "status": "proposed",
        "created_at": NOW,
    },
    # ---- review section 3: F8 NREL Phase VI ----
    {
        "id": "f8-bem-torque-bound-at-sequence-s",
        "well": "W1",
        "objective": (
            "Bound what any attached-flow steady solution could deliver "
            "for the NREL Phase VI Sequence S torque at seven metres per "
            "second, by a zero-compute blade-element calculation from the "
            "published S809 polars and the verified chord and twist"),
        "rationale": (
            "The steady branch closed three ways: geometry exonerated to "
            "the millimetre, frame terms audited to source lines, "
            "initialisation tested single-variable, and the motoring limit "
            "cycle persisted through all of it. What no record yet holds "
            "is the hand calculation the case invites: blade-element "
            "torque at Sequence S from published S809 polars and the "
            "chord and twist this lab has already verified against the "
            "reference geometry. That number bounds every attached-flow "
            "steady solution at once. If it lands near the published plus "
            "800 newton metre turbine-signed torque, the limit cycle is "
            "numerical or basin behaviour; if blade-element theory is "
            "itself ambiguous at tip speed ratio 5.4, the case is "
            "intrinsically unsteady and the transient branch stops being "
            "optional."),
        "gate": (
            "The calculation is written down before any comparison: "
            "blade-element torque at Sequence S from published S809 "
            "polars and the verified chord and twist, with its "
            "sensitivity to polar source stated beside it. Outcome one: "
            "the blade-element torque lands near the published plus 800 "
            "newton metre turbine-signed value, so an attached steady "
            "solution exists in principle and the persisting limit cycle "
            "is numerical or basin behaviour. Outcome two: the "
            "blade-element result is itself ambiguous at tip speed ratio "
            "5.4, so the case is intrinsically unsteady and the transient "
            "branch is mandatory. Either way the transient branch "
            "inherits a quantified bound"),
        "est_core_min": 0,
        "predicted_memory_gb": 0.5,
        "predicted_usd": 0.0,
        "cost_basis": (
            "zero compute by construction: a blade-element hand "
            "calculation from published polars and the chord and twist "
            "already verified on the record; no solver is launched"),
        "expected_knowledge_gain": (
            "The cheapest decisive statement available about the F8 "
            "family: whether the steady branch failed because the flow "
            "refuses a steady description or because the solver sits in "
            "the wrong basin, which is exactly the fork the transient "
            "branch needs answered before it spends"),
        "source_kind": "measurement",
        "hard_criterion": "instrument-check",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 3",
            "The F8 record gating the existing MRF blade forces against "
            "Hand and colleagues 2001, including the geometry exoneration",
            "The published S809 airfoil polars",
            "Hand, Simms, Fingersh, Jager, Cotrell, Schreck and Larwood, "
            "the NREL Unsteady Aerodynamics Experiment Phase VI report, "
            "2001"],
        "launch_prompt": (
            "F8 NREL Phase VI, blade-element bound. Zero compute. Read "
            "demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_"
            "2026-08-07.md section 3 and demo-output/website/campaign/"
            "F8_MRF_HAND2001_GATE.md sections 3 and 10 first (the verified "
            "chord, twist and station angles of attack are there). "
            "Pre-register the calculation and its polar source before "
            "computing the number. Compute blade-element torque at "
            "Sequence S, 7 m/s, from published S809 polars plus the "
            "verified chord and twist; state sensitivity to polar choice. "
            "Compare against the plus 800 N-m turbine-signed reference "
            "the gate record carries, with its provenance tier. Record: "
            "evidence file in demo-output/website/campaign/, docket "
            "update on this item, honest verdict."),
        "status": "approved",
        "created_at": NOW,
        "decided_at": NOW,
        "decision_note": NOTE,
    },
    {
        "id": "f8-s10-replay-of-the-mrf-limit-cycle",
        "well": "W7",
        "objective": (
            "Replay rules S10 and S12 of the monitor standard, as "
            "written, against the F8 steady rotor histories that diverged "
            "behind a converged residual, and record whether the standard "
            "catches its newest specimen"),
        "rationale": (
            "The F8 closure produced a real specimen of the failure S10 "
            "was written for: a re-run that diverged while the "
            "convergence reporting read clean, named as such in the gate "
            "record. The standard's own discipline, the archive-replay "
            "rule the charters now enforce, is that a specimen this good "
            "goes to the replay corpus and the rules meet it as written, "
            "with no reinterpretation. The question is narrow and "
            "falsifiable: do S10 and S12, exactly as their clauses stand, "
            "fire on this run's stored histories. The histories already "
            "exist on disk, so the answer costs nothing but the reading."),
        "gate": (
            "The run's stored histories are read against the clauses of "
            "S10 and S12 exactly as written, with no reinterpretation. "
            "Outcome one: a clause fires, and the standard is confirmed "
            "on a specimen from the failure class it was designed for. "
            "Outcome two: nothing fires as written, and the record names "
            "the exact clause that failed to bind, which is the input the "
            "standard's amendment process requires. A miss is a finding "
            "about the standard, not about the run, and is filed as one"),
        "est_core_min": 0,
        "predicted_memory_gb": 0.5,
        "predicted_usd": 0.0,
        "cost_basis": (
            "zero compute: the force and residual histories already exist "
            "on disk and the replay only reads them; nothing is solved"),
        "expected_knowledge_gain": (
            "Either the monitor standard demonstrated working on the "
            "newest real specimen of divergence behind a converged "
            "residual, or the precise clause gap that let the specimen "
            "through, stated in the form the amendment process consumes"),
        "source_kind": "gate",
        "hard_criterion": "instrument-check",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 3",
            "The monitor standard, rules S10 and S12 and the replay "
            "discipline of section 3.1",
            "The F8 record gating the existing MRF blade forces against "
            "Hand and colleagues 2001, where the diverged re-run is "
            "named as the S10 class"],
        "launch_prompt": (
            "F8, monitor-standard replay. Zero compute. Read demo-output/"
            "website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md "
            "section 3, docs/standards/MONITOR_STANDARD.md (S10 clauses "
            "a through c, S12, and the section 3.1 replay pattern), and "
            "demo-output/website/campaign/F8_MRF_HAND2001_GATE.md section "
            "12 first. Apply S10 and S12 verbatim to the stored histories "
            "of the diverged re-run and the limit-cycle runs under "
            "demo-output/website/campaign/F8_runs/. Report per clause: "
            "fires or does not, with the history lines quoted. If nothing "
            "fires, name the clause gap in the amendment-process form. "
            "Record: evidence file in demo-output/website/campaign/, "
            "docket update on this item, honest verdict."),
        "status": "approved",
        "created_at": NOW,
        "decided_at": NOW,
        "decision_note": NOTE,
    },
    # ---- review section 4: B52 ladder noise ----
    {
        "id": "b52-replicate-meshes-at-rung-6",
        "well": "W3",
        "objective": (
            "Build two same-recipe replicate meshes at rung 6 of the B52 "
            "ladder with seed-varied castellation and measure the drag "
            "spread against the measured 1.91e-3 floor, applying the "
            "mesh-draw-sensitivity protocol to its second family"),
        "rationale": (
            "The B52 ladder's verdict answered the family's question: the "
            "increment is noise, 15 percent of the measured 1.91e-3 "
            "floor. The remaining question is the floor's origin, and the "
            "lab already owns the instrument for it: the verdict protocol "
            "for mesh-draw-sensitive credentials, which decides by "
            "replicate meshes rather than by argument. Two same-recipe "
            "meshes at rung 6 with varied seed put the floor to that "
            "test. If the replicates reproduce it, the recipe owns the "
            "floor and castellation is the named mechanism; if they sit "
            "well below it, the floor is iteration-history noise and the "
            "settle gate is the instrument that needs work."),
        "gate": (
            "Two replicate meshes from the identical recipe with varied "
            "seed, solved at the standing settings, the drag spread read "
            "against the 1.91e-3 floor, and the dividing line between "
            "outcomes written into the pre-registration before either "
            "mesh is built. Outcome one: the replicate spread reproduces "
            "the floor, so the recipe owns it and castellation is the "
            "named mechanism. Outcome two: the spread sits well below "
            "the floor, so the floor is iteration-history noise and the "
            "settle gate needs work. Either outcome closes the floor's "
            "origin on evidence"),
        "est_core_min": 14,
        "predicted_memory_gb": 2.0,
        "predicted_usd": usd(14),
        "cost_basis": (
            "estimate, the review's figure: two meshes and two solves at "
            "rung 6, priced beside the measured rung costs the B52 "
            "ladder's own records carry"),
        "expected_knowledge_gain": (
            "The origin of the noise floor that ended the B52 ladder, "
            "assigned either to the meshing recipe or to iteration "
            "history, and a second family measured under the replicate "
            "protocol, which was adopted precisely to be applied beyond "
            "its first case"),
        "source_kind": "measurement",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 4",
            "The B52 rung 8 results record, where the ladder's verdict "
            "and the 1.91e-3 floor are measured",
            "The verdict protocol for mesh-draw-sensitive credentials on "
            "the docket"],
        "launch_prompt": (
            "B52, replicate meshes at rung 6. Read demo-output/website/"
            "SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md section 4 "
            "and demo-output/website/campaign/B52_RUNG8_RESULTS.md first, "
            "then the protocol proposal "
            "w3-a-verdict-protocol-for-mesh-draw-sensitive-credentials on "
            "the docket. Pre-register the dividing line between "
            "recipe-owned and iteration-noise outcomes BEFORE meshing. "
            "Build two rung 6 meshes from the identical snappy recipe "
            "with varied seed, solve at the standing settings with the "
            "settle discipline, and report the Cd spread against the "
            "1.91e-3 floor. Budget 14 core-min; setsid, poll logs "
            "inline. Record: evidence file in demo-output/website/"
            "campaign/, docket update on this item, honest verdict."),
        "status": "proposed",
        "created_at": NOW,
    },
    # ---- review section 5: F5c backward-facing step ----
    {
        "id": "f5c-inlet-development-audit",
        "well": "W1",
        "objective": (
            "Audit the F5c backward-facing step inlet against Driver and "
            "Seegmiller's stated boundary-layer development, verifying "
            "that our inlet reproduces the reference boundary-layer "
            "thickness at the step within the experiment's tolerance, "
            "before any new solve is spent on the case"),
        "rationale": (
            "The F5c record shows converged solves landing a factor of "
            "four to twelve short on reattachment and wandering across "
            "configurations, and the out-of-memory premise that once "
            "excused the case is dead, refuted by our own record. The "
            "classic backward-facing step trap is an inlet that never "
            "develops the boundary layer the experiment had at the step, "
            "and a miss this large smells like it. The reference states "
            "a developed layer of given thickness there. Reading our "
            "inlet and existing fields against that statement costs "
            "nothing, and the review orders it first for exactly that "
            "reason: it is the cheapest hypothesis and it must be "
            "cleared before the unsteady probe spends anything"),
        "gate": (
            "The audit reads our inlet condition and the existing "
            "solution fields and compares boundary-layer thickness at "
            "the step against the value and tolerance the experiment "
            "states. Outcome one: our thickness sits outside the "
            "tolerance, the inlet owns a share of the "
            "factor-of-four-to-twelve failure, and repairing inlet "
            "development precedes all further spending on the case. "
            "Outcome two: our thickness sits inside, the inlet is "
            "exonerated on the record, and the unsteady probe run "
            "becomes the next diagnostic in the declared order"),
        "est_core_min": 0,
        "predicted_memory_gb": 0.5,
        "predicted_usd": 0.0,
        "cost_basis": (
            "zero compute: the audit reads the existing inlet "
            "specification and stored fields against the reference's "
            "stated thickness; no new solve is launched"),
        "expected_knowledge_gain": (
            "Either the mechanism behind the largest unexplained failure "
            "on the campaign record, found for free in the inlet, or a "
            "clean exoneration that licenses the unsteady probe as the "
            "next diagnostic, with the order of spending decided by "
            "evidence rather than appetite"),
        "source_kind": "measurement",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 5",
            "The F5b and F5c unsteady statistics record, where the "
            "factor-of-four-to-twelve reattachment failure is measured",
            "The next-cases slate, item 3, whose diagnosis plan these "
            "diagnostics sharpen",
            "Driver and Seegmiller, Features of a reattaching turbulent "
            "shear layer in divergent channel flow, 1985"],
        "launch_prompt": (
            "F5c backward-facing step, inlet-development audit. Zero "
            "compute. Read demo-output/website/SUPERVISOR_NEGATIVE_"
            "VERDICT_REVIEW_2026-08-07.md section 5, demo-output/website/"
            "campaign/F5bc_unsteady_statistics.md, and item 3 of "
            "demo-output/website/campaign/NEXT_CASES_SLATE.md first. "
            "Pre-register the reference boundary-layer thickness at the "
            "step and the experiment's tolerance BEFORE reading our "
            "fields. Then read the F5c inlet specification and stored "
            "fields under demo-output/website/campaign/F5c_runs/ and "
            "report delta over step height at the step against the "
            "reference. Verdict per the declared tolerance; if the inlet "
            "fails, state the repair before proposing any run. Record: "
            "evidence file in demo-output/website/campaign/, docket "
            "update on this item, honest verdict."),
        "status": "approved",
        "created_at": NOW,
        "decided_at": NOW,
        "decision_note": NOTE,
    },
    {
        "id": "f5c-unsteady-probe-run",
        "well": "W1",
        "objective": (
            "Run one unsteady probe solve of the F5c backward-facing "
            "step, contingent on the inlet audit coming back clean, to "
            "test whether a steady solver on a genuinely unsteady "
            "reattachment region wanders exactly as the record shows"),
        "rationale": (
            "Second diagnostic in the review's cost order, and it runs "
            "only if the inlet audit exonerates the inlet. The recorded "
            "failure is not just magnitude but behaviour: converged "
            "solves whose reattachment wanders across six numerical "
            "configurations, plus a second separation with no "
            "counterpart in the reference. A steady solver applied to a "
            "flow whose reattachment region is genuinely unsteady "
            "wanders in exactly that way, so one unsteady solve "
            "discriminates between a formulation mismatch and a setup "
            "defect that survived the audit."),
        "gate": (
            "Runs only if the inlet audit exonerates the inlet. One "
            "unsteady solve long enough for the reattachment statistics "
            "to distinguish a stationary mean from a wandering one. "
            "Outcome one: the reattachment region is genuinely unsteady "
            "and its time mean lands near the reference, which explains "
            "the steady wandering and reassigns the family to the "
            "unsteady branch. Outcome two: the unsteady mean reproduces "
            "the steady failure, so the defect is in the setup rather "
            "than the formulation, and the audit trail narrows to what "
            "remains. A partial result is reported rather than "
            "overspending, because unsteady cases have overrun this lab "
            "by fifteen to twenty five times before"),
        "est_core_min": 25,
        "predicted_memory_gb": 2.0,
        "predicted_usd": usd(25),
        "cost_basis": (
            "estimate, the review's figure, and stated as one: the lab's "
            "relevant measurement is that unsteady siblings of steady "
            "cases have run fifteen to twenty five times longer at a "
            "Courant-limited step, so the item reports a partial result "
            "rather than spending past the figure"),
        "expected_knowledge_gain": (
            "Whether the backward-facing step failure is a steady "
            "formulation applied to an unsteady flow, which would close "
            "the wandering mystery and reassign the family, or a setup "
            "defect that survives both the inlet audit and the unsteady "
            "probe, which would narrow the remaining suspect list to "
            "something small enough to enumerate"),
        "source_kind": "gate",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 5",
            "The F5b and F5c unsteady statistics record, where the "
            "wandering reattachment is measured",
            "The next-cases slate, item 3",
            "Driver and Seegmiller, Features of a reattaching turbulent "
            "shear layer in divergent channel flow, 1985"],
        "launch_prompt": (
            "F5c backward-facing step, unsteady probe. CONTINGENT: do "
            "not launch until the inlet-development audit "
            "(f5c-inlet-development-audit) has exonerated the inlet on "
            "the record. Read demo-output/website/SUPERVISOR_NEGATIVE_"
            "VERDICT_REVIEW_2026-08-07.md section 5 and demo-output/"
            "website/campaign/F5bc_unsteady_statistics.md first. One "
            "pimpleFoam solve of the existing F5c case at a "
            "Courant-limited step, long enough for reattachment "
            "statistics to separate a stationary mean from a wandering "
            "one; probe wall shear along the bottom wall every step. "
            "Pre-register both outcomes before launch. Budget 25 "
            "core-min and report a partial result rather than spending "
            "past it; setsid, poll logs inline. Record: evidence file "
            "in demo-output/website/campaign/, docket update on this "
            "item, honest verdict."),
        "status": "proposed",
        "created_at": NOW,
    },
    # ---- review section 6: S1, the meta-lesson ----
    {
        "id": "s1-case-integrity-manifest-rule",
        "well": "S1",
        "objective": (
            "Add a case-integrity rule to the standards: any case "
            "directory used as a reference or objective source gets a "
            "manifest of input checksums recorded at validation time, "
            "and any writer to that directory invalidates the badge "
            "until the case is re-validated"),
        "rationale": (
            "The S1 first inversion failed both gates because its "
            "objective was measuring a corrupted inlet: a pilot's "
            "write-back had overwritten reference fields and nothing "
            "existed to notice. The diagnosis is done and the "
            "reinversion is underway; the meta-lesson is the part worth "
            "institutionalising. A checksum manifest recorded when a "
            "case is validated, with the badge invalidated by any "
            "subsequent writer, would have caught the write-back at "
            "cost zero. This is a standards addition, an amendment to "
            "the mesh standard and the verification charter, not a run"),
        "gate": (
            "The rule text lands in the mesh standard and the "
            "verification charter with the manifest fields named, and "
            "the S1 reference directory receives the first manifest. "
            "The falsifier is the motivating case replayed: computing "
            "the manifest on the S1 reference directory as it stood "
            "before the repair must flag the overwritten inlet fields, "
            "at zero solver cost. If the manifest as specified would "
            "not have caught the S1 write-back, the rule is wrong as "
            "written and goes back for redrafting rather than adoption"),
        "est_core_min": 2,
        "predicted_memory_gb": 0.5,
        "predicted_usd": usd(2),
        "cost_basis": (
            "estimate: a standards text amendment plus one checksum "
            "manifest computed over the S1 reference directory; no "
            "solver work anywhere in it"),
        "expected_knowledge_gain": (
            "The class of failure that wasted the first S1 inversion "
            "becomes detectable at cost zero for every future reference "
            "or objective case, and the badge stops asserting an "
            "integrity nobody is checking"),
        "source_kind": "capability",
        "hard_criterion": "instrument-check",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 6",
            "The S1 CBFS inversion result record, where the write-back "
            "and the corrupted objective are diagnosed",
            "The mesh standard",
            "The verification charter"],
        "launch_prompt": (
            "Case-integrity manifest rule. Standards work, not a run. "
            "Read demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_"
            "REVIEW_2026-08-07.md section 6 and demo-output/website/"
            "dafoam/ladder-b/S1_CBFS_INVERSION_RESULT.md first. Draft "
            "the rule into docs/standards/MESH_STANDARD.md and docs/"
            "charters/VERIFICATION_CHARTER.md: manifest of input "
            "checksums at validation time on any directory used as a "
            "reference or objective source; any writer invalidates the "
            "badge until re-validation. Then run the falsifier: compute "
            "the manifest over the S1 reference directory pre-repair "
            "state and show it flags the overwritten inlet fields. If "
            "it would not have caught the write-back, redraft instead "
            "of adopting. Record: the amended standards, evidence note "
            "beside the S1 record, docket update on this item."),
        "status": "proposed",
        "created_at": NOW,
    },
    # ---- review section 7: alpha_05 regime model ----
    {
        "id": "r5-alpha05-weighted-loss-variant",
        "well": "W5",
        "objective": (
            "Train a spatially weighted loss variant of the declined "
            "regime correction on the same split, offline and "
            "validation-only, weighting by local truth magnitude or by "
            "the metric's own point density, to test whether the error "
            "relocation was an artifact of equal-weight training"),
        "rationale": (
            "The regime model went NO-GO on its own pre-registered cap: "
            "the boundary moved instead of vanishing, which is the "
            "recorded mechanism finding, and the census showed the "
            "correction relocating error into the strip the metric "
            "weights least. That leaves one cheap, well-posed question: "
            "is the relocation a property of the correction or of the "
            "equal-weight loss it was trained under. A variant weighted "
            "by local truth magnitude or by the metric's own point "
            "density, trained on the same split with nothing else "
            "changed, answers it offline. Its pre-registration must "
            "state the same hurt-cap discipline that killed the "
            "predecessor, so a GO cannot be manufactured by weakening "
            "the rule that produced the NO-GO"),
        "gate": (
            "Pre-registered before training, carrying the same hurt-cap "
            "discipline that produced the predecessor's NO-GO. Outcome "
            "one: the weighted variant stops relocating error into the "
            "metric's weakly sampled strip on the validation split, so "
            "the relocation was an artifact of equal-weight training "
            "and a successor candidate has a stated mechanism. Outcome "
            "two: the relocation persists under weighting, so it is "
            "structural to the correction and the regime route stays "
            "closed on evidence. No test case is opened and no scoring "
            "call is made; the work is validation-only by construction"),
        "est_core_min": 0,
        "predicted_memory_gb": 0.5,
        "predicted_usd": 0.0,
        "cost_basis": (
            "zero solver core-minutes, the review's own costing: "
            "offline fitting of the sklearn class on data already on "
            "disk, and the predecessor's measured cost was about two "
            "core-minutes of wall at a two-core cap, which is the "
            "scale expected here"),
        "expected_knowledge_gain": (
            "Whether the error relocation that ended the regime route "
            "belongs to the correction or to its training loss, which "
            "is the difference between a closed road and a mislabelled "
            "one, bought without opening a test case or launching a "
            "solver"),
        "source_kind": "challenge",
        "hard_criterion": "no-case",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 7",
            "The R5 regime-model pre-registration, whose section 4 "
            "records the NO-GO on the pre-declared cap",
            "The product list, where the mechanism finding on the "
            "moving boundary is recorded",
            "The closure evaluation protocol, where the census locates "
            "the relocated error"],
        "launch_prompt": (
            "Alpha 05 regime route, weighted-loss variant. Offline, "
            "validation-only, no test case opened, open() guard armed "
            "as the predecessor had it. Read demo-output/website/"
            "SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md section 7 "
            "and demo-output/website/closure_challenge_R5_ALPHA05_"
            "REGIME_PREREGISTRATION.md first. Pre-register BEFORE "
            "training: the weighting (local truth magnitude, and "
            "separately the metric's own point density), the identical "
            "split, and the identical hurt-cap discipline that produced "
            "the predecessor's NO-GO. Train, then report relocation on "
            "the validation split beside the equal-weight predecessor. "
            "Record: evidence file beside the R5 records, docket update "
            "on this item, honest verdict."),
        "status": "proposed",
        "created_at": NOW,
    },
    # ---- review section 8: A3 ONERA M6 adjoint ----
    {
        "id": "a3-m6-vcoarse-adjoint-sub-lu-arm",
        "well": "W4",
        "objective": (
            "Run one arm of the ONERA M6 vcoarse adjoint with the "
            "sub-preconditioner set to LU together with the liaison's "
            "transonic preconditioner lead, neither of which has ever "
            "been set on our M6 runs, to learn whether the conditioning "
            "block that predates the sub-LU tool still stands"),
        "rationale": (
            "A3 closed as blocked: adjoint breakdown at every mesh size "
            "tested, regardless of memory headroom. But the block "
            "predates the sub-LU unblock that later cleared the "
            "incompressible family, and that unblock was never carried "
            "to M6; separately, the liaison's research found the "
            "official transonic tutorial setting a transonic "
            "preconditioner option our M6 records never set. That is a "
            "gap, not a verdict, and one arm on the cheapest mesh "
            "closes it either way: convergence reopens the A3 ladder "
            "and gives the breakdown story its epilogue, and a second "
            "breakdown confirms the conditioning wall beyond the "
            "incompressible family with both known unblocks tested"),
        "gate": (
            "One adjoint solve on the vcoarse M6 mesh with the "
            "sub-preconditioner set to LU and the transonic "
            "preconditioner option set as the official transonic "
            "tutorial sets it, nothing else changed from the archived "
            "arm. Outcome one: the adjoint converges, the A3 ladder "
            "reopens, and the breakdown record gains an epilogue naming "
            "the settings that were missing. Outcome two: the adjoint "
            "breaks down again, and the conditioning wall is confirmed "
            "beyond the incompressible family, with both known unblocks "
            "on the record as tested and insufficient"),
        "est_core_min": 30,
        "predicted_memory_gb": 6.0,
        "predicted_usd": usd(30),
        "cost_basis": (
            "estimate, the review's figure: the vcoarse M6 adjoint has "
            "run before and failed by breakdown rather than by "
            "walltime, and the two settings change conditioning rather "
            "than problem size, so the archived arm's spend is the "
            "anchor"),
        "expected_knowledge_gain": (
            "Either the A3 ladder reopened by a setting that already "
            "existed, which converts a blocked family into a running "
            "one for the cost of a single arm, or the conditioning "
            "wall confirmed as real beyond the incompressible family, "
            "which is the epilogue the breakdown record currently "
            "lacks"),
        "source_kind": "gate",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 8",
            "The DAFoam adjoint memory envelope record, where breakdown "
            "at every M6 point is measured",
            "The liaison research record on adjoint conditioning, lead "
            "1.5, the transonic preconditioner option",
            "The CBFS unblock verification sweep, where the sub-LU "
            "setting cleared the incompressible family"],
        "launch_prompt": (
            "A3 ONERA M6, sub-LU plus transonic preconditioner arm. "
            "Read demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_"
            "REVIEW_2026-08-07.md section 8, demo-output/website/"
            "dafoam/ADJOINT_MEMORY_ENVELOPE.md, and lead 1.5 of "
            "demo-output/website/dafoam/LIAISON_RESEARCH_adjoint_"
            "conditioning.md first. One arm: the archived vcoarse M6 "
            "adjoint case with DAFOAM_SUBPC_TYPE=lu and "
            "transonicPCOption set as the official transonic NACA0012 "
            "tutorial sets it, nothing else changed. Pre-register both "
            "outcomes before launch. Budget 30 core-min; dispatch as a "
            "solver agent, setsid, poll logs inline. Record: evidence "
            "file in demo-output/website/dafoam/, docket update on "
            "this item, honest verdict."),
        "status": "approved",
        "created_at": NOW,
        "decided_at": NOW,
        "decision_note": NOTE,
    },
    # ---- review section 9: model-form family B ----
    {
        "id": "modelform-family-b-bump-diagnosis-arm",
        "well": "W3",
        "objective": (
            "Run one diagnosis arm of model-form family B, the bump at "
            "a doubled iteration cap with per-quantity settle "
            "tracking, to decide slow-but-convergent against genuinely "
            "stalled, which decides whether family B gets a band or a "
            "documented exclusion"),
        "rationale": (
            "Family B produced no band: all four closures stalled, and "
            "the archived rung never met its residual criterion "
            "either, so the family's absence from the band rests on "
            "runs that never finished deciding. One arm at double the "
            "archived cap, with each quantity's settle state tracked "
            "separately, separates the two readings. Slow but "
            "convergent means the family re-enters the band with a "
            "stated cap; genuinely stalled means the family receives a "
            "documented exclusion instead of a silent hole. Either "
            "way the band's coverage statement becomes honest"),
        "gate": (
            "One closure from the family at double the archived "
            "iteration cap, with the cap and the per-quantity settle "
            "criteria declared before the run. Outcome one: the "
            "quantities settle and the residual criterion is met, so "
            "the family is slow but convergent, the archived verdict "
            "is revised to under-iterated, and family B re-enters the "
            "band with its cap stated. Outcome two: the histories "
            "plateau at the doubled cap, so the family is genuinely "
            "stalled and receives a documented exclusion. Both "
            "outcomes are written into the band's coverage statement"),
        "est_core_min": 15,
        "predicted_memory_gb": 2.0,
        "predicted_usd": usd(15),
        "cost_basis": (
            "estimate, the review's figure: one closure at twice the "
            "archived rung's iteration cap, about twice the archived "
            "rung's recorded spend"),
        "expected_knowledge_gain": (
            "Whether family B belongs in the model-form band or in a "
            "documented exclusion, decided by measurement instead of "
            "by the ambiguity of runs that stopped on a backstop, "
            "which makes the band's coverage claim honest either way"),
        "source_kind": "gate",
        "hard_criterion": "instrument-check",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 9",
            "The model-form band record, where family B's four stalled "
            "closures are logged",
            "The model-form batch design record"],
        "launch_prompt": (
            "Model-form family B, bump diagnosis arm. Read demo-output/"
            "website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md "
            "section 9 and demo-output/website/campaign/MODEL_FORM_"
            "BAND.md first. Pick one closure from family B, double the "
            "archived iteration cap, and declare the cap and "
            "per-quantity settle criteria BEFORE launch. Solve with "
            "the settle watcher discipline (setsid; beware the "
            "coefficient-file rename on restart). Verdict: slow but "
            "convergent, or genuinely stalled, per the declared "
            "criteria; update the band's coverage statement "
            "accordingly. Budget 15 core-min. Record: evidence file "
            "in demo-output/website/campaign/, docket update on this "
            "item, honest verdict."),
        "status": "proposed",
        "created_at": NOW,
    },
    # ---- review section 10: TMR NACA 0012 generator pathology ----
    {
        "id": "tmr-naca0012-alternative-generator-mesh",
        "well": "W6",
        "objective": (
            "Build one TMR NACA 0012 mesh at matched cell count from "
            "an alternative generator, a C-grid per the resource "
            "recipe or an unstructured equivalent, and rerun the "
            "ladder point to learn whether the aspect-ratio pathology "
            "under refinement belongs to the generator"),
        "rationale": (
            "The standing finding attributes the NACA 0012 "
            "aspect-ratio pathology under refinement to the mesh "
            "generator, and the family is blocked on it. A finding "
            "that convicts a tool owes the tool a control: one mesh "
            "at matched cell count from a different generator, run "
            "at the standing settings, decides ownership. If the "
            "ladder behaves on the alternative mesh, the generator "
            "owns the pathology and the family unblocks on the new "
            "generator; if the pathology reproduces, the conviction "
            "was wrong and the finding is corrected on the record"),
        "gate": (
            "One mesh at matched cell count from a different "
            "generator, solved at the standing settings and read "
            "against the same ladder criteria as the blocked family. "
            "Outcome one: the ladder behaves on the alternative mesh, "
            "the generator owns the pathology, the standing finding "
            "is confirmed by its own control, and the NACA 0012 "
            "family unblocks on the new generator. Outcome two: the "
            "pathology reproduces at matched cell count, ownership "
            "moves off the generator, and the standing finding is "
            "corrected rather than left convicting the wrong tool"),
        "est_core_min": 20,
        "predicted_memory_gb": 2.0,
        "predicted_usd": usd(20),
        "cost_basis": (
            "estimate, the review's figure: one mesh build and one "
            "solve at a cell count matched to the blocked ladder "
            "point, priced beside that point's recorded spend"),
        "expected_knowledge_gain": (
            "The generator conviction tested by the control it never "
            "had: either the NACA 0012 family unblocks on an "
            "alternative generator, or the standing finding is "
            "corrected before it misdirects any more work"),
        "source_kind": "gate",
        "hard_criterion": "existing-family",
        "citations": [
            "The supervisor review of standing negative verdicts, "
            "2026-08-07, section 10",
            "The standing generator finding on aspect-ratio growth "
            "under refinement",
            "The TMR mesh aspect-ratio record of the 4G campaign",
            "The NASA Turbulence Modeling Resource verification cases "
            "and their grid recipes"],
        "launch_prompt": (
            "TMR NACA 0012, alternative-generator control. Read "
            "demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_"
            "2026-08-07.md section 10, demo-output/website/dafoam/"
            "GENERATOR_FINDING_pyhyp_aspect_ratio.md, and demo-output/"
            "website/campaign/4G_tmr_mesh_aspect_ratio.md first. Build "
            "one mesh at a cell count matched to the blocked ladder "
            "point: blockMesh C-grid per the TMR recipe, or gmsh if "
            "the C-grid cannot be matched. Verify the aspect-ratio "
            "profile of the new mesh BEFORE solving, then solve at "
            "the standing settings and grade against the same ladder "
            "criteria. Pre-register both outcomes. Budget 20 "
            "core-min; setsid, poll logs inline. Record: evidence "
            "file beside the generator finding, docket update on "
            "this item, honest verdict."),
        "status": "proposed",
        "created_at": NOW,
    },
]


def main() -> int:
    docket = json.loads(DOCKET.read_text(encoding="utf-8"))
    have_ids = {p["id"] for p in docket["proposals"]}
    have_obj = {agenda.normalize_objective(p.get("objective", ""))
                for p in docket["proposals"]}
    inbox_ids = {p.stem for p in INBOX.glob("*.json")}

    failures = []
    for p in NEW:
        if p["id"] in have_ids or p["id"] in inbox_ids:
            failures.append((p["id"], ["id collision"]))
        if agenda.normalize_objective(p["objective"]) in have_obj:
            failures.append((p["id"], ["objective collision"]))
        v = agenda.proposal_violations(p)
        if v:
            failures.append((p["id"], v))
    if failures:
        for i, v in failures:
            print(f"  REFUSED {i}: {v}")
        return 1

    for p in NEW:
        adv = agenda.premise_violations(p, repo=REPO)
        if adv:
            print(f"  advisory {p['id']}: {adv}")

    # write the inbox files, then prove ingestion keeps all of them
    for p in NEW:
        (INBOX / f"{p['id']}.json").write_text(
            json.dumps(p, indent=1) + "\n", encoding="utf-8")
    ingested = {p["id"] for p in agenda.read_inbox()}
    dropped = [p["id"] for p in NEW if p["id"] not in ingested]
    if dropped:
        print(f"  DROPPED at inbox ingestion: {dropped}")
        return 1

    docket["proposals"].extend(NEW)
    docket["generated_at"] = NOW
    DOCKET.write_text(json.dumps(docket, indent=1), encoding="utf-8")
    for p in NEW:
        print(f"  + {p['id']}  {p['status']:9s} {p['est_core_min']:>3} "
              f"core-min  {p['source_kind']}/{p['hard_criterion']}")
    print(f"  docket now {len(docket['proposals'])}, intake rails clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
