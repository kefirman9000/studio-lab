"""Genre rigs: play each part through the real plugin that defines that genre's sound.

A rig maps what a part plays (the built-in instrument the style chose: 'acid', 'supersaw', 'epiano' ...) to a list of
plugin patches, best first. Patches are parameter recipes applied when the plugin loads (see vst_worker.apply_recipe):
names are matched against the plugin's own parameter names, values are 0..1 knob positions or choice labels.
A patch lists `required` settings; if the plugin doesn't accept them the part keeps its built-in sound rather than
playing something that isn't the intended instrument.

Sample players (BBC Symphony Orchestra, LABS ...) have no patch parameters - their instrument is picked inside the
plugin. For those the rig uses a VST sound you saved yourself, chosen by its name ("BBC strings", "LABS piano").
"""
import json
import os
import re
import time

from . import vsthost


def _matcher(*pats, exclude=()):
    def m(path):
        n = re.sub(r'[\s_\-]+', ' ', os.path.splitext(os.path.basename(path))[0].lower())
        return any(p in n for p in pats) and not any(x in n for x in exclude)
    return m


PLAYERS = {
    'surge': dict(name='Surge XT', match=_matcher('surge xt', exclude=('effects', 'fx')), kind='synth', pack='surge'),
    'tal': dict(name='TAL-NoiseMaker', match=_matcher('noisemaker', 'noise maker'), kind='synth', pack=None),
    'dexed': dict(name='Dexed', match=_matcher('dexed'), kind='synth', pack='dexed'),
    'jc303': dict(name='JC303', match=_matcher('jc303', 'jc 303'), kind='synth', pack='jc303'),
    'nekobi': dict(name='Nekobi', match=_matcher('nekobi'), kind='synth', pack=None),
    'kars': dict(name='Kars', match=_matcher('kars'), kind='synth', pack=None),
    'bbcso': dict(name='BBC Symphony Orchestra', match=_matcher('bbc symphony orchestra'), kind='sampler', pack=None),
    'labs': dict(name='Spitfire LABS', match=_matcher('labs', exclude=('kilohearts',)), kind='sampler', pack=None),
}

