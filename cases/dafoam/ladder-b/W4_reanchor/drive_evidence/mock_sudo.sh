#!/usr/bin/env bash
# MOCK `sudo` for the W4-reanchor production drive. Intercepts the ONLY three sudo
# calls the real drivers make -- `sudo docker run`, `sudo docker rm -f`, `sudo chown`
# -- so the drivers run end to end with NO real container and NO privilege. It is on
# PATH ahead of the real sudo for the duration of the drive only.
MOCK_SOLVER="$(dirname "$(readlink -f "$0")")/mock_solver.py"
cmd="$1"; shift
case "$cmd" in
  docker)
    sub="$1"; shift
    case "$sub" in
      run) exec python3 "$MOCK_SOLVER" "$@" ;;
      rm)  exit 0 ;;   # container reap: no-op, no container ever existed
      *)   exit 0 ;;
    esac ;;
  chown) exit 0 ;;      # sandbox is already owned by the invoking user
  *) echo "mock sudo: unhandled command: $cmd" >&2; exit 0 ;;
esac
