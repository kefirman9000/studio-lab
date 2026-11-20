"""(1.90) Works out the genre map (which genres sound closest to which) and saves it to sgcore/genre_map.json.
Run it after adding genres or re-running tools/genre_fingerprints.py."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sgcore import genrematch  # noqa: E402
from sgcore.styles import STYLES, LABELS  # noqa: E402

if __name__ == '__main__':
    path = os.path.join(os.path.dirname(genrematch.__file__), 'genre_map.json')
    if os.path.exists(path):
        os.remove(path)
    m = genrematch.genre_map(STYLES, LABELS)
    with open(path, 'w') as f:
        json.dump(m, f, separators=(',', ':'))
    print(len(m), 'genres ->', path)