OFF, ON = 0.0, 1.0
ACID_STYLES = {'acid_house', 'techno', 'minimal', 'psytrance', 'tech_house', 'electro', 'breakcore'}   # a 303 bassline only where it belongs
# ----------------------------------------------------------------------------- patches
# keys: plugin parameter names ("A|B" = try A, then B). float = knob position 0..1, str = choice label.
PATCHES = {
    # ---- TAL-NoiseMaker: Juno-flavoured analog. Parameter names read from the plugin itself.
    'tal.saw_bass': dict(player='tal', label='Analog saw bass', required=['Filter Cutoff'], params={
        'Osc 1 Waveform': 'saw', 'Osc 1 Volume': 0.85, 'Osc 2 Volume': 0.0, 'Osc 3 Volume': 0.55,
        'Filter Type': 'LP 24', 'Filter Cutoff': 0.34, 'Filter Resonance': 0.18, 'Filter Contour': 0.62,
        'Filter Attack': 0.0, 'Filter Decay': 0.32, 'Filter Sustain': 0.12, 'Filter Release': 0.12,
        'Amp Attack': 0.0, 'Amp Decay': 0.5, 'Amp Sustain': 0.85, 'Amp Release': 0.1, 'Master Detune': 0.0,
        'Chorus 1 Enable': OFF, 'Chorus 2 Enable': OFF, 'Delay Wet': 0.0, 'Reverb Wet': 0.0, 'Portamento Amount': 0.0}),
    'tal.reese': dict(player='tal', label='Detuned reese', required=['Filter Cutoff'], params={
        'Osc 1 Waveform': 'saw', 'Osc 2 Waveform': 'saw', 'Osc 1 Volume': 0.8, 'Osc 2 Volume': 0.8, 'Osc 3 Volume': 0.4,
        'Master Detune': 0.35, 'Filter Type': 'LP 24', 'Filter Cutoff': 0.42, 'Filter Resonance': 0.12, 'Filter Contour': 0.2,
        'Amp Attack': 0.0, 'Amp Sustain': 1.0, 'Amp Release': 0.12, 'Chorus 1 Enable': OFF, 'Chorus 2 Enable': OFF,
        'Delay Wet': 0.0, 'Reverb Wet': 0.0}),
    'tal.analog_pad': dict(player='tal', label='Juno pad', required=['Amp Attack'], params={
        'Osc 1 Waveform': 'saw', 'Osc 2 Waveform': 'saw', 'Osc 1 Volume': 0.75, 'Osc 2 Volume': 0.7, 'Osc 3 Volume': 0.0,
        'Master Detune': 0.22, 'Filter Type': 'LP 24', 'Filter Cutoff': 0.5, 'Filter Resonance': 0.1, 'Filter Contour': 0.15,
        'Filter Attack': 0.5, 'Amp Attack': 0.42, 'Amp Decay': 0.6, 'Amp Sustain': 0.9, 'Amp Release': 0.55,
        'Chorus 1 Enable': ON, 'Chorus 2 Enable': OFF, 'Reverb Wet': 0.25, 'Delay Wet': 0.0}),
    'tal.brass_stab': dict(player='tal', label='Poly brass stab', required=['Filter Cutoff'], params={
        'Osc 1 Waveform': 'saw', 'Osc 2 Waveform': 'saw', 'Osc 1 Volume': 0.8, 'Osc 2 Volume': 0.6, 'Osc 3 Volume': 0.0,
        'Master Detune': 0.12, 'Filter Type': 'LP 24', 'Filter Cutoff': 0.4, 'Filter Resonance': 0.15, 'Filter Contour': 0.5,
        'Filter Attack': 0.12, 'Filter Decay': 0.4, 'Filter Sustain': 0.3, 'Amp Attack': 0.04, 'Amp Decay': 0.45,
        'Amp Sustain': 0.6, 'Amp Release': 0.2, 'Chorus 1 Enable': ON, 'Reverb Wet': 0.12, 'Delay Wet': 0.0}),
    'tal.pluck': dict(player='tal', label='Analog pluck', required=['Filter Cutoff'], params={
        'Osc 1 Waveform': 'saw', 'Osc 2 Waveform': 'pulse', 'Osc 1 Volume': 0.8, 'Osc 2 Volume': 0.4, 'Osc 3 Volume': 0.0,
        'Master Detune': 0.08, 'Filter Type': 'LP 24', 'Filter Cutoff': 0.28, 'Filter Resonance': 0.2, 'Filter Contour': 0.7,
        'Filter Attack': 0.0, 'Filter Decay': 0.25, 'Filter Sustain': 0.0, 'Amp Attack': 0.0, 'Amp Decay': 0.38,
        'Amp Sustain': 0.0, 'Amp Release': 0.22, 'Chorus 1 Enable': ON, 'Delay Wet': 0.15, 'Reverb Wet': 0.1}),
    'tal.80s_lead': dict(player='tal', label='80s saw lead', required=['Filter Cutoff'], params={
        'Osc 1 Waveform': 'saw', 'Osc 2 Waveform': 'pulse', 'Osc 1 Volume': 0.8, 'Osc 2 Volume': 0.55, 'Osc 3 Volume': 0.0,
        'Master Detune': 0.15, 'Filter Type': 'LP 24', 'Filter Cutoff': 0.62, 'Filter Resonance': 0.15, 'Filter Contour': 0.25,
        'Amp Attack': 0.02, 'Amp Sustain': 0.9, 'Amp Release': 0.25, 'Portamento Amount': 0.12,
        'Chorus 2 Enable': ON, 'Delay Wet': 0.22, 'Reverb Wet': 0.15}),
    'tal.soft_lead': dict(player='tal', label='Soft triangle lead', required=['Filter Cutoff'], params={
        'Osc 1 Waveform': 'pulse', 'Osc 2 Waveform': 'tri', 'Osc 1 Volume': 0.2, 'Osc 2 Volume': 0.85, 'Osc 3 Volume': 0.0,
        'Filter Type': 'LP 24', 'Filter Cutoff': 0.45, 'Filter Resonance': 0.05, 'Filter Contour': 0.1,
        'Amp Attack': 0.08, 'Amp Sustain': 0.85, 'Amp Release': 0.3, 'Chorus 1 Enable': ON, 'Delay Wet': 0.2, 'Reverb Wet': 0.2}),
    'tal.acid': dict(player='tal', label='Acid squelch', required=['Filter Resonance'], params={
        'Osc 1 Waveform': 'saw', 'Osc 1 Volume': 0.85, 'Osc 2 Volume': 0.0, 'Osc 3 Volume': 0.0,
        'Filter Type': 'LP 24', 'Filter Cutoff': 0.24, 'Filter Resonance': 0.78, 'Filter Contour': 0.72,
        'Filter Attack': 0.0, 'Filter Decay': 0.28, 'Filter Sustain': 0.0, 'Amp Attack': 0.0, 'Amp Sustain': 0.9,
        'Amp Release': 0.08, 'Portamento Amount': 0.15, 'Chorus 1 Enable': OFF, 'Chorus 2 Enable': OFF,
        'Delay Wet': 0.0, 'Reverb Wet': 0.0}),
    # ---- TB-303 clones (JC303 and Nekobi share the 303 panel names)
    'jc303.acid': dict(player='jc303', label='303 acid', required=['Cutoff', 'Resonance'], params={
        'Waveform': 0.0, 'Cutoff': 0.28, 'Resonance': 0.82, 'Env Mod|Envmod': 0.65, 'Decay': 0.4, 'Accent': 0.6, 'Volume': 0.8}),
    'jc303.bass': dict(player='jc303', label='303 bassline', only=ACID_STYLES, required=['Cutoff'], params={
        'Waveform': 0.0, 'Cutoff': 0.42, 'Resonance': 0.35, 'Env Mod|Envmod': 0.35, 'Decay': 0.55, 'Accent': 0.4, 'Volume': 0.8}),
    'nekobi.acid': dict(player='nekobi', label='303 acid', required=['Cutoff', 'VCF Resonance'], params={
        'Waveform': 'triangle', 'Cutoff': 0.26, 'VCF Resonance': 0.85, 'Env Mod': 0.7, 'Decay': 0.4, 'Accent': 0.6, 'Volume': 0.8}),
    'nekobi.bass': dict(player='nekobi', label='303 bassline', only=ACID_STYLES, required=['Cutoff'], params={
        'Waveform': 'triangle', 'Cutoff': 0.4, 'VCF Resonance': 0.3, 'Env Mod': 0.35, 'Decay': 0.55, 'Accent': 0.4, 'Volume': 0.8}),
    # ---- Kars: Karplus-Strong plucked string
    'kars.pluck': dict(player='kars', label='Plucked string', required=['Release'], params={
        'Sustain': OFF, 'Release': 0.15, 'Volume': 0.8}),
    # ---- Dexed: original DX7 ROM 1A voices, selected by program name
    'dexed.epiano': dict(player='dexed', label='DX7 E.Piano 1', program=['E.PIANO 1', 10], params={}),
    'dexed.clav': dict(player='dexed', label='DX7 Clav', program=['CLAV 1', 19], params={}),
    'dexed.marimba': dict(player='dexed', label='DX7 Marimba', program=['MARIMBA', 21], params={}),
    'dexed.vibes': dict(player='dexed', label='DX7 Vibes', program=['VIBE 1', 20], params={}),
    'dexed.bells': dict(player='dexed', label='DX7 Tubular bells', program=['TUB BELLS', 25], params={}),
    'dexed.steeldrum': dict(player='dexed', label='DX7 Steel drum', program=['STEEL DRUM', 26], params={}),
    'dexed.bass': dict(player='dexed', label='DX7 Bass 1', program=['BASS 1', 14], params={}),
    'dexed.organ': dict(player='dexed', label='DX7 E.Organ', program=['E.ORGAN 1', 16], params={}),
    'dexed.koto': dict(player='dexed', label='DX7 Koto', program=['KOTO', 22], params={}),
    # ---- Surge XT: from its init patch (scene A). Surge names parameters "A Osc 1 ...", "A Filter 1 ...".
    'surge.supersaw': dict(player='surge', label='Supersaw', required=['A Osc 1 Unison Voices'], params={
        'A Osc 1 Unison Voices|Osc 1 Unison Voices': 0.4, 'A Osc 1 Unison Detune|Osc 1 Unison Detune': 0.32,
        'A Filter 1 Cutoff|Filter 1 Cutoff': 0.78, 'A Filter 1 Resonance|Filter 1 Resonance': 0.1,
        'A Amp EG Attack|Amp EG Attack': 0.05, 'A Amp EG Release|Amp EG Release': 0.5, 'A Amp EG Sustain|Amp EG Sustain': 1.0}),
    'surge.supersaw_lead': dict(player='surge', label='Supersaw lead', required=['A Osc 1 Unison Voices'], params={
        'A Osc 1 Unison Voices|Osc 1 Unison Voices': 0.33, 'A Osc 1 Unison Detune|Osc 1 Unison Detune': 0.25,
        'A Filter 1 Cutoff|Filter 1 Cutoff': 0.85, 'A Amp EG Attack|Amp EG Attack': 0.0, 'A Amp EG Release|Amp EG Release': 0.4}),
    'surge.warm_pad': dict(player='surge', label='Warm pad', required=['A Amp EG Attack'], params={
        'A Osc 1 Unison Voices|Osc 1 Unison Voices': 0.2, 'A Osc 1 Unison Detune|Osc 1 Unison Detune': 0.2,
        'A Filter 1 Cutoff|Filter 1 Cutoff': 0.5, 'A Amp EG Attack|Amp EG Attack': 0.6, 'A Amp EG Release|Amp EG Release': 0.62}),
    'surge.reese': dict(player='surge', label='Reese bass', required=['A Osc 1 Unison Voices'], params={
        'A Osc 1 Unison Voices|Osc 1 Unison Voices': 0.14, 'A Osc 1 Unison Detune|Osc 1 Unison Detune': 0.18,
        'A Filter 1 Cutoff|Filter 1 Cutoff': 0.52, 'A Amp EG Attack|Amp EG Attack': 0.0, 'A Amp EG Release|Amp EG Release': 0.3}),
    'surge.saw_bass': dict(player='surge', label='Saw bass', required=['A Filter 1 Cutoff'], params={
        'A Osc 1 Unison Voices|Osc 1 Unison Voices': 0.0, 'A Filter 1 Cutoff|Filter 1 Cutoff': 0.45,
        'A Filter 1 Resonance|Filter 1 Resonance': 0.2, 'A Amp EG Attack|Amp EG Attack': 0.0, 'A Amp EG Release|Amp EG Release': 0.3}),
    'surge.pluck': dict(player='surge', label='Pluck', required=['A Amp EG Sustain'], params={
        'A Osc 1 Unison Voices|Osc 1 Unison Voices': 0.2, 'A Osc 1 Unison Detune|Osc 1 Unison Detune': 0.2,
        'A Filter 1 Cutoff|Filter 1 Cutoff': 0.6, 'A Amp EG Attack|Amp EG Attack': 0.0, 'A Amp EG Decay|Amp EG Decay': 0.42,
        'A Amp EG Sustain|Amp EG Sustain': 0.0, 'A Amp EG Release|Amp EG Release': 0.4}),
    'surge.saw_lead': dict(player='surge', label='Saw lead', required=['A Filter 1 Cutoff'], params={
        'A Osc 1 Unison Voices|Osc 1 Unison Voices': 0.07, 'A Osc 1 Unison Detune|Osc 1 Unison Detune': 0.15,
        'A Filter 1 Cutoff|Filter 1 Cutoff': 0.75, 'A Amp EG Attack|Amp EG Attack': 0.0, 'A Amp EG Release|Amp EG Release': 0.35}),
}

