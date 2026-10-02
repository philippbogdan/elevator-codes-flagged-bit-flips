#!/bin/bash
# Run python from this directory's .venv, creating it (under a lock) if missing.
# Used for cluster jobs: each place keeps its own copy of the directory.
set -e
cd "$(dirname "$0")/.."
PKGS="stim==1.16.0 sinter==1.16.0 ldpc==2.4.1 pymatching==2.4.0 numpy scipy"
if ! .venv/bin/python -c "import stim, ldpc, scipy" 2>/dev/null; then
  exec 9>.venv.lock
  flock 9
  if ! .venv/bin/python -c "import stim, ldpc, scipy" 2>/dev/null; then
    rm -rf .venv
    python3 -m venv .venv
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q $PKGS
  fi
  flock -u 9
fi
exec .venv/bin/python "$@"
