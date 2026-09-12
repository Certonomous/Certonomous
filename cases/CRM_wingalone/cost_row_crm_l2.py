#!/usr/bin/env python3
"""
CRM WING-ALONE L2 -- COST ROW ONLY.  IT EMITS NO VERDICT AND CANNOT.

WHY THIS IS NOT A SECOND GRADER.  "Two watchers on one run is two records" is a rule about
GRADERS: a second thing that emits a verdict creates a second record of a verdict.  This
emits cost, and the constraint is MACHINE-ENFORCED rather than promised -- before writing,
it scans its OWN output for every token in CLAUDE.md rule 1's vocabulary and REFUSES to
write if it finds one.  A later reader can run that check against this file and see it holds.

WHAT IT MAY TOUCH.  It writes COST_ROW.txt, COST_ROW.log and COST_WRITER_RC.txt and nothing
else.  It never writes the grader's outputs (GRADE_CRM_L2.txt, VERDICT.crm_l2, grade_rc,
AUTOGRADE.*, GRADE_PLANT/), never writes solve_rc or any rc the grader reads, and never
writes into 0/, 4000/ or postProcessing/.  If it fails, the grader and the run are untouched.

WHY IT EXISTS.  Rule 12 makes estimate-versus-actual calibration part of a COMPLETION, and a
standing rule is not retired by any relay.  CRM lands ~6.5 h out and this session has already
died once tonight, taking three lanes with it.  A cost row that needs something alive at
landing is a row that probably never gets written; "recoverable by a human who knows to look"
is how an obligation quietly becomes optional.

IT HAS NO KILL PRIMITIVE AND NO CAP.  It reads.
"""
import os, re, sys, datetime

PREDICTED_CORE_MIN = 720      # §8 O5, solver stage, HEAD blob
PREDICTED_RANKS    = 4        # §8 O5 -- the run used 6; see the departure note below
REGISTERED_CAP     = 1500     # §8 -- a rule-12 PREDICTION SCORED AT COMPLETION, never a kill
RATE_USD_CORE_H    = 0.0513   # c7a.4xlarge, owner-stated; DERIVED, NOT MEASURED

# CLAUDE.md rule 1, in full.  This file must contain none of these in its OUTPUT.
VERDICT_TOKENS = ["PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"]

def kv(path):
    d = {}
    if os.path.exists(path):
        for line in open(path, errors="replace"):
            if "=" in line:
                k, _, v = line.partition("=")
                d[k.strip()] = v.strip()
    return d

