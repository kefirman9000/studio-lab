"""List what the era / character check removed from each genre's sound list (1.90).

    python tools/pool_audit.py            # every genre with something removed
    python tools/pool_audit.py trance     # one genre: its final lists, and anything removed

A genre's own chosen sounds are never removed - only sounds the shared scene lists added, when they clash with the
genre (brutal bass-music sounds in a gentle genre, modern EDM sounds in an older or acoustic one). The rules are
sgcore/pool_variety.py: era_clash().
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    import sgcore.compose  # noqa: F401  (builds the lists)
    from sgcore.pool_variety import ERA_DROPPED
    from sgcore.styles import POOLS
    names = [a for a in sys.argv[1:] if not a.startswith('-')]
    if names:
        for g in names:
            print(g)
            for role, lst in (POOLS.get(g) or {}).items():
                print(f'  {role:7s} {", ".join(lst)}')
            for role, x, why in ERA_DROPPED.get(g, []):
                print(f'  removed from {role}: {x} ({why})')
        return
    total = 0
    for g, lst in sorted(ERA_DROPPED.items()):
        print(f'{g:28s} ' + ', '.join(f'{x} ({role})' for role, x, _ in lst))
        total += len(lst)
    print(f'{total} sounds removed from {len(ERA_DROPPED)} genres')


if __name__ == '__main__':
    main()
