#!/bin/bash
# F6d campaign driver.  Sequential stages, bounded concurrency inside each.
set -u
cd "$(dirname "$0")"
echo "START $(date -u)"
python3 build_ensemble.py --null      --concurrency 1  && echo "NULL done $(date -u)"
python3 build_ensemble.py --corners   --concurrency 3  && echo "CORNERS done $(date -u)"
python3 build_signdemo.py                              && echo "SIGNDEMO done $(date -u)"
python3 build_ensemble.py --delta 0.2 --n 40 --seed 20260730 --concurrency 6 && echo "D02 done $(date -u)"
python3 build_ensemble.py --delta 0.6 --n 40 --seed 20260731 --concurrency 6 && echo "D06 done $(date -u)"
echo "ALL done $(date -u)"
