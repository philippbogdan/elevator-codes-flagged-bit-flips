#!/bin/bash
# Run python for cluster jobs.  Uses .venv if it imports the pinned packages; otherwise a
# private .venv-elev built (under a lock) with an explicit Python 3.12.  Never modifies .venv.
set -e
cd "$(dirname "$0")/.."
PKGS="stim==1.16.0 sinter==1.16.0 ldpc==2.4.1 pymatching==2.4.0 numpy scipy"
CHECK="import sys, stim, ldpc, scipy, scipy.optimize; assert sys.version_info[:2] == (3, 12)"
if [ -x .venv/bin/python ] && .venv/bin/python -c "$CHECK" 2>/dev/null; then
  exec .venv/bin/python "$@"
fi
PY=.venv-elev/bin/python
if ! "$PY" -c "$CHECK" 2>/dev/null; then
  mkdir -p .gpurun
  exec 9>.gpurun/venv-elev.lock
  flock 9
  if ! "$PY" -c "$CHECK" 2>/dev/null; then
    BASE=""
    for cand in /vol/bitbucket/pb825/.tools/python/cpython-3.12-linux-x86_64-gnu/bin/python3.12 \
                "$HOME/.tools/python/cpython-3.12-linux-x86_64-gnu/bin/python3.12" python3.12; do
      if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import sys; assert sys.version_info[:2]==(3,12)" 2>/dev/null; then
        BASE="$cand"; break
      fi
    done
    if [ -z "$BASE" ]; then echo "no python3.12 on $(hostname)" >&2; exit 97; fi
    rm -rf .venv-elev
    "$BASE" -m venv .venv-elev
    .venv-elev/bin/python -m pip install -q --upgrade pip
    .venv-elev/bin/python -m pip install -q $PKGS
  fi
  flock -u 9
fi
exec "$PY" "$@"
