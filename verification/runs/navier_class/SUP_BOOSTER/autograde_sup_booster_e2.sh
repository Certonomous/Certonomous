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

python3 "$GRADER" \
    --coarse "$RUN/coarse" --medium "$RUN/medium" --fine "$RUN/fine" \
    --reference "$REF" --report "$RUN/VERDICT.json" > "$RUN/verdict_stdout.txt" 2>&1
echo $? > "$RUN/rc.autograde"
