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
    ap.add_argument('--melody', choices=['diatonic', 'pentatonic', 'blues', 'bebop'], help='how the lead phrases (default: genre)')
    ap.add_argument('--voicing', choices=['close', 'open', 'drop2', 'rootless', 'power'], help='chord voicing (default: genre)')
    ap.add_argument('--chord-color', choices=['triad', '7', 'add9', '9', '6', 'sus2', 'sus4'])
    ap.add_argument('--level', action='append', default=[], help='part level in dB, e.g. --level lead=-3 --level bass=+2')
    ap.add_argument('--mute', default='', help='comma-separated layers to drop: kick,snare,top,bass,chords,pad,arp,lead,fx')
    ap.add_argument('--no-vst-rig', action='store_true', help="don't play parts through your installed plugins")
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
            o.setdefault('vst_rig', not a.no_vst_rig)
            for k, v in (('melody_style', a.melody), ('voicing', a.voicing), ('chord_color', a.chord_color)):
                if v:
                    o[k] = v
            if a.level:
                o['part_levels'] = {k: float(v) for k, v in (x.split('=', 1) for x in a.level)}
            if a.mute:
                o['muted'] = [m.strip() for m in a.mute.split(',') if m.strip()]
            generate(Options.from_dict(o), a.out, outputs=[f.strip() for f in a.formats.split(',')], preview=a.preview)


def vsts_main(argv=None):
    """python studiolab.py vsts [--install all|surge,dexed,...] [--for STYLE] [--remove ID] [--params PLUGIN]"""
    from . import vstpacks, vstrigs, vsthost
    ap = argparse.ArgumentParser(prog='studiolab vsts', description='Download free instruments for the genre rigs.')
    ap.add_argument('--install', help='"all" or comma-separated pack ids')
    ap.add_argument('--for', dest='style', help='install whatever this style needs, then show its rig')
    ap.add_argument('--remove', help='pack id to uninstall from the plugins folder')
    ap.add_argument('--params', help='path to a .vst3 - list its parameter names (for writing new patches)')
    a = ap.parse_args(argv)
    if a.params:
        r = vsthost.probe(a.params, list_params=True)
        if not r.get('ok'):
            sys.exit(r.get('error'))
        for p in r.get('params', []):
            print(f"  {p['name']:<36} {p['value']:.3f}  {', '.join(p['choices'][:8])}")
        return
    if a.remove:
        vstpacks.remove(a.remove)
    ids = []
    if a.install:
        ids = list(vstpacks.BY_ID) if a.install == 'all' else [i.strip() for i in a.install.split(',') if i.strip()]
    if a.style:
        if a.style not in STYLES:
            sys.exit(f'unknown style {a.style!r}')
        ids += [i for i in vstrigs.plan(a.style)['missing_packs'] if i not in ids]
    if ids:
        if not vsthost.available() and not vsthost.install():
            sys.exit('could not install VST support (pip install pedalboard)')
        r = vstpacks.install_many(ids)
        if r['failed']:
            print('some downloads failed:', ', '.join(f['id'] for f in r['failed']))
    st = vstpacks.status()
    for p in st['packs']:
        print(f"  [{'x' if p['installed'] else ' '}] {p['id']:<7} {p['name']:<24} {p['plays']}")
    for k in st['known']:
        print(f"  [{'x' if k['installed'] else ' '}] {'-':<7} {k['name']:<24} {k['plays']}  ({k['url']})")
    if a.style:
        print(f"\n  {a.style} rig:")
        for r in vstrigs.plan(a.style)['parts']:
            print(f"    {r['layer']:<7} {r['inst']:<14} -> {r['uses'] or 'built-in'}{('  (' + r['hint'] + ')') if r.get('hint') else ''}")
