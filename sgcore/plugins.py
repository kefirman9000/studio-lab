"""Plugin catalog + recommendations: which VST/AU to load for each part, preferring what the user owns."""

# category tags: bass 808 lead pad pluck chords keys epiano organ strings orchestral choir brass guitar fm drums
#                reverb delay eq comp limiter meter
CATALOG = [
    # ---------------- free instruments
    dict(id='vital', name='Vital', maker='Matt Tytel', free=True, url='https://vital.audio',
         cats=['bass', 'lead', 'pad', 'pluck', 'chords', 'fm'], rank=10,
         tip='Wavetable synth. Supersaw: Init > OSC1 saw, unison 7, detune ~0.3. Bass: OSC1 saw + sub, filter env on cutoff.'),
    dict(id='surge', name='Surge XT', maker='Surge Synth Team', free=True, url='https://surge-synthesizer.github.io',
         cats=['bass', 'lead', 'pad', 'pluck', 'chords', 'fm', 'organ'], rank=10,
         tip='Open-source hybrid synth with 1000+ presets - browse the Bass / Leads / Pads categories first.'),
    dict(id='odin2', name='Odin 2', maker='The Wave Warden', free=True, url='https://thewavewarden.com/odin2',
         cats=['bass', 'lead', 'pad', 'pluck'], rank=7, tip='Great analog-style basses and leads; free and open source.'),
    dict(id='dexed', name='Dexed', maker='Digital Suburban', free=True, url='https://asb2m10.github.io/dexed/',
         cats=['epiano', 'fm', 'bass', 'keys'], rank=8, tip='DX7 clone - load the classic "E.PIANO 1" for Rhodes-style keys, FM bells and basses.'),
    dict(id='tal_noisemaker', name='TAL-NoiseMaker', maker='TAL Software', free=True,
         url='https://tal-software.com/products/tal-noisemaker', cats=['bass', 'lead', 'pad', 'pluck'], rank=6,
         tip='Simple, punchy virtual-analog; ideal for 80s/synthwave basses and leads.'),
    dict(id='tyrell', name='Tyrell N6', maker='u-he', free=True, url='https://u-he.com/products/tyrelln6/',
         cats=['bass', 'lead', 'pad'], rank=6, tip='Juno-flavoured analog synth - warm pads and strings.'),
    dict(id='labs', name='Spitfire LABS / Splice INSTRUMENT', maker='Spitfire Audio', free=True,
         url='https://labs.spitfireaudio.com', cats=['keys', 'strings', 'choir', 'pad', 'orchestral', 'epiano', 'brass'], rank=9,
         tip='Free sampled instruments: Soft Piano, Strings, Choir, Autograph Grand and many more.'),
    dict(id='bbcso_discover', name='BBC Symphony Orchestra Discover', maker='Spitfire Audio', free=True,
         url='https://www.spitfireaudio.com/bbc-symphony-orchestra-discover',
         cats=['orchestral', 'strings', 'brass'], rank=10,
         tip='Full orchestra: strings, brass (horns!), woodwinds, harp, celeste, timpani. Check the site for current pricing.'),
    dict(id='decent', name='Decent Sampler + Pianobook', maker='Decent Samples', free=True,
         url='https://www.decentsamples.com/product/decent-sampler-plugin/',
         cats=['keys', 'strings', 'guitar', 'choir', 'orchestral', 'epiano'], rank=7,
         tip='Free sample player; grab instruments from pianobook.co.uk (hundreds of free pianos, strings, oddities).'),
    dict(id='mt_power', name='MT Power Drum Kit 2', maker='MT Power', free=True, url='https://www.powerdrumkit.com',
         cats=['drums'], rank=8, tip='Acoustic rock/pop kit with General-MIDI mapping - the MIDI drum track plays straight into it.'),
    dict(id='sitala', name='Sitala', maker='Decomposer', free=True, url='https://decomposer.de/sitala/',
         cats=['drums', '808'], rank=7, tip='16-pad drum sampler: drop in your own kicks/snares/808s.'),
    dict(id='ample_lite', name='Ample Guitar / Bass Lite', maker='Ample Sound', free=True, url='https://www.amplesound.net',
         cats=['guitar', 'bass'], rank=6, tip='Free "Lite" sampled guitars and a P-bass.'),
    # ---------------- free effects
    dict(id='supermassive', name='Valhalla Supermassive', maker='Valhalla DSP', free=True,
         url='https://valhalladsp.com/shop/reverb/valhalla-supermassive/', cats=['reverb', 'delay'], rank=10,
         tip='Huge reverbs & delays - put it on a send for pads, leads and orchestral parts.'),
    dict(id='tdr_nova', name='TDR Nova', maker='Tokyo Dawn Labs', free=True, url='https://www.tokyodawn.net/tdr-nova/',
         cats=['eq'], rank=9, tip='Dynamic EQ - tame mud around 250-400 Hz on the master.'),
    dict(id='kotelnikov', name='TDR Kotelnikov', maker='Tokyo Dawn Labs', free=True, url='https://www.tokyodawn.net/tdr-kotelnikov/',
         cats=['comp'], rank=9, tip='Transparent glue compressor for the mix bus (2:1, slow attack).'),
    dict(id='ott', name='OTT', maker='Xfer Records', free=True, url='https://xferrecords.com/freeware', cats=['comp'], rank=7,
         tip='Aggressive multiband compressor - the classic EDM "make it pop" effect.'),
    dict(id='youlean', name='Youlean Loudness Meter', maker='Youlean', free=True, url='https://youlean.co/youlean-loudness-meter/',
         cats=['meter'], rank=8, tip='Check LUFS when mastering (streaming ~ -14, club ~ -8).'),
    dict(id='kh_essentials', name='Kilohearts Essentials', maker='Kilohearts', free=True,
         url='https://kilohearts.com/products/kilohearts_essentials', cats=['delay', 'eq', 'comp', 'limiter'], rank=6,
         tip='Bundle of handy free effects (delay, EQ, compressor, limiter...).'),
    # ---------------- paid favourites
    dict(id='serum', name='Serum 2', maker='Xfer Records', free=False, url='https://xferrecords.com/products/serum-2',
         cats=['bass', 'lead', 'pad', 'pluck', 'chords', 'fm'], rank=10, tip='The EDM standard for basses, leads and supersaws.'),
    dict(id='omnisphere', name='Omnisphere', maker='Spectrasonics', free=False, url='https://www.spectrasonics.net/products/omnisphere/',
         cats=['pad', 'lead', 'keys', 'bass', 'choir', 'guitar'], rank=9, tip='Massive library - especially pads and cinematic textures.'),
    dict(id='keyscape', name='Keyscape', maker='Spectrasonics', free=False, url='https://www.spectrasonics.net/products/keyscape/',
         cats=['keys', 'epiano', 'organ'], rank=10, tip='Top-tier pianos and electric pianos.'),
    dict(id='pigments', name='Pigments', maker='Arturia', free=False, url='https://www.arturia.com/products/software-instruments/pigments/overview',
         cats=['bass', 'lead', 'pad', 'pluck', 'fm'], rank=8, tip='Wavetable/analog/granular hybrid with great presets.'),
    dict(id='diva', name='Diva', maker='u-he', free=False, url='https://u-he.com/products/diva/',
         cats=['bass', 'lead', 'pad', 'chords'], rank=8, tip='Most analog-sounding soft synth - synthwave/house basses and chords.'),
    dict(id='sylenth', name='Sylenth1', maker='LennarDigital', free=False, url='https://www.lennardigital.com',
         cats=['lead', 'pad', 'pluck', 'bass'], rank=7, tip='Classic trance/house supersaws and plucks.'),
    dict(id='kontakt', name='Kontakt (+ libraries)', maker='Native Instruments', free=False, url='https://www.native-instruments.com',
         cats=['keys', 'strings', 'orchestral', 'choir', 'guitar', 'drums', 'brass', 'epiano', 'organ'], rank=8,
         tip='Host for most commercial sample libraries.'),
    dict(id='bbcso_core', name='BBC Symphony Orchestra Core/Pro', maker='Spitfire Audio', free=False,
         url='https://www.spitfireaudio.com', cats=['orchestral', 'strings', 'brass', 'choir'], rank=10,
         tip='Full professional orchestra with all articulations.'),
    dict(id='addictive_drums', name='Addictive Drums 2', maker='XLN Audio', free=False,
         url='https://www.xlnaudio.com/products/addictive_drums_2', cats=['drums'], rank=9, tip='Mix-ready acoustic kits; GM mapping available.'),
    dict(id='superior', name='Superior Drummer 3', maker='Toontrack', free=False, url='https://www.toontrack.com/product/superior-drummer-3/',
         cats=['drums'], rank=10, tip='Deepest acoustic drum sampler.'),
    dict(id='fabfilter', name='FabFilter Pro-Q / Pro-L', maker='FabFilter', free=False, url='https://www.fabfilter.com',
         cats=['eq', 'limiter'], rank=10, tip='Surgical EQ and transparent mastering limiter.'),
    dict(id='vintageverb', name='Valhalla VintageVerb', maker='Valhalla DSP', free=False,
         url='https://valhalladsp.com/shop/reverb/valhalla-vintage-verb/', cats=['reverb'], rank=9, tip='Classic hall/plate reverbs.'),
    dict(id='ozone', name='Ozone', maker='iZotope', free=False, url='https://www.izotope.com', cats=['limiter', 'eq', 'meter'], rank=8,
         tip='All-in-one mastering suite.'),
]
CATALOG.append(dict(id='generaluser', name='GeneralUser GS soundfont', maker='S. Christian Collins', free=True,
                    url='https://schristiancollins.com/generaluser.php',
                    cats=['keys', 'strings', 'orchestral', 'brass', 'choir', 'guitar', 'organ', 'epiano', 'drums', 'bass', 'lead', 'pad'],
                    rank=5, tip="General-MIDI soundfont (.sf2). In LMMS add an 'Sf2 Player' instrument and load it - works on every OS, no VST needed."))

