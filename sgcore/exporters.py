"""Exports: Standard MIDI file, LMMS project (.mmp), Waveform / Tracktion edit (.tracktionedit)."""
import os
import struct

from .instruments import DRUMS, GM_PROGRAM, INSTRUMENT_INFO

GM_DRUM = {'kick': 36, 'chipkick': 36, 'snare': 38, 'chipsnare': 38, 'clap': 39, 'chat': 42, 'chiphat': 42,
           'ohat': 46, 'shaker': 70, 'ride': 51, 'rim': 37, 'crash': 49, 'tom': 45, 'cowbell808': 56,
           'conga': 63, 'taiko': 41, 'timp': 43, 'snap': 39, 'tamb': 54, 'woodblock': 76}


def _vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def _track_chunk(events, name):
    data = b'\x00\xff\x03' + _vlq(len(name.encode())) + name.encode()
    events.sort(key=lambda e: (e[0], e[1]))
    last = 0
    for tick, _, msg in events:
        data += _vlq(tick - last) + msg
        last = tick
    data += b'\x00\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(data)) + data


def write_midi(path, song):
    """Type-1 MIDI: one track per part, General MIDI programs chosen to match each built-in instrument."""
    ppq = 480
    st = song['st']
    tcfgs = {t['name']: t for t in st['tracks']}
    chunks = []
    tempo = int(60_000_000 / song['bpm'])
    meta = [(0, 0, b'\xff\x51\x03' + tempo.to_bytes(3, 'big')), (0, 0, b'\xff\x58\x04\x04\x02\x18\x08')]
    k = song['key']                                   # key signature: home note + major/minor quality (DAWs show it)
    minor = (k.scale[2] - k.scale[0]) % 12 == 3
    sf = (((k.root + 3) % 12 if minor else k.root) * 7) % 12
    sf = sf - 12 if sf > 6 else sf
    meta.append((0, 0, b'\xff\x59\x02' + struct.pack('bB', sf, 1 if minor else 0)))
    for s in song['sections']:
        txt = s['name'].encode()
        meta.append((int(s['bar'] * 4 * ppq), 0, b'\xff\x06' + _vlq(len(txt)) + txt))
    chunks.append(_track_chunk(meta, 'Tempo & markers'))
    groups = {}
    for e in song['events']:
        groups.setdefault(e.track, []).append(e)
    drum_evs = []
    ch = 0
    for t in st['tracks']:
        name = t['name']
        evs = groups.get(name)
        if not evs:
            continue
        if t['inst'] in DRUMS:
            note = GM_DRUM.get(t['inst'], 37)
            for e in evs:
                tk = int(round(e.beat * ppq))
                v = max(1, min(127, int(e.vel * 110)))
                drum_evs.append((tk, 1, bytes([0x99, note, v])))
                drum_evs.append((tk + ppq // 8, 0, bytes([0x89, note, 0])))
            continue
        if ch == 9:
            ch += 1
        chn = ch % 16
        out = [(0, 0, bytes([0xC0 | chn, GM_PROGRAM.get(t['inst'], 0)]))]
        for e in evs:
            tk = int(round(e.beat * ppq))
            te = tk + max(1, int(round(e.dur * ppq)))
            v = max(1, min(127, int(e.vel * 110)))
            m = max(0, min(127, int(e.midi)))
            out.append((tk, 1, bytes([0x90 | chn, m, v])))
            out.append((te, 0, bytes([0x80 | chn, m, 0])))
        rec = (song.get('plugin_recs') or {}).get(name)
        hint = f" -> {rec['picks'][0]['name']}" if rec and rec['picks'] else ''
        chunks.append(_track_chunk(out, f"{name} ({INSTRUMENT_INFO.get(t['inst'], t['inst'])}){hint}"))
        ch += 1
    if drum_evs:
        chunks.append(_track_chunk(drum_evs, 'Drums'))
    vocal = song.get('vocal') or []
    if vocal and 'vocal' not in tcfgs:              # guide melody for a singer (General MIDI "Voice Oohs")
        chn = ch % 16 if ch % 16 != 9 else 10
        out = [(0, 0, bytes([0xC0 | chn, 53]))]
        for e in vocal:
            tk = int(round(e.beat * ppq))
            te = tk + max(1, int(round(e.dur * ppq)))
            v = max(1, min(127, int(e.vel * 110)))
            out.append((tk, 0, b'\xff\x05\x02la'))          # lyric placeholder, shown by most DAWs
            out.append((tk, 1, bytes([0x90 | chn, int(e.midi), v])))
            out.append((te, 0, bytes([0x80 | chn, int(e.midi), 0])))
        chunks.append(_track_chunk(out, 'Vocal guide (sing this)'))
    with open(path, 'wb') as f:
        f.write(b'MThd' + struct.pack('>IHHH', 6, 1, len(chunks), ppq))
        for c in chunks:
            f.write(c)
    return path


def write_part_midis(folder, song):
    """One small MIDI file per part (drag-and-drop friendly). Returns {part: path}."""
    import copy
    os.makedirs(folder, exist_ok=True)
    out = {}
    st = song['st']
    drum_names = [t['name'] for t in st['tracks'] if t['inst'] in DRUMS]
    parts = [t['name'] for t in st['tracks'] if t['inst'] not in DRUMS]
    groups = [(p, [p]) for p in parts] + ([('drums', drum_names)] if drum_names else [])
    for label, names in groups:
        evs = [e for e in song['events'] if e.track in names]
        if not evs:
            continue
        sub = dict(song)
        sub['events'] = evs
        sub['st'] = dict(st, tracks=[t for t in st['tracks'] if t['name'] in names])
        path = os.path.join(folder, f"{song['style']}_{song['bpm']}bpm_{label}.mid")
        write_midi(path, sub)
        out[label] = path
    if song.get('vocal') and 'vocal' not in parts:
        sub = dict(song, events=[], st=dict(st, tracks=[]))
        path = os.path.join(folder, f"{song['style']}_{song['bpm']}bpm_vocal_guide.mid")
        write_midi(path, sub)
        out['vocal guide'] = path
    return out


# Suggested replacement instruments for a DAW (free options first)
SUGGEST = {
    'strings': 'String ensemble - BBC Symphony Orchestra Discover (free) or Spitfire LABS "Strings"; LMMS: Sf2 Player + GM 48',
    'violin': 'Solo violin/cello - Spitfire LABS "Solo Cello"/"Soft Piano"-style solo patches; GM 40 Violin',
    'pizz': 'Pizzicato strings - BBC SO Discover "Strings pizzicato"; GM 45',
    'harp': 'Harp - BBC SO Discover "Harp"; GM 46',
    'horn': 'French horns - BBC SO Discover "Horns"; GM 60',
    'brass': 'Brass section - BBC SO Discover "Trumpets/Trombones"; GM 61',
    'choir': 'Choir - Spitfire LABS "Choir"; GM 52 Choir Aahs',
    'timpani': 'Timpani - BBC SO Discover "Timpani"; GM 47',
    'celesta': 'Celesta - BBC SO Discover "Celeste"; GM 8',
    'piano': 'Piano - Spitfire LABS "Soft Piano" or any free grand; GM 0',
    'softlead': 'Flute - BBC SO Discover "Flute"; GM 73',
}


def write_orchestration_notes(path, song):
    st = song['st']
    lines = [f"Orchestration guide - {song['style']} in {song['key'].name()}, {song['bpm']} BPM", '',
             st.get('gm_hint', ''), '',
             'The MIDI file has one track per part with a matching General MIDI instrument already set.',
             'For realistic sound, load each MIDI track onto a sample library in your DAW:', '']
    for t in st['tracks']:
        if t['inst'] in DRUMS:
            if t['inst'] in ('taiko', 'timp'):
                lines.append(f"  {t['name']:<8} -> Taiko / timpani: BBC SO Discover percussion, or any free cinematic drum kit")
            continue
        lines.append(f"  {t['name']:<8} ({INSTRUMENT_INFO.get(t['inst'], t['inst'])}) -> {SUGGEST.get(t['inst'], 'GM program %d' % GM_PROGRAM.get(t['inst'], 0))}")
    lines += ['', 'Tips: keep strings on long reverb (hall, 2.5-3.5 s), pan violins left / celli right,',
              'and ride the modulation wheel (CC1) for dynamics if your library supports it.']
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return path


# =============================================================================
#  LMMS (.mmp) - uses LMMS's own built-in synths/samples so every sound is editable inside LMMS
# =============================================================================
import math
from xml.sax.saxutils import quoteattr

# (wave, vol, coarse, fine_l, fine_r, pan) waves: 0 sine 1 tri 2 saw 3 square 4 moogsaw 5 exp 6 noise
#  env: (attack, decay, sustain, release) seconds ; filt: (type, cutoff, res) ; fenv: (amount, decay s)
LMMS_PATCH = {
    'sawbass':  dict(osc=[(2, 60, 0, 0, 0, 0), (3, 35, -12, 0, 0, 0), (0, 50, 0, 0, 0, 0)], env=(0.003, 0.2, 0.6, 0.05), filt=(0, 900, 1.4), fenv=(0.45, 0.15)),
    'reese':    dict(osc=[(2, 50, 0, -15, 15, 0), (2, 50, 0, 10, -10, 0), (0, 70, 0, 0, 0, 0)], env=(0.01, 0.3, 0.9, 0.1), filt=(0, 750, 1.0)),
    '808':      dict(osc=[(0, 100, 0, 0, 0, 0), (1, 12, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.002, 1.4, 0.0, 0.05)),
    'sinebass': dict(osc=[(0, 100, 0, 0, 0, 0), (1, 10, 12, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.006, 0.5, 0.75, 0.08), filt=(0, 700, 0.7)),
    'chipbass': dict(osc=[(1, 100, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0)], env=(0.001, 0.1, 1.0, 0.02)),
    'wobble':   dict(osc=[(2, 45, 0, -6, 6, 0), (3, 25, 12, 0, 0, 0), (0, 60, -12, 0, 0, 0)], env=(0.005, 0.1, 1.0, 0.05), filt=(0, 500, 1.8), lfo=True),
    'fmbass':   dict(osc=[(0, 90, 0, 0, 0, 0), (0, 70, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)], modalgo=0, env=(0.003, 0.25, 0.7, 0.06), filt=(0, 2500, 1.0)),
    'supersaw': dict(osc=[(2, 40, 0, -12, 12, -30), (2, 40, 0, 12, -12, 30), (2, 30, 12, -7, 7, 0)], env=(0.2, 0.6, 0.85, 0.5), filt=(0, 3000, 0.8)),
    'supersaw_lead': dict(osc=[(2, 40, 0, -14, 14, -30), (2, 40, 0, 14, -14, 30), (2, 30, 12, -7, 7, 0)], env=(0.005, 0.3, 0.8, 0.2), filt=(0, 7000, 0.8)),
    'warmpad':  dict(osc=[(2, 40, 0, -7, 7, -40), (2, 40, 0, 7, -7, 40), (1, 40, 0, 0, 0, 0)], env=(1.2, 1.0, 0.85, 2.0), filt=(0, 1100, 0.9)),
    'strings':  dict(osc=[(2, 40, 0, -10, 10, -40), (2, 40, 0, 10, -10, 40), (2, 30, 12, -5, 5, 0)], env=(0.35, 0.5, 0.9, 0.7), filt=(0, 3200, 0.7)),
    'stab':     dict(osc=[(2, 50, 0, -5, 5, 0), (2, 50, 0, 5, -5, 0), (3, 25, 0, 0, 0, 0)], env=(0.002, 0.22, 0.2, 0.08), filt=(0, 1200, 1.2), fenv=(0.5, 0.12)),
    'pluck_saw': dict(osc=[(2, 60, 0, 0, 0, 0), (3, 30, 0, 4, -4, 0), (0, 0, 0, 0, 0, 0)], env=(0.002, 0.3, 0.15, 0.12), filt=(0, 1200, 1.3), fenv=(0.6, 0.18)),
    'epiano':   dict(osc=[(0, 100, 0, 0, 0, 0), (0, 35, 0, 0, 0, 0), (0, 10, 24, 0, 0, 0)], modalgo=0, env=(0.002, 1.4, 0.15, 0.25)),
    'piano':    dict(osc=[(1, 70, 0, 0, 0, 0), (0, 40, 12, 0, 0, 0), (2, 12, 0, 0, 0, 0)], env=(0.002, 1.2, 0.1, 0.15), filt=(0, 5000, 0.7)),
    'organ':    dict(osc=[(0, 70, 0, 0, 0, 0), (0, 45, 12, 0, 0, 0), (0, 30, 19, 0, 0, 0)], env=(0.004, 0.05, 1.0, 0.05)),
    'pluck':    dict(osc=[(2, 50, 0, 0, 0, 0), (1, 50, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.001, 0.6, 0.0, 0.2), filt=(0, 1800, 0.9), fenv=(0.5, 0.15)),
    'guitar':   dict(osc=[(2, 50, 0, -3, 3, 0), (3, 30, 0, 3, -3, 0), (0, 0, 0, 0, 0, 0)], env=(0.002, 0.7, 0.25, 0.1), filt=(0, 2600, 1.1), fenv=(0.4, 0.1)),
    'bell':     dict(osc=[(0, 100, 0, 0, 0, 0), (0, 45, 22, 0, 0, 0), (0, 0, 0, 0, 0, 0)], modalgo=0, env=(0.002, 1.6, 0.0, 0.8)),
    'celesta':  dict(osc=[(0, 100, 0, 0, 0, 0), (0, 30, 24, 0, 0, 0), (0, 0, 0, 0, 0, 0)], modalgo=0, env=(0.002, 1.8, 0.0, 0.8)),
    'brass':    dict(osc=[(2, 50, 0, -5, 5, 0), (2, 50, 0, 5, -5, 0), (2, 20, 12, 0, 0, 0)], env=(0.03, 0.3, 0.8, 0.15), filt=(0, 1500, 0.9), fenv=(0.35, 0.3)),
    'horn':     dict(osc=[(2, 50, 0, -4, 4, 0), (1, 50, 0, 4, -4, 0), (0, 0, 0, 0, 0, 0)], env=(0.06, 0.3, 0.85, 0.25), filt=(0, 1200, 0.8)),
    'vox':      dict(osc=[(2, 70, 0, -4, 4, 0), (6, 6, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.012, 0.15, 0.75, 0.08), filt=(14, 1000, 0.5)),
    'choir':    dict(osc=[(2, 50, 0, -10, 10, -40), (2, 50, 0, 10, -10, 40), (6, 4, 0, 0, 0, 0)], env=(0.4, 0.5, 0.9, 0.9), filt=(14, 1000, 0.5)),
    'cowbell':  dict(osc=[(3, 60, 0, 0, 0, 0), (3, 60, 7, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.001, 0.25, 0.0, 0.1), filt=(2, 1200, 1.5)),
    'leadsaw':  dict(osc=[(2, 50, 0, -6, 6, 0), (2, 50, 0, 6, -6, 0), (3, 25, -12, 0, 0, 0)], env=(0.008, 0.3, 0.7, 0.18), filt=(0, 4500, 1.0)),
    'hoover':   dict(osc=[(2, 45, 0, -25, 25, -40), (2, 45, 0, 25, -25, 40), (3, 30, -12, 0, 0, 0)], env=(0.01, 0.3, 0.85, 0.2), filt=(0, 4500, 0.8)),
    'softlead': dict(osc=[(1, 80, 0, 0, 0, 0), (0, 30, 12, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.07, 0.5, 0.8, 0.4)),
    'chip':     dict(osc=[(3, 80, 0, 0, 0, 0), (3, 0, 0, 0, 0, 0), (3, 0, 0, 0, 0, 0)], env=(0.002, 0.25, 0.6, 0.03)),
    'violin':   dict(osc=[(2, 80, 0, -3, 3, 0), (2, 20, 12, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.08, 0.3, 0.9, 0.25), filt=(0, 3800, 0.9)),
    'harp':     dict(osc=[(1, 80, 0, 0, 0, 0), (0, 40, 12, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.001, 1.5, 0.0, 1.0)),
    'pizz':     dict(osc=[(1, 80, 0, 0, 0, 0), (2, 20, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.001, 0.2, 0.0, 0.1), filt=(0, 2000, 0.8)),
    'logdrum':  dict(osc=[(0, 100, 0, 0, 0, 0), (1, 30, 0, 0, 0, 0), (0, 15, 12, 0, 0, 0)], env=(0.001, 0.35, 0.0, 0.1), filt=(0, 1500, 0.8)),
    'marimba':  dict(osc=[(0, 100, 0, 0, 0, 0), (0, 25, 24, 0, 0, 0), (1, 10, 12, 0, 0, 0)], env=(0.001, 0.5, 0.0, 0.3)),
    'kalimba':  dict(osc=[(0, 100, 0, 0, 0, 0), (1, 20, 12, 0, 0, 0), (0, 10, 31, 0, 0, 0)], env=(0.001, 0.9, 0.0, 0.5)),
    'steeldrum': dict(osc=[(0, 90, 0, 0, 0, 0), (0, 60, 12, 0, 0, 0), (1, 25, 19, 0, 0, 0)], env=(0.001, 0.7, 0.0, 0.4)),
    'sax':      dict(osc=[(2, 60, 0, -3, 3, 0), (3, 40, 0, 3, -3, 0), (6, 4, 0, 0, 0, 0)], env=(0.04, 0.3, 0.85, 0.12), filt=(0, 2400, 1.6)),
    'flute':    dict(osc=[(0, 90, 0, 0, 0, 0), (1, 20, 12, 0, 0, 0), (6, 3, 0, 0, 0, 0)], env=(0.06, 0.3, 0.85, 0.2), filt=(0, 5000, 0.7)),
    'clav':     dict(osc=[(3, 60, 0, 0, 0, 0), (2, 40, 12, 0, 0, 0), (0, 0, 0, 0, 0, 0)], env=(0.001, 0.25, 0.0, 0.05), filt=(0, 2000, 1.4), fenv=(0.5, 0.08)),
    'timpani':  dict(osc=[(0, 100, 0, 0, 0, 0), (0, 25, 7, 0, 0, 0), (6, 3, 0, 0, 0, 0)], env=(0.002, 1.8, 0.0, 0.5), filt=(0, 1500, 0.7)),
}
LMMS_SAMPLES = {
    'default': dict(snare='drums/snare01.ogg', clap='drums/clap01.ogg', chat='drums/hihat_closed01.ogg', ohat='drums/hihat_opened01.ogg',
                    shaker='drums/shaker01.ogg', ride='drums/ride01.ogg', rim='drums/rim01.ogg', crash='drums/crash01.ogg',
                    tom='drums/tom01.ogg', cowbell808='drumsynth/tr808/Cowbell.ds', conga='drumsynth/latin/bongo_l.ds',
                    taiko='drumsynth/latin/taiko.ds', timp='drums/tom_low01.ogg', snap='drums/clap02.ogg',
                    tamb='drumsynth/linn/linn_tamb.ds', woodblock='drums/wood01.ogg', chipsnare='drums/snare_electro01.ogg',
                    chiphat='drums/hihat_closed02.ogg'),
    '808': dict(snare='drumsynth/tr808/Snare.ds', clap='drumsynth/tr808/Handclap.ds', chat='drumsynth/tr808/Hat_c.ds',
                ohat='drumsynth/tr808/Hat_o.ds', ride='drumsynth/tr808/Ride.ds', rim='drumsynth/tr808/Rimshot.ds', tom='drumsynth/tr808/Tom_lo.ds'),
    '909': dict(snare='drumsynth/tr909/Snare.ds', clap='drumsynth/tr909/Clap.ds', chat='drumsynth/tr909/Hat-c.ds', ohat='drumsynth/tr909/Hat-o.ds'),
}
# measured RMS (dBFS) of each LMMS patch at vol=50, rendered in LMMS 1.2.2 - used to level-match tracks
LMMS_CAL = {'sawbass': -19.4, 'reese': -13.5, '808': -11.5, 'sinebass': -11.5, 'chipbass': -11.5, 'wobble': -5.4, 'fmbass': -14.7, 'supersaw': -18.5, 'supersaw_lead': -18.5, 'warmpad': -34.1, 'strings': -19.3, 'stab': -24.5, 'pluck_saw': -25.7, 'epiano': -12.3, 'piano': -16.6, 'organ': -10.8, 'pluck': -26.3, 'guitar': -20.4, 'bell': -11.5, 'celesta': -11.2, 'brass': -16.9, 'horn': -16.1, 'vox': -37.0, 'choir': -35.0, 'cowbell': -23.2, 'leadsaw': -16.3, 'hoover': -15.7, 'softlead': -13.8, 'chip': -13.6, 'violin': -14.6, 'harp': -13.7, 'pizz': -25.3, 'timpani': -12.0, 'acid': -13.7, 'kick': -18.1, 'chipkick': -20.1, 'snare': -25.9, 'clap': -28.5, 'chat': -31.8, 'ohat': -22.3, 'shaker': -32.5, 'ride': -24.7, 'rim': -27.1, 'tom': -22.3, 'cowbell808': -32.1, 'conga': -27.9, 'taiko': -25.7, 'timp': -24.6, 'chipsnare': -27.1, 'chiphat': -25.9, 'crash': -31.3}
LMMS_LAYER_DB = {'kick': 0, 'snare': -3, 'top': -9, 'bass': -1, 'chords': -6, 'pad': -8, 'arp': -9, 'lead': -4, 'fx': -12}


def _lmms_vol(t):
    rms = LMMS_CAL.get(t['inst'], -18.0)
    gain = max(-24.0, min(6.0, -18.0 - rms)) + LMMS_LAYER_DB.get(t['layer'], -8) - 10.0
    return int(max(3, min(200, round(50 * 10 ** (gain / 20)))))

ENV_ATTRS = 'lspd_denominator="4" pdel="0" userwavefile="" x100="0" lpdel="0" hold="0" lspd_syncmode="0" ctlenvamt="0" lspd_numerator="4"'


def _knob(sec):
    return round(min(2.0, math.sqrt(max(sec, 0.0) / 5.0)), 4)


def _env_xml(tag, amt, att, dec, sus, rel, lfo=None):
    dk = _knob(dec) / max(1e-3, (1 - sus)) if sus < 1 else 0.5
    lfo_amt, lfo_spd, lfo_shp = lfo or (0, 0.1, 0)
    return (f'<{tag} {ENV_ATTRS} amt="{amt}" att="{_knob(att)}" dec="{min(2.0, round(dk, 4))}" sustain="{sus}" '
            f'rel="{_knob(rel)}" latt="0" lamt="{lfo_amt}" lspd="{lfo_spd}" lshp="{lfo_shp}"/>')


def _has_user_drum(inst):
    from .usersounds import SLOT_FOR, path as upath
    return bool(SLOT_FOR.get(inst) and upath('drums', SLOT_FOR[inst]))


def _instrument_xml(tcfg, kit, spb):
    inst = tcfg['inst']
    name = tcfg['name']
    if inst in ('kick', 'chipkick') and not (kit.get('_user_drums') and _has_user_drum(inst)):
        k = dict(kit.get('kick', {}))
        pitch = k.get('pitch', 48)
        start = pitch + k.get('punch', 120) * (1.6 if inst == 'chipkick' else 1)
        decay = int(min(1500, 1000 * k.get('len', 0.5) * (0.4 if inst == 'chipkick' else 0.8)))
        dist = min(60, k.get('drive', 1.6) * 3)
        return ('<instrument name="kicker"><kicker version="1" startnote="0" endnote="0" decay_syncmode="0" decay_numerator="4" '
                f'decay_denominator="4" startfreq="{start:.0f}" endfreq="{pitch:.0f}" decay="{decay}" dist="{dist:.1f}" distend="{dist / 2:.1f}" '
                f'gain="1" env="0.163" noise="0" click="{min(1, k.get("click", 0.3) + 0.1):.2f}" slope="0.06"/></instrument>'), None
    if inst.startswith('sf:'):
        from . import soundfont as sfm
        src = sfm.library_path()
        bank, prog = sfm.SAMPLED.get(inst[3:], (0, 0))[:2]
        return (f'<instrument name="sf2player"><sf2player src={quoteattr(src or "")} bank="{bank}" patch="{prog}" gain="1" '
                'reverbOn="0" reverbRoomSize="0.2" reverbDamping="0" reverbWidth="0.5" reverbLevel="0.9" chorusOn="0" '
                'chorusNum="3" chorusLevel="2" chorusSpeed="0.3" chorusDepth="8"/></instrument>'), dict(env=None)
    if inst.startswith('user:'):
        from .usersounds import path as upath
        src = upath('inst', inst[5:]) or ''
        return (f'<instrument name="audiofileprocessor"><audiofileprocessor src={quoteattr(src)} amp="100" interp="1" reversed="0" '
                'looped="0" sframe="0" lframe="0" eframe="1" stutter="0"/></instrument>'), dict(env=(0.003, 0.3, 0.9, 0.15))
    if inst in DRUMS and kit.get('_user_drums'):
        from .usersounds import SLOT_FOR, path as upath
        src = upath('drums', SLOT_FOR.get(inst, '')) if SLOT_FOR.get(inst) else None
        if src:
            return (f'<instrument name="audiofileprocessor"><audiofileprocessor src={quoteattr(src)} amp="100" interp="1" reversed="0" '
                    'looped="0" sframe="0" lframe="0" eframe="1" stutter="0"/></instrument>'), None
    if inst in DRUMS:
        kitname = kit.get('_name', 'default')
        src = LMMS_SAMPLES.get(kitname, {}).get(inst) or LMMS_SAMPLES['default'].get(inst, 'drums/snare01.ogg')
        return (f'<instrument name="audiofileprocessor"><audiofileprocessor src={quoteattr(src)} amp="100" interp="1" reversed="0" '
                'looped="0" sframe="0" lframe="0" eframe="1" stutter="0"/></instrument>'), None
    if inst == 'acid':
        return ('<instrument name="lb302"><lb302 vcf_cut="0.6" vcf_res="0.85" vcf_mod="0.7" vcf_dec="0.15" shape="0" dist="0.2" '
                'slide_dec="0.6" slide="0" dead="0" db24="0"/></instrument>'), dict(env=None)
    patch = LMMS_PATCH.get(inst, LMMS_PATCH['pluck_saw'])
    a = []
    for i, (w, v, c, fl, fr, pn) in enumerate(patch['osc']):
        a.append(f'vol{i}="{v}" pan{i}="{pn}" coarse{i}="{c}" finel{i}="{fl}" finer{i}="{fr}" phoffset{i}="0" '
                 f'stphdetun{i}="{abs(fl) * 3 % 360}" wavetype{i}="{w}" userwavefile{i}=""')
    mod = patch.get('modalgo', 2)
    xml = (f'<instrument name="tripleoscillator"><tripleoscillator {" ".join(a)} modalgo1="{mod}" modalgo2="2" modalgo3="2"/>'
           '</instrument>')
    return xml, patch


def _eldata_xml(patch, spb):
    if not patch or patch.get('env') is None:
        return ('<eldata fwet="0" ftype="0" fcut="14000" fres="0.5">' + _env_xml('elvol', 0, 0, 0.5, 0.5, 0.1) +
                _env_xml('elcut', 0, 0, 0.5, 0.5, 0.1) + _env_xml('elres', 0, 0, 0.5, 0.5, 0.1) + '</eldata>')
    att, dec, sus, rel = patch['env']
    ft, fc, fr = patch.get('filt', (0, 14000, 0.5))
    fwet = 1 if 'filt' in patch else 0
    famt, fdec = patch.get('fenv', (0, 0.5))
    lfo = None
    if patch.get('lfo'):
        lfo = (0.8, round(min(1.0, max(0.001, spb / 2 / 20)), 4), 0)  # 1/8-note wobble
    return (f'<eldata fwet="{fwet}" ftype="{ft}" fcut="{fc}" fres="{fr}">' + _env_xml('elvol', 1, att, dec, sus, rel) +
            _env_xml('elcut', famt, 0.0, fdec, 0.0, 0.1, lfo) + _env_xml('elres', 0, 0, 0.5, 0.5, 0.1) + '</eldata>')


def write_lmms(path, song):
    """LMMS 1.2+ project. Every part is an LMMS instrument track using LMMS's built-in synths and drum samples,
    one pattern per song section, a mixer with reverb/delay send channels and kick-triggered sidechain ducking."""
    st = song['st']
    bpm = int(round(song['bpm']))
    spb = 60.0 / song['bpm']
    kit = dict(st.get('kitparams', {}))
    kit['_name'] = song['opts'].kit or st.get('kit', 'default')
    kit['_user_drums'] = bool(getattr(song['opts'], 'user_drums', False))
    groups = {}
    for e in song['events']:
        groups.setdefault(e.track, []).append(e)
    tracks = [t for t in st['tracks'] if groups.get(t['name'])]
    rev_ch = len(tracks) + 1
    dly_ch = len(tracks) + 2
    sc = st.get('sc_depth', 0) > 0
    kick_name = st.get('kick_track', 'kick')
    swing = st['swing']
    unit = st.get('swing_unit', 16)

    def tick(beat):
        q = beat * (4 if unit == 16 else 2)
        if abs(q - round(q)) < 1e-6 and int(round(q)) % 2 == 1:
            beat += (swing - 0.5) * (0.5 if unit == 16 else 1.0)
        return int(round(beat * 48))

    out = ['<?xml version="1.0"?>', '<!DOCTYPE lmms-project>',
           '<lmms-project version="1.0" creator="LMMS" creatorversion="1.2.2" type="song">',
           f'  <head timesig_numerator="4" mastervol="100" timesig_denominator="4" bpm="{bpm}" masterpitch="0"/>',
           '  <song>',
           '    <trackcontainer width="600" x="5" y="5" maximized="0" height="300" visible="1" type="song" minimized="0">']
    for i, t in enumerate(tracks):
        ch = i + 1
        if t['inst'].startswith('vst:'):          # LMMS can't load VST3 - use the matching built-in patch
            t = dict(t, inst=t.get('fallback') or 'pluck_saw')
        if t['inst'].startswith('sf:'):
            from . import soundfont as _sfm
            if not _sfm.library_path():
                t = dict(t, inst=t.get('fallback') or _sfm.fallback_for(t['inst'][3:]))
        ixml, patch = _instrument_xml(t, kit, spb)
        vol = _lmms_vol(t)
        out.append(f'      <track muted="0" type="0" name={quoteattr(t["name"] + " - " + t["inst"])} solo="0">')
        base = 48 if t['inst'].startswith('user:') else 57
        out.append(f'        <instrumenttrack pan="{int(t["pan"] * 100)}" fxch="{ch}" usemasterpitch="1" pitchrange="1" pitch="0" basenote="{base}" vol="{vol}">')
        out.append('          ' + ixml)
        out.append('          ' + _eldata_xml(patch if t['inst'] not in DRUMS else None, spb))
        out.append('          <chordcreator chord="0" chordrange="1" chord-enabled="0"/>')
        out.append('          <arpeggiator arptime="100" arprange="1" arpskip="0" arptime_denominator="4" arptime_syncmode="0" arpmode="0" '
                   'arpcycle="0" arp-enabled="0" arp="0" arptime_numerator="4" arpdir="0" arpmiss="0" arpgate="100"/>')
        out.append('          <midiport inputcontroller="0" fixedoutputvelocity="-1" inputchannel="0" outputcontroller="0" writable="0" '
                   'outputchannel="1" fixedinputvelocity="-1" fixedoutputnote="-1" outputprogram="1" basevelocity="63" readable="0"/>')
        out.append('          <fxchain numofeffects="0" enabled="0"/>')
        out.append('        </instrumenttrack>')
        is_drum = t['inst'] in DRUMS
        for s in song['sections']:
            b0, b1 = s['bar'] * 4, (s['bar'] + s['bars']) * 4
            notes = [e for e in groups[t['name']] if b0 <= e.beat < b1]
            if not notes:
                continue
            p0 = b0 * 48
            out.append(f'        <pattern pos="{p0}" len="{s["bars"] * 192}" muted="0" steps="16" name={quoteattr(s["name"])} type="1">')
            for e in notes:
                pos = tick(e.beat) - p0
                ln = 12 if is_drum else max(1, int(round(e.dur * 48)))
                key = 57 if is_drum else max(0, min(119, int(e.midi) - 12))
                vol = max(1, min(200, int(round(e.vel * 100))))
                out.append(f'          <note pos="{pos}" len="{ln}" key="{key}" vol="{vol}" pan="0"/>')
            out.append('        </pattern>')
        out.append('      </track>')
    out.append('    </trackcontainer>')
    # tempo/master automation track (empty, as LMMS writes it)
    out.append('    <track muted="0" type="6" name="Automation track" solo="0"><automationtrack/></track>')
    # ---- mixer
    out.append('    <fxmixer width="543" x="5" y="310" maximized="0" height="335" visible="1" minimized="0">')
    out.append('      <fxchannel num="0" muted="0" volume="1" name="Master" soloed="0"><fxchain numofeffects="0" enabled="0"/></fxchannel>')
    for i, t in enumerate(tracks):
        ch = i + 1
        fx = '<fxchain numofeffects="0" enabled="0"/>'
        conn = ''
        if sc and t['name'] == kick_name:
            depth = min(0.9, st['sc_depth'])
            fx = ('<fxchain numofeffects="1" enabled="1"><effect autoquit="1" gate="0" autoquit_denominator="4" wet="1" '
                  'name="peakcontrollereffect" on="1" autoquit_numerator="4" syncmode="0">'
                  f'<peakcontrollereffectcontrols abs="1" treshold="0" mute="0" base="0.5" amount="{-0.55 * depth:.3f}" '
                  'amountmult="1" decay="0.99" attack="0.999" effectId="1001"/><key/></effect></fxchain>')
        elif sc and t['sc'] and t['layer'] not in ('kick', 'snare', 'top'):
            conn = '<connection><volume id="0"/></connection>'
        sends = '<send amount="1" channel="0"/>'
        if t['rev']:
            sends += f'<send amount="{min(1.0, t["rev"] * 1.2):.2f}" channel="{rev_ch}"/>'
        if t['dly']:
            sends += f'<send amount="{min(1.0, t["dly"] * 1.2):.2f}" channel="{dly_ch}"/>'
        out.append(f'      <fxchannel num="{ch}" muted="0" volume="1" name={quoteattr(t["name"])} soloed="0">{fx}{conn}{sends}</fxchannel>')
    size = min(0.97, 0.6 + st['reverb'] / 12)
    out.append(f'      <fxchannel num="{rev_ch}" muted="0" volume="0.8" name="Reverb" soloed="0"><fxchain numofeffects="1" enabled="1">'
               '<effect autoquit="1" gate="0" autoquit_denominator="4" wet="1" name="reverbsc" on="1" autoquit_numerator="4" syncmode="0">'
               f'<ReverbSCControls input_gain="0" size="{size:.2f}" color="9000" output_gain="0"/><key/></effect></fxchain>'
               '<send amount="1" channel="0"/></fxchannel>')
    out.append(f'      <fxchannel num="{dly_ch}" muted="0" volume="0.7" name="Delay" soloed="0"><fxchain numofeffects="1" enabled="1">'
               '<effect autoquit="1" gate="0" autoquit_denominator="4" wet="1" name="delay" on="1" autoquit_numerator="4" syncmode="0">'
               f'<Delay DelayTimeSamples="{st["delay_beats"] * spb:.4f}" FeebackAmount="0.4" LfoFrequency="2" LfoAmount="0" OutGain="0" '
               'DelayTimeSamples_syncmode="0" DelayTimeSamples_numerator="4" DelayTimeSamples_denominator="4" '
               'LfoFrequency_syncmode="0" LfoFrequency_numerator="4" LfoFrequency_denominator="4" '
               'LfoAmount_syncmode="0" LfoAmount_numerator="4" LfoAmount_denominator="4"/><key/></effect></fxchain>'
               '<send amount="1" channel="0"/></fxchannel>')
    out.append('    </fxmixer>')
    out.append('    <ControllerRackView width="350" x="680" y="310" maximized="0" height="200" visible="1" minimized="0"/>')
    out.append('    <pianoroll width="640" x="5" y="5" maximized="0" height="480" visible="0" minimized="0"/>')
    out.append('    <automationeditor width="640" x="-36" y="0" maximized="0" height="400" visible="0" minimized="0"/>')
    notes = (f'Made with Studio Lab - {song["style"]} in {song["key"].name()} at {bpm} BPM. '
             'Sections are separate patterns. Kick drives the sidechain (Controller 1).')
    out.append(f'    <projectnotes width="640" x="700" y="10" maximized="0" height="400" visible="0" minimized="0"><![CDATA[{notes}]]></projectnotes>')
    out.append(f'    <timeline lp1pos="{song["total_bars"] * 192}" lp0pos="0" lpstate="0"/>')
    if sc:
        out.append('    <controllers><Peakcontroller name="Sidechain (kick)" effectId="1001" type="3"/></controllers>')
    else:
        out.append('    <controllers/>')
    out.append('  </song>')
    out.append('</lmms-project>')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    return path


# =============================================================================
#  Waveform Free / Tracktion (.tracktionedit)
# =============================================================================
import shutil
import time as _time
import wave as _wave


def _wav_seconds(path):
    with open(path, 'rb') as f:
        data = f.read(64)
    if data[20:22] == (3).to_bytes(2, 'little'):      # float WAV we wrote ourselves
        size = os.path.getsize(path) - 58
        return size / (8 * 44100)
    with _wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def _fader_pos(db):
    return math.exp((db - 6.0) / 20.0) if db > -100 else 0.0


def write_waveform(folder, song, renderer, mastered_wav):
    """A Waveform (Tracktion) edit: one audio track per rendered part (exact sound of the song),
    plus muted MIDI tracks of every part loaded with Waveform's built-in 4OSC synth so you can swap sounds."""
    os.makedirs(os.path.join(folder, 'Audio'), exist_ok=True)
    st = song['st']
    spb = 60.0 / song['bpm']
    nid = [1000]

    def new_id():
        nid[0] += 1
        return nid[0]

    title = os.path.basename(folder.rstrip('/\\'))
    ref = os.path.join(folder, 'Audio', 'mastered_reference' + os.path.splitext(mastered_wav)[1])
    shutil.copy2(mastered_wav, ref)
    stems = []
    for s in getattr(renderer, 'stems', []):
        if s.get('bus'):
            continue
        dst = os.path.join(folder, 'Audio', os.path.basename(s['path']))
        shutil.copy2(s['path'], dst)
        stems.append(dict(s, path=dst))
    # true peak of the summed stems (what Waveform will play), +3 dB for the centre pan law, +1.5 dB headroom
    import numpy as _np
    acc = None
    for s in stems:
        a = _np.fromfile(s['path'], dtype='<f4', offset=58)
        acc = a.astype(_np.float64) if acc is None else acc[:len(a)] + a[:len(acc)]
    peak = float(_np.max(_np.abs(acc))) if acc is not None and len(acc) else 1.0
    master_db = max(-40.0, min(6.0, -(20 * math.log10(max(peak, 1e-6)) + 4.5)))

    colours = {'kick': 'ffff5555', 'snare': 'ffff8855', 'top': 'ffffbb55', 'bass': 'ff55aaff', 'chords': 'ffaa77ff',
               'pad': 'ff7777ff', 'arp': 'ff55ffcc', 'lead': 'ff55ff55', 'fx': 'ffaaaaaa', 'drums': 'ffff7755'}

    def audio_track(name, path, colour, mute=False, vol_db=0.0):
        tid, vid, lid, cid = new_id(), new_id(), new_id(), new_id()
        rel = os.path.relpath(path, folder).replace('\\', '/')
        length = _wav_seconds(path)
        return (f'  <TRACK id="{tid}" name={quoteattr(name)} colour="{colour}"{" mute=\"1\"" if mute else ""}>\n'
                '    <MODIFIERS/>\n    <OUTPUTDEVICES><DEVICE name="(default audio output)"/></OUTPUTDEVICES>\n    <CLIPSLOTS/>\n'
                f'    <PLUGIN type="volume" id="{vid}" enabled="1" volume="{_fader_pos(vol_db):.6f}" pan="0.0" remapOnTempoChange="1"><MODIFIERASSIGNMENTS/></PLUGIN>\n'
                f'    <PLUGIN type="level" id="{lid}" enabled="1"/>\n'
                f'    <AUDIOCLIP name={quoteattr(name)} start="0.0" length="{length:.6f}" offset="0.0" id="{cid}" source={quoteattr(rel)} '
                f'sync="0" elastiqueMode="0" pan="0.0" colour="{colour}" proxyAllowed="1" resamplingQuality="lagrange">\n'
                '      <AUTOMATIONCURVES/>\n      <LOOPINFO numBeats="0.0" denominator="4" numerator="4" oneShot="0" bpm="0" rootNote="-1" inMarker="0" outMarker="-1"/>\n'
                '    </AUDIOCLIP>\n  </TRACK>\n')

    groups = {}
    for e in song['events']:
        groups.setdefault(e.track, []).append(e)

    def midi_track(name, events, colour, synth=True, drum_map=None):
        tid, vid, lid = new_id(), new_id(), new_id()
        x = (f'  <TRACK id="{tid}" name={quoteattr(name)} colour="{colour}" mute="1">\n'
             '    <MODIFIERS/>\n    <OUTPUTDEVICES><DEVICE name="(default audio output)"/></OUTPUTDEVICES>\n    <CLIPSLOTS/>\n')
        if synth:
            x += f'    <PLUGIN type="4osc" id="{new_id()}" enabled="1"><MODIFIERASSIGNMENTS/></PLUGIN>\n'
        x += (f'    <PLUGIN type="volume" id="{vid}" enabled="1" remapOnTempoChange="1"><MODIFIERASSIGNMENTS/></PLUGIN>\n'
              f'    <PLUGIN type="level" id="{lid}" enabled="1"/>\n')
        for s in song['sections']:
            b0, b1 = s['bar'] * 4, (s['bar'] + s['bars']) * 4
            evs = [e for e in events if b0 <= e.beat < b1]
            if not evs:
                continue
            x += (f'    <MIDICLIP name={quoteattr(s["name"])} start="{b0 * spb:.6f}" length="{(b1 - b0) * spb:.6f}" offset="0.0" '
                  f'id="{new_id()}" sync="0" currentTake="0" speed="1.0" colour="{colour}">\n'
                  '      <AUTOMATIONCURVES/>\n      <QUANTISATION/>\n      <GROOVE/>\n      <SEQUENCE ver="1" channelNumber="1">\n')
            for e in evs:
                b = renderer.t_of(e.beat, human=False) / spb - b0
                p = drum_map.get(e.track, 37) if drum_map else int(e.midi)
                l = 0.25 if drum_map else max(0.01, e.dur)
                v = max(1, min(127, int(e.vel * 110)))
                x += f'        <NOTE p="{p}" b="{b:.4f}" l="{l:.4f}" v="{v}" c="0"/>\n'
            x += '      </SEQUENCE>\n    </MIDICLIP>\n'
        x += '  </TRACK>\n'
        return x

    body = [audio_track('Mastered reference (muted)', ref, 'ff888888', mute=True)]
    for s in stems:
        body.append(audio_track(f"{s['name']} ({INSTRUMENT_INFO.get(s['inst'], s['inst'])})", s['path'],
                                colours.get(s['layer'], 'ff99cc99')))
    drum_names = [t['name'] for t in st['tracks'] if t['inst'] in DRUMS and groups.get(t['name'])]
    if drum_names:
        devs = [e for n in drum_names for e in groups[n]]
        dmap = {t['name']: GM_DRUM.get(t['inst'], 37) for t in st['tracks'] if t['inst'] in DRUMS}
        body.append(midi_track('MIDI drums (GM map - load a drum sampler)', devs, 'ffff7755', synth=False, drum_map=dmap))
    for t in st['tracks']:
        if t['inst'] in DRUMS or not groups.get(t['name']):
            continue
        rec = (song.get('plugin_recs') or {}).get(t['name'])
        hint = f"try {rec['picks'][0]['name']}" if rec and rec['picks'] else 'swap for any instrument'
        body.append(midi_track(f"MIDI {t['name']} (4OSC - {hint})", groups[t['name']],
                               colours.get(t['layer'], 'ff99cc99')))
    total = song['total_bars'] * 4 * spb
    head = ('<?xml version="1.0" encoding="UTF-8"?>\n\n'
            f'<EDIT appVersion="Waveform 13.0.0" projectID="0/{int(_time.time()) % 0xfffffff:x}" creationTime="{int(_time.time() * 1000)}">\n'
            f'  <TRANSPORT start="0.0" loopPoint1="0.0" loopPoint2="{total:.6f}"/>\n'
            '  <PITCHSEQUENCE>\n    <PITCH startBeat="0.0" pitch="60"/>\n  </PITCHSEQUENCE>\n'
            f'  <TEMPOSEQUENCE>\n    <TEMPO startBeat="0.0" bpm="{song["bpm"]:.1f}" curve="1.0"/>\n'
            '    <TIMESIG numerator="4" denominator="4" startBeat="0.0"/>\n  </TEMPOSEQUENCE>\n'
            '  <VIDEO/>\n  <CLICKTRACK level="0.6"/>\n'
            f'  <MASTERVOLUME>\n    <PLUGIN type="volume" volume="{_fader_pos(master_db):.6f}" id="{new_id()}" enabled="1"><MODIFIERASSIGNMENTS/></PLUGIN>\n  </MASTERVOLUME>\n'
            '  <RACKS/>\n  <MASTERPLUGINS/>\n  <INPUTDEVICES/>\n  <TRACKCOMPS/>\n'
            f'  <ARRANGERTRACK name="Arranger" id="{new_id()}"/>\n  <CHORDTRACK name="Chord" id="{new_id()}"/>\n'
            f'  <MARKERTRACK id="{new_id()}" name="Marker"/>\n  <TEMPOTRACK name="Global" id="{new_id()}"><MODIFIERS/></TEMPOTRACK>\n'
            f'  <MASTERTRACK name="Master" id="{new_id()}"><MODIFIERS/></MASTERTRACK>\n')
    path = os.path.join(folder, title + '.tracktionedit')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(head + ''.join(body) + '  <SCENES/>\n</EDIT>\n')
    with open(os.path.join(folder, 'READ ME.txt'), 'w') as f:
        f.write('Open the .tracktionedit file in Waveform (Free or Pro).\n'
                'In Waveform: drag the .tracktionedit file into the Projects browser (or double-click it).\n\n'
                'Audio tracks play the song exactly as rendered (one track per part, plus reverb/delay returns).\n'
                'The muted "MIDI ..." tracks hold every note on Waveform\'s 4OSC synth - unmute one and mute its\n'
                'audio twin to replace a sound, or drop any plugin/instrument onto it.\n'
                'The muted "Mastered reference" track is the finished master for A/B comparison.\n')
    return path


# ----------------------------------------------------------------------------- DAW pack (Ableton, FL Studio, Logic, Reaper ...)
DAW_GUIDE = """{title}
{style} · {key} · {bpm} BPM · 4/4 · {bars} bars

This folder works in any DAW: every audio stem starts at bar 1 and is the full length of the song, so they line up
when dropped at the start of the timeline. Set your project to {bpm} BPM first.

  Audio/      one WAV per part (32-bit float, 44.1 kHz) - drag them ALL in and you have the whole song
  Audio/Extras  the finished mix (to compare against) and the drums as one processed bus
              (use the bus INSTEAD of the separate drum stems if you prefer)
  MIDI/       one MIDI file per part, the whole song as one MIDI file, and a vocal guide melody
  {title}.rpp a ready-made REAPER project (open it in REAPER)

ABLETON LIVE
  1. New Live Set, set tempo to {bpm}.
  2. Select all files in Audio/ and drag them into the Arrangement View at bar 1 - each becomes its own track.
     (Hold Cmd/Ctrl while dropping to put them on separate tracks if Live stacks them.) Turn Warp OFF for the stems.
  3. Drag files from MIDI/ onto MIDI tracks with your own instruments.

FL STUDIO
  1. Set the tempo to {bpm}.
  2. Drag the files from Audio/ into the Playlist at bar 1 (one per track), or into the Channel Rack as Audio Clips.
  3. Drag MIDI files onto a channel / plugin (File > Import > MIDI file for the whole song).

LOGIC PRO / GARAGEBAND
  1. Set the tempo to {bpm}. Drag all files from Audio/ to the track area at bar 1 - choose "Create new tracks".
  2. Drag MIDI files to the track area for software-instrument tracks.

CUBASE / STUDIO ONE / BITWIG
  Set the tempo, then drag the Audio/ files to bar 1 (one track each) and the MIDI files to instrument tracks.

The vocal guide (MIDI/…vocal_guide.mid) is a melody to sing over - load a piano or choir on it while you write lyrics.
"""


def _rpp(title, bpm, stems, length_s):
    """A minimal REAPER project with one track per stem, all starting at 0."""
    lines = ['<REAPER_PROJECT 0.1 "6.0"', f'  TEMPO {bpm} 4 4', '  SAMPLERATE 44100 0 0']
    for st in stems:
        name = os.path.splitext(os.path.basename(st))[0]
        lines += ['  <TRACK', f'    NAME "{name}"', '    <ITEM', '      POSITION 0', f'      LENGTH {length_s:.3f}',
                  f'      NAME "{name}"', '      <SOURCE WAVE', f'        FILE "Audio/{os.path.basename(st)}"', '      >', '    >', '  >']
    lines.append('>')
    return '\n'.join(lines) + '\n'


def write_daw_pack(folder, song, renderer, mix_wav, log=print):
    """Stems + per-part MIDI + full MIDI + vocal guide + import guide + REAPER project, zipped. Returns the zip path."""
    import shutil
    import zipfile
    title = os.path.basename(folder.rstrip('/\\'))
    audio, midi = os.path.join(folder, 'Audio'), os.path.join(folder, 'MIDI')
    os.makedirs(audio, exist_ok=True)
    os.makedirs(midi, exist_ok=True)
    copied = []
    n = 0
    for st in getattr(renderer, 'stems', []) or []:
        if not os.path.exists(st['path']):
            continue
        if st.get('bus'):                               # the processed drum sum: an alternative, not an extra layer
            os.makedirs(os.path.join(audio, 'Extras'), exist_ok=True)
            shutil.copy2(st['path'], os.path.join(audio, 'Extras', 'Drum bus (all drums processed - use INSTEAD of the drum stems).wav'))
            continue
        n += 1
        dst = os.path.join(audio, f"{n:02d} {st['name'].replace('_', ' ').title()}.wav")
        shutil.copy2(st['path'], dst)
        copied.append(dst)
    if mix_wav and os.path.exists(mix_wav):
        os.makedirs(os.path.join(audio, 'Extras'), exist_ok=True)
        dst = os.path.join(audio, 'Extras', 'Full mix (reference).wav')
        shutil.copy2(mix_wav, dst)
    write_midi(os.path.join(midi, f'{title} - full song.mid'), song)
    write_part_midis(midi, song)
    k = song['key']
    with open(os.path.join(folder, 'HOW TO OPEN IN YOUR DAW.txt'), 'w', encoding='utf-8') as f:
        f.write(DAW_GUIDE.format(title=title, style=song['style'], key=k.name(), bpm=song['bpm'], bars=song['total_bars']))
    length = song['total_bars'] * 4 * 60 / song['bpm'] + 4
    with open(os.path.join(folder, title + '.rpp'), 'w', encoding='utf-8') as f:
        f.write(_rpp(title, song['bpm'], copied, length))
    zpath = folder.rstrip('/\\') + '.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            for fn in files:
                fp = os.path.join(root, fn)
                z.write(fp, os.path.join(title, os.path.relpath(fp, folder)))
    log(f'   DAW pack: {len(copied)} stems, MIDI, guide -> {os.path.basename(zpath)}')
    return zpath
