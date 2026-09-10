#!/bin/bash
# SUP_BOOSTER **E2** DETACHED AUTOGRADER (rule-10 committed; section 2ba).
#
# Fires the PINNED E2 grader (grade_sup_booster_e2.py) against the three E2 graded levels under
# the REGISTERED E2 run root graded_e2/, against the FROZEN regenerated reference JSON
# (blob c442a94b, unchanged from E1). It touches E1's root `graded/` nowhere.
#
# The grader itself enforces rule-4 completion (refuse exit 2 if a level is incomplete, NOT A
# RESULT if a level is not iteratively plateaued at endTime), the rule-3 planted-zero control,
# C1's Roache/Celik gate and C2's value-in-band + consistency gate under ruling 0e9c1bcb.
# None of that is re-implemented here. Writes the verdict JSON. Sends nothing (rules 7, 16).
# source OpenFOAM BEFORE `set -u` (its bashrc references unset vars -> would abort under nounset)
source /usr/lib/openfoam/openfoam2606/etc/bashrc 2>/dev/null
set -u
REPO=/home/ubuntu/Certonomous
RUN=$REPO/verification/runs/navier_class/SUP_BOOSTER/graded_e2
REF=$REPO/verification/runs/navier_class/SUP_BOOSTER/tm_reference_M2p0_tc15.json
GRADER=$REPO/verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster_e2.py

# Refuse rather than degrade -- this wrapper previously had NO input guard, so a missing grader
# or reference would have reached rc.autograde as a bare python3 exit code indistinguishable from
# the grader's own refusal (exit 2). (Launcher exercise 2026-09-10.)
case "$RUN" in *graded_e2) : ;; *) echo "REFUSE: run root is not graded_e2: $RUN" >&2; exit 2;; esac
[ -d "$RUN" ] || { echo "REFUSE: run root missing: $RUN" >&2; exit 2; }
for f in "$GRADER" "$REF" "$RUN/coarse" "$RUN/medium" "$RUN/fine"; do
    [ -e "$f" ] || { echo "REFUSE: pinned input missing: $f" >&2; echo 2 > "$RUN/rc.autograde"; exit 2; }
done

python3 "$GRADER" \
    --coarse "$RUN/coarse" --medium "$RUN/medium" --fine "$RUN/fine" \
    --reference "$REF" --report "$RUN/VERDICT.json" > "$RUN/verdict_stdout.txt" 2>&1
echo $? > "$RUN/rc.autograde"