# what each built-in instrument becomes, best first (synths: only in electronic styles unless marked 'any')
ROLE_PATCHES = {
    'acid': ['jc303.acid', 'nekobi.acid', 'tal.acid'],
    'sawbass': ['tal.saw_bass', 'surge.saw_bass', 'jc303.bass', 'nekobi.bass'],
    'reese': ['surge.reese', 'tal.reese'],
    'wobble': [],                                              # LFO-routed wobbles stay built-in
    'fmbass': ['dexed.bass'],
    'chipbass': [], 'sinebass': [], '808': [],                # sub-heavy parts sound best from the built-in engine
    'supersaw': ['surge.supersaw', 'tal.analog_pad'],
    'supersaw_lead': ['surge.supersaw_lead', 'tal.80s_lead'],
    'warmpad': ['tal.analog_pad', 'surge.warm_pad'],
    'stab': ['tal.brass_stab', 'surge.pluck'],
    'pluck_saw': ['tal.pluck', 'surge.pluck'],
    'leadsaw': ['tal.80s_lead', 'surge.saw_lead'],
    'softlead': ['tal.soft_lead'],
    'pluck': ['kars.pluck', 'tal.pluck'],
    'epiano': ['dexed.epiano'], 'clav': ['dexed.clav'], 'marimba': ['dexed.marimba'], 'bell': ['dexed.bells'],
    'steeldrum': ['dexed.steeldrum'], 'kalimba': ['dexed.koto'], 'cowbell': [], 'organ': ['dexed.organ'],
}
ANY_CATEGORY = {'epiano', 'clav', 'marimba', 'steeldrum', 'kalimba', 'fmbass'}   # FM keys also suit funk, city pop, bossa, reggae

