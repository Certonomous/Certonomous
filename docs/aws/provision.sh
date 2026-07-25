#!/usr/bin/env bash
# Certonomous lab provisioning - Ubuntu 24.04 on EC2 (c7a.8xlarge class).
# Run as the default ubuntu user:  bash provision.sh
# Idempotent where practical; each phase prints what it did.
set -euo pipefail

echo "== Phase 1: base tooling =="
sudo apt-get update -y
sudo apt-get install -y build-essential git tmux curl unzip rsync \
    python3.12 python3.12-venv python3-pip python-is-python3 \
    nodejs npm libgl1 libxrender1 libosmesa6

echo "== Phase 2: OpenFOAM v2606 (native, no WSL layer) =="
curl -fsSL https://dl.openfoam.com/add-debian-repo.sh | sudo bash
sudo apt-get install -y openfoam2606-default
# The lab invokes tools through the 'openfoam2606' wrapper; the package
# provides /usr/bin/openfoam2606 which matches the launcher convention.

echo "== Phase 3: OpenVSP / VSPAERO =="
# Release tarball into /opt/OpenVSP (vspaero.available() checks this path,
# so no OPENVSP_RUN_PREFIX is needed on native Linux).
OPENVSP_VER="3.41.1"
if [ ! -x /opt/OpenVSP/vspaero ]; then
  cd /tmp
  curl -fsSL -o openvsp.zip \
    "https://openvsp.org/download.php?file=OpenVSP-${OPENVSP_VER}-Ubuntu-24.04.zip" \
    || echo "NOTE: fetch the Ubuntu release zip from openvsp.org manually if this 404s"
  sudo mkdir -p /opt/OpenVSP && sudo unzip -o openvsp.zip -d /opt/OpenVSP \
    && sudo find /opt/OpenVSP -maxdepth 2 -name vspaero -exec ln -sf {} /opt/OpenVSP/vspaero \;
fi

echo "== Phase 4: Python environment =="
python3.12 -m pip install --break-system-packages --upgrade pip
python3.12 -m pip install --break-system-packages \
    numpy scipy matplotlib pyyaml anthropic pypdf

echo "== Phase 5: Claude Code =="
curl -fsSL https://claude.ai/install.sh | bash || sudo npm install -g @anthropic-ai/claude-code

echo "== Phase 6: repo =="
if [ ! -d "$HOME/Certonomous" ]; then
  echo "Clone manually with your GitHub auth:  git clone git@github.com:<you>/Certonomous.git ~/Certonomous"
fi

echo "== Phase 7: environment (append to ~/.bashrc) =="
grep -q CERTONOMOUS_SOLVE_RANKS ~/.bashrc || cat >> ~/.bashrc <<'ENV'
# Certonomous lab environment (native Linux: no WSL prefixes needed)
export CERTONOMOUS_SOLVE_RANKS=16
export OPENFOAM_RUN_PREFIX="openfoam2606"
export CHIEF_ADAPTER=openfoam
# export ANTHROPIC_API_KEY=...   # set by hand, NEVER commit it
ENV

echo "== Phase 8: optional heavy tools (run when wanted) =="
echo "  ParaView headless:  sudo apt-get install -y paraview"
echo "  Docker + DAFoam:    sudo apt-get install -y docker.io && sudo docker pull dafoam/opt-packages"

echo "== Done. Next: set ANTHROPIC_API_KEY in ~/.bashrc, clone the repo, =="
echo "== rsync artifacts, then run the test suite from ~/Certonomous/sdk. =="