FORMATS = {'vital': ['vst2', 'vst3', 'au', 'lv2'], 'surge': ['vst3', 'au', 'clap', 'lv2'], 'odin2': ['vst3', 'au', 'lv2'], 'dexed': ['vst3', 'au'], 'tal_noisemaker': ['vst2', 'vst3', 'au', 'clap'], 'tyrell': ['vst2', 'vst3', 'au'], 'labs': ['vst3', 'au'], 'bbcso_discover': ['vst2', 'vst3', 'au'], 'decent': ['vst2', 'vst3', 'au'], 'mt_power': ['vst2', 'au'], 'sitala': ['vst2', 'vst3', 'au'], 'ample_lite': ['vst2', 'vst3', 'au'], 'supermassive': ['vst2', 'vst3', 'au'], 'tdr_nova': ['vst2', 'vst3', 'au'], 'kotelnikov': ['vst2', 'vst3', 'au'], 'ott': ['vst2', 'vst3', 'au'], 'youlean': ['vst2', 'vst3', 'au'], 'kh_essentials': ['vst2', 'vst3', 'au'], 'serum': ['vst3', 'au'], 'omnisphere': ['vst2', 'vst3', 'au'], 'keyscape': ['vst2', 'vst3', 'au'], 'pigments': ['vst3', 'au'], 'diva': ['vst2', 'vst3', 'au'], 'sylenth': ['vst2', 'vst3', 'au'], 'kontakt': ['vst3', 'au'], 'bbcso_core': ['vst2', 'vst3', 'au'], 'addictive_drums': ['vst2', 'vst3', 'au'], 'superior': ['vst2', 'vst3', 'au'], 'fabfilter': ['vst2', 'vst3', 'au'], 'vintageverb': ['vst2', 'vst3', 'au'], 'ozone': ['vst3', 'au'], 'generaluser': ['sf2']}
MATCH = {'vital': ['vital'], 'surge': ['surge xt', 'surgext', 'surge'], 'odin2': ['odin2', 'odin 2'], 'dexed': ['dexed'], 'tal_noisemaker': ['noisemaker'], 'tyrell': ['tyrelln6', 'tyrell'], 'labs': ['labs', 'splice instrument'], 'bbcso_discover': ['bbc symphony orchestra'], 'decent': ['decentsampler', 'decent sampler'], 'mt_power': ['powerdrumkit', 'power drum kit', 'mt-power'], 'sitala': ['sitala'], 'ample_lite': ['ample'], 'supermassive': ['supermassive'], 'tdr_nova': ['tdr nova', 'tdrnova'], 'kotelnikov': ['kotelnikov'], 'ott': ['ott'], 'youlean': ['youlean'], 'kh_essentials': ['kilohearts'], 'serum': ['serum'], 'omnisphere': ['omnisphere'], 'keyscape': ['keyscape'], 'pigments': ['pigments'], 'diva': ['diva'], 'sylenth': ['sylenth'], 'kontakt': ['kontakt'], 'addictive_drums': ['addictive drums'], 'superior': ['superior drummer', 'superior3'], 'fabfilter': ['fabfilter'], 'vintageverb': ['vintageverb', 'vintage verb'], 'ozone': ['ozone'], 'generaluser': ['generaluser']}
for _p in CATALOG:
    _p['formats'] = FORMATS.get(_p['id'], ['vst3', 'au'])