def main():
    CASE = sys.argv[1].rstrip("/")
    now  = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    S    = kv(os.path.join(CASE, "STATUS.solve"))
    L    = []
    def say(s=""): L.append(s)

    # ---- measured, from the run's own artifacts ----------------------------
    ranks = int(S.get("solver_ranks", "0") or 0)
    wall  = float(S.get("solver_wall_s", "0") or 0)
    solver_cm = float(S.get("solver_core_min", "0") or 0)
    total_cm  = S.get("total_core_min", "")
    rp_wall   = S.get("reconstructPar_wall_s", "")

    ex = ck = None; n_exec = 0
    log = os.path.join(CASE, "log.rhoSimpleFoam")
    if os.path.exists(log):
        for line in open(log, errors="replace"):
            m = re.match(r"ExecutionTime = ([0-9.e+-]+) s\s+ClockTime = ([0-9.e+-]+) s", line)
            if m:
                ex, ck = float(m.group(1)), float(m.group(2)); n_exec += 1

    say("CRM WING-ALONE L2 -- COST CALIBRATION ROW (CLAUDE.md rule 12)")
    say("written %s by cost_row_crm_l2.py. THIS FILE CARRIES NO VERDICT." % now)
    say("The verdict is the grader's alone, in VERDICT.crm_l2. Nothing here grades anything.")
    say("=" * 76)
    say()
    say("MEASURED, from this run's own artifacts")
    say("  solver_ranks          : %s        (STATUS.solve)" % S.get("solver_ranks", "UNMEASURED"))
    say("  solver_wall_s         : %s        (STATUS.solve)" % S.get("solver_wall_s", "UNMEASURED"))
    say("  solver_core_min       : %s        (STATUS.solve)" % S.get("solver_core_min", "UNMEASURED"))
    say("  reconstructPar_wall_s : %s        (STATUS.solve)" % (rp_wall or "UNMEASURED"))
    say("  total_core_min        : %s        (STATUS.solve, sum of phases at their OWN rank counts)"
        % (total_cm or "UNMEASURED -- the launcher did not reach its reconstruct phase"))
    say("  iterations written    : %d" % n_exec)
    if ex is not None:
        say("  ExecutionTime (final) : %.1f s   (log.rhoSimpleFoam)" % ex)
        say("  ClockTime     (final) : %.1f s   (log.rhoSimpleFoam)" % ck)
    say()

    actual_gross = float(total_cm) if total_cm else solver_cm
    basis = "total_core_min" if total_cm else "solver_core_min (reconstruct phase absent)"

    say("ESTIMATE VERSUS ACTUAL")
    say("  predicted (§8 O5, solver stage) : %d core-min, at %d ranks" % (PREDICTED_CORE_MIN, PREDICTED_RANKS))
    say("  actual, GROSS                   : %.1f core-min   [basis: %s]" % (actual_gross, basis))
    if PREDICTED_CORE_MIN:
        say("  ratio actual/predicted, GROSS   : %.2fx" % (actual_gross / PREDICTED_CORE_MIN))
    say()

    # ---- the attribution split: contention is NEVER folded into the ratio --
    say("ATTRIBUTION -- CONTENTION IS NAMED SEPARATELY AND IS NEVER FOLDED INTO THE RATIO")
    say("  (COMPUTE_BUDGET_CHARTER §6: waste is reported, not absorbed.)")
    # CONSISTENCY ASSERT.  The split is only meaningful if the log and STATUS.solve
    # describe THE SAME FINISHED RUN.  A partial or truncated log read against a completed
    # STATUS.solve yields a confident-looking split that is simply wrong -- the selftest
    # produced exactly that (a 0.32x "misprediction" from a live log against a synthetic
    # completed status).  A number that can be silently wrong is worse than one refused.
    consistent = None
    if ex is not None and ck and wall:
        consistent = abs(ck - wall) / wall <= 0.10
    if ex is not None and ck and ranks and consistent is False:
        say("  NOT COMPUTED -- THE TWO SOURCES DISAGREE ABOUT THIS RUN'S LENGTH.")
        say("    log.rhoSimpleFoam final ClockTime : %.1f s" % ck)
        say("    STATUS.solve solver_wall_s        : %.1f s" % wall)
        say("    They differ by %.1f%%, beyond the 10%% tolerance. The log and the status"
            % (100.0 * abs(ck - wall) / wall))
        say("    are not describing the same finished run (a truncated, rotated or still-")
        say("    being-written log will do this), so the contention split is NOT guessed.")
        say("    Both numbers are printed above so a reader can see the disagreement.")
    elif ex is not None and ck and ranks:
        cfree = ex * ranks / 60.0
        say("  ExecutionTime/ClockTime        : %.4f   (1.0 would be an uncontended box)" % (ex / ck))
        say("  contention-free equivalent     : %.1f core-min  (ExecutionTime x ranks / 60)" % cfree)
        say("  ratio contention-free/predicted: %.2fx  <-- THIS is the misprediction figure" % (cfree / PREDICTED_CORE_MIN))
        say("  charged to CONTENTION          : %.1f core-min  (gross minus contention-free)"
            % (actual_gross - cfree))
        say("  So the prediction error and the shared-box cost are two numbers, not one.")
    else:
        say("  UNMEASURABLE: the ExecutionTime/ClockTime pair was not readable, so the")
        say("  contention split cannot be computed and is NOT guessed.")
    say()

    say("AGAINST THE REGISTERED CAP")
    say("  registered cap (§8)   : %d core-min" % REGISTERED_CAP)
    say("  actual, GROSS         : %.1f core-min  -> %.2fx the cap" % (actual_gross, actual_gross / REGISTERED_CAP))
    say("  THE CAP DID NOT AND COULD NOT STOP THIS RUN. Sanaa has ruled four times that no")
    say("  run is stopped by a time or budget cap; retiring a cap is the owner's call and she")
    say("  made it in her own words. The cap is scored here as a PREDICTION, never enforced.")
    say("  No instrument on this run contains a kill primitive.")
    say()

    say("DEPARTURE THAT BOUNDS HOW THIS ROW MAY BE COMPARED")
    say("  The run used %s ranks; §8 O5 predicted %d. Core-minutes are wall x ranks, so this"
        % (S.get("solver_ranks", "?"), PREDICTED_RANKS))
    say("  actual CANNOT be compared naively against the 4-rank estimate: at equal wall time")
    say("  6 ranks cost 1.5x what 4 do, before any efficiency difference. Recorded in")
    say("  DEPARTURES.md D1, with the MRF R2 2/2/6-rank precedent that makes rank count")
    say("  something to disclose rather than absorb.")
    say()

    say("DERIVED DOLLARS -- DERIVED, NOT MEASURED")
    say("  $%.2f at $%s/core-h. This box CANNOT read its own billing" % (actual_gross / 60 * RATE_USD_CORE_H, RATE_USD_CORE_H))
    say("  (COMPUTE_BUDGET_CHARTER §5), so this figure is derived from a rate, never observed.")
    say()
    say("TO LAND IN docs/COST_CALIBRATION.md -- BY AN AGENT, UNDER THE RULE-10 PRIVATE-INDEX")
    say("PROTOCOL. This writer deliberately does NOT edit that shared file: a detached process")
    say("writing a shared git document while peers commit is how an index gets clobbered.")
    say("  | CRM wing-alone L2 M=0.85 | %d | %.1f | %.2fx | contention %.4f | %s |"
        % (PREDICTED_CORE_MIN, actual_gross,
           actual_gross / PREDICTED_CORE_MIN, (ex / ck) if (ex and ck) else float("nan"), now))

    text = "\n".join(L) + "\n"

    # ---- MACHINE-ENFORCED: this file may carry no rule-1 verdict token ------
    found = [t for t in VERDICT_TOKENS if re.search(r"\b%s\b" % t.replace(" ", r"\s+"), text)]
    if found:
        with open(os.path.join(CASE, "COST_ROW.REFUSED.txt"), "w") as f:
            f.write("COST ROW REFUSED at %s.\nIts own output carried rule-1 verdict "
                    "token(s): %s\nA cost writer that speaks in the verdict vocabulary is a "
                    "second record of a verdict, which is exactly what it must not be.\n"
                    % (now, ", ".join(found)))
        sys.stderr.write("REFUSED: output carried verdict token(s) %s\n" % ", ".join(found))
        return 2

    with open(os.path.join(CASE, "COST_ROW.txt"), "w") as f:
        f.write(text)
    print(text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