# your own saved VST sounds (any plugin): a sound whose name contains one of these words plays that kind of part.
# Sample players (BBC SO, LABS) can only be used this way; for synths it lets e.g. "Serum supersaw" beat the built-in rig.
SOUND_WORDS = {
    'strings': ['strings', 'string', 'ensemble', 'violins', 'cello'], 'violin': ['violin', 'strings'], 'pizz': ['pizz', 'pizzicato'],
    'horn': ['horn', 'horns', 'brass'], 'brass': ['brass', 'horns', 'trumpet', 'trombone'], 'harp': ['harp'],
    'timpani': ['timpani', 'timp'], 'celesta': ['celesta', 'celeste', 'glock', 'glockenspiel'],
    'choir': ['choir', 'voices', 'vox'], 'vox': ['choir', 'voices', 'vox'], 'flute': ['flute', 'woodwind', 'woodwinds', 'piccolo'],
    'piano': ['piano', 'grand'], 'epiano': ['epiano', 'e-piano', 'rhodes', 'wurli', 'wurlitzer'], 'organ': ['organ'],
    'guitar': ['guitar'], 'sax': ['sax', 'saxophone'], 'marimba': ['marimba'], 'bell': ['bell', 'bells'],
    'supersaw': ['supersaw', 'pad'], 'warmpad': ['pad'], 'supersaw_lead': ['supersaw', 'lead'],
    'leadsaw': ['lead'], 'softlead': ['lead'], 'hoover': ['hoover', 'lead'], 'stab': ['stab', 'chords'],
    'pluck': ['pluck'], 'pluck_saw': ['pluck'], 'acid': ['acid', '303'], '808': ['808'],
    'sawbass': ['bass'], 'reese': ['reese', 'bass'], 'fmbass': ['bass'], 'sinebass': ['sub', 'bass'], 'wobble': ['wobble', 'bass'],
}
SAMPLER_ROLES = {k for k in SOUND_WORDS if k in ('strings', 'violin', 'pizz', 'horn', 'brass', 'harp', 'timpani', 'celesta',
                                                    'choir', 'vox', 'flute', 'piano')}

