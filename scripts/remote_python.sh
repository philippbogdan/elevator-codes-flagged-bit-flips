#!/bin/bash
# Run python from this directory's .venv (created by gpurun on each place), installing
# the pinned packages into it under a lock if they are missing.  Never deletes the venv.
set -e
cd "$(dirname "$0")/.."
PKGS="stim==1.16.0 sinter==1.16.0 ldpc==2.4.1 pymatching==2.4.0 numpy scipy"
PY=.venv/bin/python
if [ ! -x "$PY" ]; then
  for cand in python3.12 python3; do
    if command -v $cand >/dev/null && $cand -m venv .venv 2>/dev/null; then break; fi
  done
fi
if ! "$PY" -c "import stim, ldpc, scipy" 2>/dev/null; then
  mkdir -p .gpurun
  exec 9>.gpurun/pkgs.lock
  flock 9
  if ! "$PY" -c "import stim, ldpc, scipy" 2>/dev/null; then
    "$PY" -m pip install -q $PKGS
  fi
  flock -u 9
fi
exec "$PY" "$@"
