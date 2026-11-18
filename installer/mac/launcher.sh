#!/bin/bash
# Studio Lab.app/Contents/MacOS/Studio Lab
# The app bundle carries a private Python (Resources/python) and the program (Resources/app). The program is copied to
# ~/Library/Application Support/Studio Lab and run from there, so in-app updates, songs and settings live outside the
# (read-only, signed) bundle and survive dragging a newer Studio Lab into Applications.
RES="$(cd "$(dirname "$0")/../Resources" && pwd)"
PY="$RES/python/bin/python3"
DATA="$HOME/Library/Application Support/Studio Lab"
export PYTHONPYCACHEPREFIX="$HOME/Library/Caches/Studio Lab/pycache"   # never write inside the signed bundle
mkdir -p "$DATA"

NEW="$(cat "$RES/app/VERSION" 2>/dev/null)"
OLD="$(cat "$DATA/VERSION" 2>/dev/null || echo 0)"
if [ ! -f "$DATA/studiolab.py" ] || "$PY" -c '
import sys
v = lambda s: tuple(int(x) for x in s.strip().split(".") if x.isdigit())
sys.exit(0 if v(sys.argv[1]) > v(sys.argv[2]) else 1)' "$NEW" "$OLD"; then
  # a newer program than the one in Application Support: copy it over (songs, settings and sounds are not touched)
  (cd "$RES/app" && tar -cf - --exclude settings.json --exclude recent_instruments.json --exclude ratings.json .) \
    | (cd "$DATA" && tar -xf -)
fi

cd "$DATA"
exec "$PY" "$DATA/studiolab.py" "$@"