# genre flavour: which plugin family to reach for first, and a tone tweak (shifts filter cutoffs)
STYLE_PREF = {
    'synthwave': ['tal'], 'synthpop': ['tal'], 'electro': ['tal'], 'vaporwave': ['tal', 'dexed'], 'eurodance': ['tal', 'surge'],
    'city_pop': ['dexed', 'tal'], 'house': ['tal'], 'deep_house': ['tal', 'dexed'], 'ukgarage': ['tal'],
    'trance': ['surge'], 'progressive_house': ['surge'], 'bigroom': ['surge'], 'hardstyle': ['surge'], 'future_bass': ['surge'],
    'dnb': ['surge'], 'jungle': ['surge'], 'hyperpop': ['surge'],
    'acid_house': ['jc303', 'nekobi'], 'techno': ['jc303', 'nekobi'], 'psytrance': ['jc303', 'surge'], 'minimal': ['jc303'],
}
STYLE_TONE = {'lofi': -0.12, 'vaporwave': -0.1, 'downtempo': -0.08, 'deep_house': -0.08, 'ambient': -0.1, 'boombap': -0.08,
              'trance': 0.08, 'bigroom': 0.1, 'hyperpop': 0.12, 'eurodance': 0.06, 'hardstyle': 0.08, 'future_bass': 0.06}


# ----------------------------------------------------------------------------- plugin lookup
_CACHE = {'t': 0, 'plugins': None}


def plugins_on_disk(refresh=False):
    if refresh or _CACHE['plugins'] is None or time.time() - _CACHE['t'] > 30:
        _CACHE.update(t=time.time(), plugins=vsthost.find_plugins())
    return _CACHE['plugins']


def player_path(pid, plugins=None):
    plugins = plugins if plugins is not None else plugins_on_disk()
    m = PLAYERS[pid]['match']
    bad = vsthost.broken()
    hits = [p['path'] for p in plugins if m(p['path']) and p['path'] not in bad]
    hits.sort(key=lambda p: (not p.startswith(vsthost.PLUGIN_DIR), len(p)))
    return hits[0] if hits else None


