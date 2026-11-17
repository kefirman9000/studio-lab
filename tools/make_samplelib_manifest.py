"""Build sgcore/samplelibs.json: the exact files Studio Lab downloads for its real-instrument libraries.

Every library is CC0 (public domain) and pinned to one commit; each file is listed with its git blob SHA-1, which the
app checks after download. Run from the repo root with shallow, blob-less clones of the three repos:

    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/sgossner/VSCO-2-CE  <dir>/vsco-2-ce
    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/sgossner/VCSL        <dir>/vcsl
    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/sfzinstruments/virtuosity_drums <dir>/vdrums
    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/sfzinstruments/karoryfer.black-and-green-guitars <dir>/bng
    git clone --depth 1 --filter=blob:none --no-checkout https://github.com/sfzinstruments/karoryfer.shinyguitar <dir>/shiny
    python tools/make_samplelib_manifest.py <dir>                     (all libraries)
    python tools/make_samplelib_manifest.py <dir> --only twang,archtop  (just these, merged into the existing file)
(never use `git ls-tree -l` on these clones: it downloads every sample to report its size)
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
DYN_WORDS = {'pp': 1, 'p': 2, 'mp': 3, 'mf': 4, 'f': 5, 'ff': 6}


def tree(d):
    out = subprocess.run(['git', '-C', d, 'ls-tree', '-r', 'HEAD'], capture_output=True, text=True, check=True).stdout
    rows = {}
    for line in out.splitlines():
        meta, path = line.split('\t', 1)
        rows[path] = meta.split()[2]
    head = subprocess.run(['git', '-C', d, 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    return head, rows


def parse(name, lower=False):
    base = name.rsplit('/', 1)[-1].rsplit('.', 1)[0]
    if lower or re.match(r'^(twang|staccato)_|^[a-g]b?\d_vl', base):       # Karoryfer guitars: lower-case notes, 'bb3' = B flat 3
        base = re.sub(r'(^|_)([a-g])(b?)(\d)(?=_)', lambda m: m.group(1) + m.group(2).upper() + m.group(3) + m.group(4), base)
    m = re.search(r'(?:^|_)([A-G])(#|b)?(-?\d)(?=_|$)', base)
    midi = None
    if m:
        midi = 12 * (int(m.group(3)) + 1) + NOTE[m.group(1)] + {'#': 1, 'b': -1}.get(m.group(2) or '', 0)
    v = re.search(r'_vl?(\d+)(?=_|$)', base)
    dyn = int(v.group(1)) if v else None
    if dyn is None:
        w = re.search(r'_(pp|p|mp|mf|f|ff)(?:\d)?(?=_|$)', base)
        dyn = DYN_WORDS[w.group(1)] if w else None
    if dyn is None:
        w = re.search(r'_(soft|med|loud)(?=_|$)', base, re.I)
        dyn = {'soft': 1, 'med': 3, 'loud': 5}[w.group(1).lower()] if w else 1
    r = re.search(r'_rr(\d+)', base, re.I)
    rr = int(r.group(1)) if r else 1
    if not r:
        t = re.search(r'_v\d+_(\d+)$', base)               # VSCO sustains: ..._v1_1.wav
        rr = int(t.group(1)) if t else 1
    return midi, dyn, rr


# lib -> list of (instrument, articulation, folder regex, file regex, max round robins)
VSCO = [
    ('violins', 'sus', r'^Strings/Violin Section/susVib/', r'', 9), ('violins', 'short', r'^Strings/Violin Section/Spic/', r'', 1),
    ('violins', 'pizz', r'^Strings/Violin Section/Pizz/', r'', 1), ('violins', 'trem', r'^Strings/Violin Section/Trem/', r'', 1),
    ('violas', 'sus', r'^Strings/Viola Section/susvib/', r'', 9), ('violas', 'short', r'^Strings/Viola Section/spic/', r'', 1),
    ('violas', 'pizz', r'^Strings/Viola Section/pizz/', r'', 1), ('violas', 'trem', r'^Strings/Viola Section/trem/', r'', 1),
    ('celli', 'sus', r'^Strings/Cello Section/susvib/', r'', 9), ('celli', 'short', r'^Strings/Cello Section/spic/', r'', 1),
    ('celli', 'pizz', r'^Strings/Cello Section/pizzT/', r'', 1), ('celli', 'trem', r'^Strings/Cello Section/trem/', r'', 1),
    ('basses', 'sus', r'^Strings/Solo Contrabass/SusVib/', r'', 9), ('basses', 'short', r'^Strings/Solo Contrabass/Spic/', r'', 1),
    ('basses', 'pizz', r'^Strings/Solo Contrabass/Pizz/', r'', 1), ('basses', 'trem', r'^Strings/Solo Contrabass/Trem/', r'', 1),
    ('violin', 'sus', r'^Strings/Solo Violin/Arco Vib/', r'', 9),
    ('horn', 'sus', r'^Brass/F Horn/sus/', r'', 9), ('horn', 'short', r'^Brass/F Horn/stac/', r'', 1),
    ('trumpet', 'sus', r'^Brass/Trumpet/sus/', r'', 9), ('trumpet', 'short', r'^Brass/Trumpet/stac/', r'', 1),
    ('trombone', 'sus', r'^Brass/Tenor Trombone/sus/', r'', 9), ('trombone', 'short', r'^Brass/Tenor Trombone/stac/', r'', 1),
    ('tuba', 'sus', r'^Brass/Tuba/sus/', r'', 9), ('tuba', 'short', r'^Brass/Tuba/stac/', r'', 1),
    ('flute', 'sus', r'^Woodwinds/Flute/susvib/', r'', 9), ('flute', 'short', r'^Woodwinds/Flute/stac/', r'', 1),
    ('oboe', 'sus', r'^Woodwinds/Oboe/Vib/', r'', 9), ('oboe', 'short', r'^Woodwinds/Oboe/Stacc/', r'', 1),
    ('clarinet', 'sus', r'^Woodwinds/Clarinet/susLong/', r'', 9), ('clarinet', 'short', r'^Woodwinds/Clarinet/stac/', r'', 1),
    ('bassoon', 'sus', r'^Woodwinds/Bassoon/vib/', r'', 9), ('bassoon', 'short', r'^Woodwinds/Bassoon/stac/', r'', 1),
    ('piccolo', 'sus', r'^Woodwinds/Piccolo/Sus/', r'', 9), ('piccolo', 'short', r'^Woodwinds/Piccolo/Stac/', r'', 1),
    ('timpani', 'hit', r'^Percussion/Timpani/Timpani\d_Hit', r'', 2),
]
VCSL = [
    ('conga', 'hit', r'/Struck Membranophones/Conga/', r'Conga_HitN', 2), ('conga', 'slap', r'/Struck Membranophones/Conga/', r'Slap', 2),
    ('bongo', 'hit', r'/Struck Membranophones/Bongos/', r'BongoH_Hit1', 2),
    ('shaker', 'hit', r'/Shaker, Small/', r'ShakerDouble|Shaker_Slap', 2),
    ('tamb', 'hit', r'/Tambourine 1/', r'Tamb1_Hit', 2),
    ('clap', 'hit', r'/Struck Idiophones/Claps/', r'Clap_rr', 6),
    ('cowbell', 'hit', r'/Struck Idiophones/Cowbells/', r'Cowbell1_Hit', 2),
    ('claves', 'hit', r'/Struck Idiophones/Claves/', r'Claves1_Hit', 2),
    ('guiro', 'hit', r'/Struck Idiophones/Guiro/', r'Guiro_Hit', 2),
    ('woodblock', 'hit', r'/Struck Idiophones/Woodblock/', r'wood_click', 2),
    ('agogo', 'hit', r'/Struck Idiophones/Agogo Bells/', r'Agogo_High', 2),
    ('triangle', 'hit', r'/Struck Idiophones/Triangles/', r'triangle1_hit_m[pf]', 2),
    ('cabasa', 'hit', r'/Struck Idiophones/Cabasa/', r'Cabasa1_Hit', 2),
    ('orchcrash', 'hit', r'/Struck Idiophones/Clash Cymbals 1/', r'cymbal_crash1', 1),
]


def vdrums(mic):
    s = rf'^Samples/{mic}/'
    return [
        ('kick', 'hit', s + 'kick/', r'_kick_snoff_', 2), ('snare', 'hit', s + 'snare/', r'_snare_center_', 2),
        ('rim', 'hit', s + 'snare/', r'_snare_crossstick_', 2), ('rimshot', 'hit', s + 'snare/', r'_snare_rimshot_', 2),
        ('chat', 'hit', s + 'hh/', r'_hh_closed_', 2), ('ohat', 'hit', s + 'hh/', r'_hh_open_', 1),
        ('ride', 'hit', s + 'ride/', r'_ride_(?!bell)', 2), ('crash', 'hit', s + 'crash/', r'_crash_crash_', 2),
        ('tom', 'hit', s + 'htom/', r'_htom_center_', 1), ('ltom', 'hit', s + 'ltom/', r'_ltom_center_', 1),
    ]


Z = 'Chordophones/Zithers/'
KEYS = [
    ('grand', 'sus', r'^' + Z + 'Grand Piano, Steinway B/NoSus/', r'', 1),
    ('upright_piano', 'sus', r'^' + Z + 'Upright Piano, Yamaha/Sustains/', r'', 1),
    ('harpsichord', 'sus', r'^' + Z + 'Harpsichord, Flemish/Sustains/', r'', 1),
    ('pipeorgan', 'sus', r'^Aerophones/Edge-blown Aerophones/Pipe Organ/Loud/', r'', 1),
    ('fmpiano', 'sus', r'^Electrophones/TX81Z/FM Piano/', r'', 1),
]
I = 'Idiophones/Struck Idiophones/'
COLORS = [
    ('harp', 'ring', r'^Chordophones/Composite Chordophones/Concert Harp/', r'', 2),
    ('marimba', 'ring', r'^' + I + 'Marimba/', r'', 1),
    ('vibes', 'ring', r'^' + I + 'Vibraphone/Soft Mallets/', r'', 1),
    ('xylophone', 'ring', r'^' + I + 'Xylophone/Medium Mallets/', r'', 1),
    ('glock', 'ring', r'^' + I + 'Glockenspiel/', r'', 1),
    ('tubular', 'ring', r'^' + I + 'Tubular Bells 1/', r'', 1),
    ('kalimba', 'ring', r'^Idiophones/Plucked Idiophones/Kalimba, Tanzania/', r'', 2),
    ('sax', 'sus', r'^Aerophones/Reed Aerophones/Tenor Saxophone/Non-Vibrato/', r'', 1),
    ('sax', 'short', r'^Aerophones/Reed Aerophones/Tenor Saxophone/Staccato/', r'', 1),
    ('harmonica', 'sus', r'^Aerophones/Free Aerophones/Harmonica-Hohner-Special20-C/Sustains/', r'', 1),
    ('ocarina', 'sus', r'^Aerophones/Edge-blown Aerophones/Ocarina, Typical/Sustains/', r'', 1),
    ('sleigh', 'hit', r'^' + I + 'Sleigh Bells/', r'Sleighbells_Hit', 3),
]
# Karoryfer CC0 guitars
TWANG = [('twang', 'sus', r'^Samples/green/ord/', r'_(mf|f)_rr[12]\.wav$|_p_rr1\.wav$', 2),
         ('twang', 'short', r'^Samples/green/stac/', r'', 2)]
GROWLY = [('ebass', 'sus', r'^sustain/', r'_(p|f)_rr[12]\.wav$', 2), ('ebass', 'short', r'^staccato/', r'_rr[12]\.wav$', 2)]
MEAT = [('dbass', 'sus', r'^Samples/pizz/', r'/[a-g]b?\d_vl[13]_rr[12]\.wav$', 2)]
# Karoryfer CC0 drum kits (dry close mics, a few velocity layers, 2 round robins)
_V = r'_vl(2|5|8|11|14)_rr[12]\.(wav|flac)$'
SEVENTIES = [(k, 'hit', r'^Samples/retro_mic/' + f + r'_vl', r'_rr[12]\.wav$', 2) for k, f in
             (('kick', 'ks'), ('snare', 'sc'), ('rim', 'ss'), ('chat', 'hc'), ('ohat', 'ho'), ('tom', 'tm'), ('ltom', 'tl'))]
_VS = r'_vl(2|5|8|11)_rr[12](_top)?\.wav$'                  # Swirly snares: the top mic of top / bottom pairs
BRUSHES = [(k, 'hit', r'^Samples/' + f + '/', _VS, 2) for k, f in
           (('kick', 'kick_buzz'), ('snare', 'snare_main'), ('rim', 'snare_edge'), ('chat', 'hat_closed'), ('ohat', 'hat_open'),
            ('ride', 'ride'), ('crash', 'crash'), ('tom', 'tom_mlow'), ('ltom', 'tom_floor'))]
RUSTY = [(k, 'hit', r'^Samples/' + f, _V, 2) for k, f in
         (('kick', 'kick_24/kick/kick/'), ('snare', 'snare_14/center/top/'), ('rim', 'snare_14/sidestick/top/'),
          ('rimshot', 'snare_14/rimshot/top/'), ('chat', 'hihat_14/cl/cl/'), ('ohat', 'hihat_14/open/cl/'),
          ('ride', 'ride_22/rd/cl/'), ('crash', 'crash_17/cr/cl/'), ('tom', 'tom_15/center/cl/'), ('ltom', 'tom_22/center/cl/'))]
ARCHTOP = [('acguitar', 'ring', r'^Samples/acoustic/', r'/[a-g]b?\d_vl[24]_rr[12]_1\.wav$', 2)]
THIN = {'grand': ({2, 4}, 2), 'upright_piano': ({1, 3}, None), 'harpsichord': (None, 2)}
STRINGS = {'violins', 'violas', 'celli', 'basses', 'violin'}
LIBS = {
    'strings': dict(repo='sgossner/VSCO-2-CE', dir='vsco-2-ce', title='Orchestral strings (VSCO 2 Community Edition)',
                    by='Versilian Studios', rules=[('', r) for r in VSCO if r[0] in STRINGS], ext='.wav'),
    'winds': dict(repo='sgossner/VSCO-2-CE', dir='vsco-2-ce', title='Brass, woodwinds & timpani (VSCO 2 Community Edition)',
                  by='Versilian Studios', rules=[('', r) for r in VSCO if r[0] not in STRINGS], ext='.wav'),
    'percussion': dict(repo='sgossner/VCSL', dir='vcsl', title='Percussion (Versilian Community Sample Library)',
                       by='Versilian Studios', rules=[('', r) for r in VCSL], ext='.wav'),
    'keys': dict(repo='sgossner/VCSL', dir='vcsl', title='Pianos & keys (Versilian Community Sample Library)',
                 by='Versilian Studios', rules=[('', r) for r in KEYS], ext='.wav'),
    'colors': dict(repo='sgossner/VCSL', dir='vcsl', title='Harp, mallets, sax & more (Versilian Community Sample Library)',
                   by='Versilian Studios', rules=[('', r) for r in COLORS], ext='.wav'),
    'twang': dict(repo='sfzinstruments/karoryfer.black-and-green-guitars', dir='bng',
                  title='Twang electric guitar (Karoryfer Black And Green Guitars)', by='Karoryfer Samples',
                  rules=[('', r) for r in TWANG], ext='.wav'),
    'archtop': dict(repo='sfzinstruments/karoryfer.shinyguitar', dir='shiny', title='Acoustic archtop guitar (Karoryfer Shinyguitar)',
                    by='Karoryfer Samples', rules=[('', r) for r in ARCHTOP], ext='.wav'),
    'ebass': dict(repo='sfzinstruments/karoryfer.growlybass', dir='growlybass', title='Electric bass (Karoryfer Growlybass)',
                  by='Karoryfer Samples', rules=[('', r) for r in GROWLY], ext='.wav', lower=True, shift=-12),
    'dbass': dict(repo='sfzinstruments/karoryfer.meatbass', dir='meatbass', title='Upright double bass (Karoryfer Meatbass)',
                  by='Karoryfer Samples', rules=[('', r) for r in MEAT], ext='.wav'),
    'kit70s': dict(repo='sfzinstruments/karoryfer.gogodze-phu-vol-ii', dir='gogodze',
                   title='70s soul drum kit (Karoryfer Gogodze Phu Vol II)', by='Karoryfer Samples',
                   rules=[('seventies', r) for r in SEVENTIES], ext='.wav'),
    'kitbrush': dict(repo='sfzinstruments/karoryfer.swirly-drums', dir='swirly', title='Brushes drum kit (Karoryfer Swirly Drums)',
                     by='Karoryfer Samples', rules=[('brushes', r) for r in BRUSHES], ext='.wav'),
    'kitrusty': dict(repo='sfzinstruments/karoryfer.big-rusty-drums', dir='rusty',
                     title='Big vintage rock kit (Karoryfer Big Rusty Drums)', by='Karoryfer Samples',
                     rules=[('rusty', r) for r in RUSTY], ext='.flac'),
    'drums': dict(repo='sfzinstruments/virtuosity_drums', dir='vdrums', title='Acoustic drum kits (Virtuosity Drums)',
                  by='Versilian Studios & Karoryfer', rules=[('studio', r) for r in vdrums('mid')] + [('lofi', r) for r in vdrums('lofi')] + [('room', r) for r in vdrums('room')],
                  ext='.flac'),
}


def size_of(repo, commit, path):
    url = f'https://raw.githubusercontent.com/{repo}/{commit}/' + urllib.parse.quote(path)
    req = urllib.request.Request(url, method='HEAD')
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers['Content-Length'])


def main(root, only=None):
    out = {'version': 1, 'license': 'CC0-1.0', 'libs': {}}
    if only:
        with open(os.path.join('sgcore', 'samplelibs.json')) as fh:
            out = json.load(fh)
    for lib, cfg in LIBS.items():
        if only and lib not in only:
            continue
        commit, rows = tree(os.path.join(root, cfg['dir']))
        files = []
        for kit, (inst, art, folder, pat, max_rr) in cfg['rules']:
            for path, sha in sorted(rows.items()):
                if not path.lower().endswith(cfg['ext']) or not re.search(folder, path) or (pat and not re.search(pat, path)):
                    continue
                midi, dyn, rr = parse(path, cfg.get('lower', False))
                if midi is not None and cfg.get('shift'):
                    midi += cfg['shift']             # Growlybass files are named an octave above the sounding pitch
                if rr > max_rr:
                    continue
                f = dict(p=path, sha=sha, i=(kit + ':' + inst) if kit else inst, a=art, v=dyn, r=rr)
                if midi is not None and art not in ('hit', 'slap'):
                    f['n'] = midi
                elif inst == 'timpani':
                    f['n'] = None
                files.append(f)
        for inst, (layers, step) in THIN.items():       # keep downloads reasonable: fewer layers / every n-th recorded note
            mine = [f for f in files if f['i'] == inst]
            if not mine:
                continue
            notes = sorted({f['n'] for f in mine if f.get('n') is not None})
            keep_n = set(notes[::step]) if step else set(notes)
            files = [f for f in files if f['i'] != inst or ((layers is None or f['v'] in layers) and f.get('n') in keep_n)]
        with ThreadPoolExecutor(16) as ex:
            sizes = list(ex.map(lambda f: size_of(cfg['repo'], commit, f['p']), files))
        for f, s in zip(files, sizes):
            f['s'] = s
        total = sum(sizes)
        out['libs'][lib] = dict(repo=cfg['repo'], commit=commit, title=cfg['title'], by=cfg['by'], files=files, bytes=total)
        counts = {}
        for f in files:
            counts[(f['i'], f['a'])] = counts.get((f['i'], f['a']), 0) + 1
        print(f"{lib}: {len(files)} files, {total / 1e6:.0f} MB")
        for k, c in sorted(counts.items()):
            print('   ', k, c)
    with open(os.path.join('sgcore', 'samplelibs.json'), 'w') as fh:
        json.dump(out, fh, separators=(',', ':'))


if __name__ == '__main__':
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
    main(sys.argv[1], only)
