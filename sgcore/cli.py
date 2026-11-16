"""Command-line interface."""
import argparse
import json
import random
import sys

from .api import generate, OUTPUTS
from .compose import Options, MOODS, FUSION_PARTS
from .styles import STYLES


def main(argv=None):
    ap = argparse.ArgumentParser(prog='studiolab generate', description='Render from the command line.')
    ap.add_argument('--style', default='random', help='style id, "random" or "all" (see --list)')
    ap.add_argument('--blend', default='', help='comma-separated styles to fuse in, e.g. dubstep,orchestral')
    ap.add_argument('--part', action='append', default=[], help='fusion assignment, e.g. --part bass=dubstep')
    ap.add_argument('--mood', choices=list(MOODS))
    ap.add_argument('--seed', type=int)
    ap.add_argument('--count', type=int, default=1)
    ap.add_argument('--bpm', type=int)
    ap.add_argument('--key', help='C, F#m, Ebm ...')
    ap.add_argument('--scale')
    ap.add_argument('--progression', help='e.g. i-VI-III-VII')
    ap.add_argument('--length', type=float, default=1.0)
    ap.add_argument('--structure', default='auto', choices=['auto', 'radio', 'club', 'loop'])
    ap.add_argument('--energy', type=float, default=0.5)
    ap.add_argument('--complexity', type=float, default=0.5)
    ap.add_argument('--swing', type=float)
    ap.add_argument('--sidechain', type=float)
    ap.add_argument('--brightness', type=float, default=0.0)
    ap.add_argument('--loudness', type=float)
    ap.add_argument('--inst', action='append', default=[], help='instrument override, e.g. --inst lead=violin')
    ap.add_argument('--kit')
    ap.add_argument('--mute', default='', help='comma-separated layers to drop: kick,snare,top,bass,chords,pad,arp,lead,fx')
    ap.add_argument('--preview', action='store_true', help='short clip only')
    ap.add_argument('--out', default='songs')
    ap.add_argument('--formats', default='wav', help='comma list of: ' + ','.join(OUTPUTS))
    ap.add_argument('--options', help='JSON file with saved settings (from a *_settings.json)')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args(argv)
    if a.list:
        for k, v in STYLES.items():
            print(f"  {k:<18} {v['category']:<11} {v['bpm'][0]}-{v['bpm'][1]} bpm  {v['desc']}")
        print('\n  moods:', ', '.join(MOODS))
        return
    base = {}
    if a.options:
        with open(a.options) as f:
            d = json.load(f)
        base = d.get('options', d)
    seed = a.seed if a.seed is not None else base.get('seed') or random.randrange(1, 10 ** 6)
    styles = list(STYLES) if a.style == 'all' else [a.style]
    for si, st in enumerate(styles):
        for c in range(a.count):
            s = st if st != 'random' else random.Random(seed + c).choice(list(STYLES))
            if s not in STYLES:
                sys.exit(f'unknown style {s!r} - use --list')
            o = dict(base)
            o.update(style=s, seed=seed + si * 1000 + c, length=a.length, structure=a.structure, energy=a.energy,
                     complexity=a.complexity, brightness=a.brightness)
            for k in ('bpm', 'key', 'scale', 'progression', 'swing', 'sidechain', 'loudness', 'kit', 'mood'):
                if getattr(a, k) is not None:
                    o[k] = getattr(a, k)
            if a.blend:
                o['blend'] = [b.strip() for b in a.blend.split(',') if b.strip()]
            if a.part:
                o['blend_parts'] = dict(p.split('=', 1) for p in a.part)
            if a.inst:
                o['instruments'] = dict(p.split('=', 1) for p in a.inst)
            if a.mute:
                o['muted'] = [m.strip() for m in a.mute.split(',') if m.strip()]
            generate(Options.from_dict(o), a.out, outputs=[f.strip() for f in a.formats.split(',')], preview=a.preview)