def _sid(patch_id, tone):
    t = '' if abs(tone) < 1e-6 else f"_t{int(round(tone * 100)):+d}".replace('+', 'p').replace('-', 'm')
    return 'auto_' + patch_id.replace('.', '_') + t


def recipe_for(patch_id, tone=0.0):
    p = PATCHES[patch_id]
    params = {}
    for k, v in p['params'].items():
        if tone and isinstance(v, float) and 'cutoff' in k.lower():
            v = max(0.02, min(1.0, v + tone))
        params[k] = v
    r = dict(params=params, required=list(p.get('required', [])))
    if p.get('program'):
        r['program'] = p['program']
    return r


def ensure_sound(patch_id, path, tone=0.0):
    """Write (or refresh) the saved-sound file the renderer uses for this patch."""
    p = PATCHES[patch_id]
    sid = _sid(patch_id, tone)
    os.makedirs(vsthost.SOUNDS, exist_ok=True)
    fn = os.path.join(vsthost.SOUNDS, sid + '.json')
    data = dict(name=f"{PLAYERS[p['player']]['name']} · {p['label']}", path=path,
                plugin_label=os.path.splitext(os.path.basename(path))[0], auto=True, patch=patch_id,
                state={'recipe': recipe_for(patch_id, tone)})
    try:
        with open(fn) as f:
            old = json.load(f)
        if not old.get('auto'):
            return sid                         # never overwrite a sound you made yourself
        if all(old.get(k) == data[k] for k in ('path', 'state', 'name')):
            return sid
    except Exception:
        pass
    data['created'] = int(time.time())
    with open(fn, 'w') as f:
        json.dump(data, f)
    return sid


def plugin_by_name(name, plugins=None):
    plugins = plugins if plugins is not None else plugins_on_disk()
    bad = vsthost.broken()
    hits = [p for p in plugins if p['name'] == name and p['path'] not in bad]
    hits.sort(key=lambda p: (not p['path'].startswith(vsthost.PLUGIN_DIR), len(p['path'])))
    return hits[0]['path'] if hits else None


def ensure_plain_sound(name):
    """A plugin's own default sound (for instruments Studio Lab has no patches for)."""
    path = plugin_by_name(name)
    sid = 'auto_plain_' + re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')[:40]
    fn = os.path.join(vsthost.SOUNDS, sid + '.json')
    os.makedirs(vsthost.SOUNDS, exist_ok=True)
    data = dict(name=f'{name} (default sound)', path=path, plugin_label=name, auto=True, state={})
    try:
        with open(fn) as f:
            old = json.load(f)
        if not old.get('auto') or old.get('path') == path:
            return sid
    except Exception:
        pass
    with open(fn, 'w') as f:
        json.dump(data, f)
    return sid


def layer_choices(layer, plugins=None, instruments=None):
    """Sound-dropdown choices from installed plugins for one part: genre patches first, then other instrument plugins."""
    from .instruments import ROLE_CHOICES
    plugins = plugins if plugins is not None else plugins_on_disk()
    out, seen = [], set()
    suits = [c for inst in ROLE_CHOICES.get(layer, []) for c in ROLE_PATCHES.get(inst, [])]
    rest = [c for c in PATCHES if c not in suits and (layer == 'bass') == ('bass' in c or 'acid' in c or 'reese' in c)]
    for c in suits + rest:
        if c in seen:
            continue
        seen.add(c)
        if player_path(PATCHES[c]['player'], plugins):
            out.append(dict(id='vstp:' + c, name=f"{PLAYERS[PATCHES[c]['player']]['name']} · {PATCHES[c]['label']}",
                            group='Installed plugins'))
    known = lambda path: any(pl['match'](path) for pl in PLAYERS.values() if pl['kind'] == 'synth')
    for name in sorted(instruments or []):
        path = plugin_by_name(name, plugins)
        if path and not known(path):
            out.append(dict(id='vstd:' + name, name=f'{name} (default sound)', group='Installed plugins'))
    return out


def _user_sound(role, sounds):
    """First of your own saved VST sounds whose name says it plays this kind of part (best word first)."""
    words = SOUND_WORDS.get(role)
    if not words:
        return None
    mine = [x for x in sounds if x.get('ok') and not x.get('auto')]
    for w in words:
        for s in mine:
            if re.search(r'(?<![a-z0-9])' + re.escape(w) + r'(?![a-z0-9])', s['name'].lower()):
                return s
    return None


