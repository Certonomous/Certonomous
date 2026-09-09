#!/bin/bash
# SUP_BOOSTER E1 DETACHED AUTOGRADER (rule-10 committed; §2ba).
#
# Fires the PINNED grader (grade_sup_booster.py, blob 3c8d418a) against the three graded
# levels once they exist, against the FROZEN regenerated reference JSON (blob c442a94b). The
# grader itself enforces rule-4 completion (refuses exit 2 if a level is incomplete / a level
# is not iteratively plateaued at endTime -> NOT A RESULT) and the rule-3 planted-zero
# control; it is NOT re-implemented here. Writes the verdict JSON. Sends nothing (rules 7,16).
set -u
REPO=/home/ubuntu/Certonomous
RUN=$REPO/verification/runs/navier_class/SUP_BOOSTER/graded
REF=$REPO/verification/runs/navier_class/SUP_BOOSTER/tm_reference_M2p0_tc15.json
GRADER=$REPO/verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster.py
source /usr/lib/openfoam/openfoam2606/etc/bashrc 2>/dev/null

python3 "$GRADER" \
    --coarse "$RUN/coarse" --medium "$RUN/medium" --fine "$RUN/fine" \
    --reference "$REF" --report "$RUN/VERDICT.json" > "$RUN/verdict_stdout.txt" 2>&1
echo $? > "$RUN/rc.autograde"