BY_ID = {p['id']: p for p in CATALOG}

# ----------------------------------------------------------------------------- DAW / OS compatibility
DAWS = {'lmms': 'LMMS', 'waveform': 'Waveform Free'}


def daw_formats(daw, osname):
    """Formats a DAW can load: LMMS = VST2 (VeSTige) on Windows/Linux + SF2 everywhere; Waveform = VST/VST3 (+AU on Mac)."""
    if daw == 'lmms':
        return {'sf2'} if osname == 'mac' else {'vst2', 'sf2'}
    if daw == 'waveform':
        return {'vst2', 'vst3', 'au'} if osname == 'mac' else {'vst2', 'vst3'}
    return {'vst2', 'vst3', 'au', 'clap'}


def works_in(plugin, daws, osname, found_formats=None):
    fm = set(found_formats or plugin['formats'])
    return {d: bool(fm & daw_formats(d, osname)) for d in daws}


# which plugin category suits each built-in instrument
INST_CAT = {
    'sawbass': 'bass', 'reese': 'bass', 'fmbass': 'bass', 'wobble': 'bass', 'acid': 'bass', 'sinebass': 'bass',
    'chipbass': 'bass', '808': 'bass', 'supersaw': 'pad', 'warmpad': 'pad', 'stab': 'chords', 'pluck_saw': 'pluck',
    'leadsaw': 'lead', 'supersaw_lead': 'lead', 'hoover': 'lead', 'chip': 'lead', 'softlead': 'lead', 'epiano': 'epiano',
    'piano': 'keys', 'organ': 'organ', 'pluck': 'guitar', 'guitar': 'guitar', 'bell': 'fm', 'cowbell': 'fm',
    'brass': 'brass', 'vox': 'choir', 'choir': 'choir', 'strings': 'strings', 'violin': 'orchestral', 'pizz': 'orchestral',
    'harp': 'orchestral', 'horn': 'orchestral', 'timpani': 'orchestral', 'celesta': 'orchestral',
    'spiccato': 'strings', 'tremolo': 'strings', 'cello': 'strings', 'harpsichord': 'keys', 'clarinet': 'orchestral',
    'oboe': 'orchestral', 'braam': 'brass',
    'logdrum': 'bass', 'marimba': 'keys', 'kalimba': 'keys', 'steeldrum': 'fm', 'sax': 'brass', 'flute': 'orchestral', 'clav': 'keys',
}
CAT_FALLBACK = {'808': ['bass', 'drums'], 'organ': ['keys', 'pad'], 'epiano': ['keys', 'fm'], 'brass': ['orchestral', 'lead'],
                'choir': ['pad'], 'strings': ['orchestral', 'pad'], 'chords': ['pluck', 'pad'], 'pluck': ['lead'],
                'fm': ['lead'], 'guitar': ['pluck'], 'keys': ['epiano']}


