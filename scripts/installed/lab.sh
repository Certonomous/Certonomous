#!/usr/bin/env bash
# One-command lab session: ./lab.sh  (attaches if it already exists)
# Windows: server (GUI server lives here), batch (long solves), spare.
SESSION=lab
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session  -d -s "$SESSION" -n server -c "$HOME/Certonomous"
    tmux new-window   -t "$SESSION" -n batch  -c "$HOME/Certonomous"
    tmux new-window   -t "$SESSION" -n spare  -c "$HOME"
    # Pre-type (not run) the GUI server command in the server window.
    # NOTE: check nothing else owns :8765 first (REUSEADDR trap) —
    #   ss -ltnp | grep 8765
    tmux send-keys -t "$SESSION:server" \
        "cd ~/Certonomous && python3 sdk/chief_engineer/server.py"
    tmux select-window -t "$SESSION:server"
fi
exec tmux attach -t "$SESSION"