def ordered(cands, style):
    """Candidates with the genre's preferred plugin families first (stable otherwise); genre-locked patches dropped."""
    cands = [c for c in cands if not PATCHES[c].get('only') or style in PATCHES[c]['only']]
    pref = STYLE_PREF.get(style, [])
    rank = {c: i for i, c in enumerate(cands)}
    return sorted(cands, key=lambda c: (pref.index(PATCHES[c]['player']) if PATCHES[c]['player'] in pref else len(pref), rank[c]))


def choose(inst, style, category, plugins=None, sounds=None):
    """-> (kind, id, label) for this part, or None to keep the built-in sound."""
    plugins = plugins if plugins is not None else plugins_on_disk()
    s = _user_sound(inst, sounds if sounds is not None else vsthost.list_sounds())
    if s:
        return ('user', s['id'], s['name'])
    cands = list(ROLE_PATCHES.get(inst, []))
    if not cands or (category != 'Electronic' and inst not in ANY_CATEGORY):
        return None
    for c in ordered(cands, style):
        path = player_path(PATCHES[c]['player'], plugins)
        if path:
            return ('patch', c, path)
    return None


def assign(st, opts, log=None):
    """Swap parts to rig sounds (in place). Parts you picked yourself are left alone."""
    from .compose import MELODIC_ROLES
    style, cat = getattr(opts, 'style', st.get('name')), st.get('category')
    tone = STYLE_TONE.get(style, 0.0) + 0.06 * float(getattr(opts, 'brightness', 0.0) or 0.0)
    plugins = plugins_on_disk()
    if not plugins:
        return {}
    sounds = vsthost.list_sounds()
    used = {}
    for t in st['tracks']:
        inst = t['inst']
        if t['layer'] not in MELODIC_ROLES or t.get('user_pick') or inst.startswith(('vst:', 'user:')):
            continue
        base = inst[3:] if inst.startswith('sf:') else inst
        pick = choose(base, style, cat, plugins, sounds)
        if not pick:
            continue
        kind, ident, extra = pick
        sid = ident if kind == 'user' else ensure_sound(ident, extra, tone)
        t['rig_from'] = inst
        t['fallback'] = t.get('fallback') if inst.startswith('sf:') and t.get('fallback') else base
        t['inst'] = 'vst:' + sid
        t['p'] = {}
        used[t['layer']] = extra if kind == 'user' else f"{PLAYERS[PATCHES[ident]['player']]['name']} · {PATCHES[ident]['label']}"
    st['rig'] = used
    return used


def plan(style, category=None):
    """What the rig would use for a style right now, and what's missing (for the UI)."""
    from .styles import STYLES
    from .compose import MELODIC_ROLES
    s = STYLES[style]
    category = category or s['category']
    plugins = plugins_on_disk(refresh=True)
    sounds = vsthost.list_sounds()
    rows, missing = [], set()
    for t in s['tracks']:
        if t['layer'] not in MELODIC_ROLES:
            continue
        inst = t['inst'][3:] if t['inst'].startswith('sf:') else t['inst']
        pick = choose(inst, style, category, plugins, sounds)
        row = dict(layer=t['layer'], inst=inst, uses=None)
        if pick:
            kind, ident, extra = pick
            row['uses'] = extra if kind == 'user' else f"{PLAYERS[PATCHES[ident]['player']]['name']} · {PATCHES[ident]['label']}"
        elif inst in SAMPLER_ROLES and category == 'Orchestral':
            row['hint'] = 'save a BBC Symphony Orchestra / LABS sound named after this part (e.g. "BBC ' + inst + '")'
        cands = ordered(ROLE_PATCHES.get(inst, []), style) if (category == 'Electronic' or inst in ANY_CATEGORY) else []
        using = PATCHES[pick[1]]['player'] if pick and pick[0] == 'patch' else None
        for c in cands:                                        # better plugins than the one in use, best first
            pl = PATCHES[c]['player']
            if pl == using:
                break
            if not player_path(pl, plugins):
                row.setdefault('ideal', PLAYERS[pl]['name'])
                if PLAYERS[pl].get('pack'):
                    missing.add(PLAYERS[pl]['pack'])
                    break
        rows.append(row)
    return dict(style=style, parts=rows, missing_packs=sorted(missing))