def _candidates(cat):
    found = [p for p in CATALOG if cat in p['cats']]
    if not found:
        for alt in CAT_FALLBACK.get(cat, []):
            found = [p for p in CATALOG if alt in p['cats']]
            if found:
                break
    return found


def recommend(cat, owned=(), daws=('lmms', 'waveform'), osname='windows', found=None):
    """Best plugin you own for this category (preferring ones that load in your DAWs), plus the best free option."""
    owned = set(owned or [])
    found = found or {}
    cands = _candidates(cat)

    def score(p):
        w = works_in(p, daws, osname, found.get(p['id']))
        return (sum(w.values()), p['rank'])
    out = []
    mine = sorted([p for p in cands if p['id'] in owned], key=score, reverse=True)
    if mine:
        out.append(mine[0])
    free = sorted([p for p in cands if p['free'] and (not out or p['id'] != out[0]['id'])], key=score, reverse=True)
    if free:
        out.append(free[0])
    if not out:
        out = sorted(cands, key=score, reverse=True)[:1]
    res = []
    for p in out:
        res.append(dict(id=p['id'], name=p['name'], url=p['url'], free=p['free'], tip=p['tip'], owned=p['id'] in owned,
                        formats=found.get(p['id']) or p['formats'], works=works_in(p, daws, osname, found.get(p['id']))))
    return res


def song_recommendations(song, owned=(), daws=('lmms', 'waveform'), osname='windows', found=None):
    from .instruments import DRUMS
    recs = {}
    for t in song['st']['tracks']:
        if t['inst'] in DRUMS or t['layer'] == 'fx':
            continue
        cat = INST_CAT.get(t['inst'], 'lead')
        recs[t['name']] = dict(instrument=t['inst'], category=cat, picks=recommend(cat, owned, daws, osname, found))
    if any(t['inst'] in DRUMS for t in song['st']['tracks']):
        dcat = '808' if song['st'].get('category') == 'Electronic' else 'drums'
        recs['drums'] = dict(instrument='drums', category=dcat, picks=recommend(dcat, owned, daws, osname, found))
    for fx in ('reverb', 'comp', 'eq', 'limiter'):
        recs['mix: ' + fx] = dict(instrument=fx, category=fx, picks=recommend(fx, owned, daws, osname, found))
    return recs


def _works_txt(w):
    return ', '.join(f"{DAWS.get(d, d)} {'yes' if ok else 'NO'}" for d, ok in w.items())


def write_guide(path, song, prefs=None):
    prefs = prefs or {}
    owned, daws, osname = prefs.get('owned', []), prefs.get('daws') or ['lmms', 'waveform'], prefs.get('os', 'windows')
    recs = song_recommendations(song, owned, daws, osname, prefs.get('found'))
    st = song['st']
    lines = [f"Plugin guide - {song['style']} in {song['key'].name()}, {song['bpm']} BPM",
             f"Your setup: {', '.join(DAWS.get(d, d) for d in daws)} on {osname}", '',
             'Each MIDI track in the export is one part. Load the suggested plugin on it.',
             '* = you own it.  "works in" = which of your DAWs can load it',
             '(LMMS: VST2 on Windows/Linux + SF2 soundfonts everywhere.  Waveform: VST/VST3, plus AU on Mac).', '']
    if st.get('gm_hint'):
        lines += ['Orchestration: ' + st['gm_hint'], '']
    for part, r in recs.items():
        for i, p in enumerate(r['picks']):
            head = f"{part:<14} -> " if i == 0 else f"{'':<14}    or "
            lines.append(f"{head}{'* ' if p['owned'] else ''}{p['name']} ({'free' if p['free'] else 'paid'}, "
                         f"{'/'.join(p['formats']).upper()})  {p['url']}")
            lines.append(f"{'':<18}works in: {_works_txt(p['works'])}")
            if i == 0:
                lines.append(f"{'':<18}{p['tip']}")
        lines.append('')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return path


# ----------------------------------------------------------------------------- scan installed plugins
import os as _os
import sys as _sys


def plugin_dirs():
    home = _os.path.expanduser('~')
    if _sys.platform.startswith('win'):
        dirs = []
        for b in (_os.environ.get('ProgramFiles', r'C:\Program Files'), _os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')):
            dirs += [_os.path.join(b, 'Common Files', 'VST3'), _os.path.join(b, 'Common Files', 'VST2'), _os.path.join(b, 'Common Files', 'CLAP'),
                     _os.path.join(b, 'VSTPlugins'), _os.path.join(b, 'Steinberg', 'VSTPlugins')]
        dirs += [_os.path.join(home, 'Documents', 'lmms', 'plugins', 'vst'), _os.path.join(home, 'Documents', 'LMMS', 'plugins', 'vst')]
        return dirs
    if _sys.platform == 'darwin':
        out = []
        for b in ('/Library/Audio/Plug-Ins', _os.path.join(home, 'Library/Audio/Plug-Ins')):
            out += [_os.path.join(b, x) for x in ('VST', 'VST3', 'Components', 'CLAP')]
        return out
    return [_os.path.join(home, x) for x in ('.vst', '.vst3', '.clap', '.lv2', 'lmms/plugins/vst')] + \
        ['/usr/lib/vst', '/usr/lib/vst3', '/usr/local/lib/vst', '/usr/local/lib/vst3', '/usr/lib/lv2']


EXT_FMT = {'.vst3': 'vst3', '.component': 'au', '.clap': 'clap', '.dll': 'vst2', '.so': 'vst2', '.vst': 'vst2', '.lv2': 'lv2', '.sf2': 'sf2'}


def _match(base):
    for pid, pats in MATCH.items():
        if any(pt == base or (len(pt) > 3 and pt in base) for pt in pats):
            return pid
    return None


def scan(extra_dirs=()):
    """Look through the standard plugin folders. Returns found={catalog_id: [formats]}, other=[names], dirs=[searched]."""
    found, other, searched = {}, set(), []
    for d in list(plugin_dirs()) + [x for x in (extra_dirs or []) if x]:
        if not _os.path.isdir(d):
            continue
        searched.append(d)
        for root, dirnames, files in _os.walk(d):
            depth = root[len(d):].count(_os.sep)
            for name in list(dirnames) + files:
                ext = _os.path.splitext(name)[1].lower()
                fmt = EXT_FMT.get(ext)
                if not fmt:
                    continue
                base = _os.path.splitext(name)[0].lower().replace('_', ' ')
                pid = _match(base)
                if pid:
                    found.setdefault(pid, [])
                    if fmt not in found[pid]:
                        found[pid].append(fmt)
                else:
                    other.add(f"{_os.path.splitext(name)[0]} ({fmt.upper()})")
            dirnames[:] = [x for x in dirnames if _os.path.splitext(x)[1].lower() not in EXT_FMT] if depth < 3 else []
    return dict(found=found, other=sorted(other)[:300], dirs=searched)
