"""References from note files: MIDI (.mid), MusicXML (.musicxml / .xml / .mxl) and Studio Lab settings (.json).

Note files give the exact notes, so beyond tempo and key we can read the mode, the chord progression, swing and how
busy the drums and parts are - and turn them into Studio Lab settings.
"""
import io
import json
import struct
import zipfile
from collections import Counter
import xml.etree.ElementTree as ET

import numpy as np

from .theory import NOTE_NAMES, SCALES

MAX_BYTES = 20 * 1024 * 1024
# Note = (beat, length_beats, midi_pitch, velocity_0_1, is_drum)


# ----------------------------------------------------------------------------- MIDI
def _vlq(d, i):
    v = 0
    while True:
        b = d[i]
        i += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, i


def parse_midi(data):
    if data[:4] != b'MThd':
        raise ValueError('not a MIDI file')
    hl = struct.unpack('>I', data[4:8])[0]
    fmt, ntrk, div = struct.unpack('>HHH', data[8:14])
    if div & 0x8000:
        raise ValueError('SMPTE-timed MIDI files are not supported')
    ppq = div or 480
    pos = 8 + hl
    notes, tempo, timesig, keysig = [], None, (4, 4), None
    for _ in range(ntrk):
        if data[pos:pos + 4] != b'MTrk':
            break
        ln = struct.unpack('>I', data[pos + 4:pos + 8])[0]
        d, i, end = data, pos + 8, pos + 8 + ln
        pos = end
        tick, status, on = 0, 0, {}
        while i < end:
            delta, i = _vlq(d, i)
            tick += delta
            b = d[i]
            if b & 0x80:
                status = b
                i += 1
            if status == 0xFF:
                typ = d[i]
                ml, i = _vlq(d, i + 1)
                payload = d[i:i + ml]
                i += ml
                if typ == 0x51 and tempo is None and ml == 3:
                    tempo = int.from_bytes(payload, 'big')
                elif typ == 0x58 and ml >= 2 and tick == 0:
                    timesig = (payload[0], 2 ** payload[1])
                elif typ == 0x59 and ml == 2 and keysig is None:
                    keysig = (struct.unpack('b', payload[:1])[0], payload[1])
                status = 0                                     # meta events cancel running status
                continue
            if status in (0xF0, 0xF7):
                ml, i = _vlq(d, i)
                i += ml
                continue
            kind, ch = status & 0xF0, status & 0x0F
            if kind in (0xC0, 0xD0):
                i += 1
                continue
            a, v = d[i], d[i + 1]
            i += 2
            if kind == 0x90 and v > 0:
                on.setdefault((ch, a), []).append((tick, v))
            elif kind == 0x80 or (kind == 0x90 and v == 0):
                if on.get((ch, a)):
                    t0, vel = on[(ch, a)].pop(0)
                    notes.append((t0 / ppq, max(0.05, (tick - t0) / ppq), a, vel / 127, ch == 9))
    if not notes:
        raise ValueError('this MIDI file has no notes')
    bpm = 60_000_000 / tempo if tempo else 120.0
    return dict(notes=notes, bpm=bpm, timesig=timesig, keysig=keysig)


# ----------------------------------------------------------------------------- MusicXML
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def _strip(tag):
    return tag.rsplit('}', 1)[-1]


def parse_musicxml(data):
    if data[:2] == b'PK':                                   # compressed .mxl
        z = zipfile.ZipFile(io.BytesIO(data))
        root = None
        try:
            c = ET.fromstring(z.read('META-INF/container.xml'))
            root = next((e.get('full-path') for e in c.iter() if _strip(e.tag) == 'rootfile'), None)
        except Exception:
            pass
        root = root or next(n for n in z.namelist() if n.endswith(('.xml', '.musicxml')) and not n.startswith('META-INF'))
        data = z.read(root)
    if b'<!ENTITY' in data[:4096]:
        raise ValueError('unsupported XML')
    tree = ET.fromstring(data)
    for e in tree.iter():
        e.tag = _strip(e.tag)
    notes, bpm, timesig, keysig = [], None, (4, 4), None
    for part in tree.iter('part'):
        div, t = 1, 0.0
        last_start = 0.0
        for meas in part.iter('measure'):
            for el in meas:
                if el.tag == 'attributes':
                    if el.find('divisions') is not None:
                        div = float(el.find('divisions').text)
                    k = el.find('key')
                    if k is not None and keysig is None and k.find('fifths') is not None:
                        keysig = (int(k.find('fifths').text), 1 if (k.findtext('mode') or '') == 'minor' else 0)
                    ts = el.find('time')
                    if ts is not None and ts.find('beats') is not None and t == 0:
                        try:
                            timesig = (int(ts.findtext('beats')), int(ts.findtext('beat-type')))
                        except ValueError:
                            pass
                elif el.tag == 'direction' or el.tag == 'sound':
                    snd = el if el.tag == 'sound' else el.find('.//sound')
                    if snd is not None and snd.get('tempo') and bpm is None:
                        bpm = float(snd.get('tempo'))
                elif el.tag == 'backup':
                    t -= float(el.findtext('duration', '0')) / div
                elif el.tag == 'forward':
                    t += float(el.findtext('duration', '0')) / div
                elif el.tag == 'note':
                    dur = float(el.findtext('duration', '0')) / div
                    chord = el.find('chord') is not None
                    start = last_start if chord else t
                    p = el.find('pitch')
                    if p is not None and el.find('rest') is None:
                        midi = 12 * (int(p.findtext('octave', '4')) + 1) + STEP.get(p.findtext('step', 'C'), 0) + \
                            int(float(p.findtext('alter', '0')))
                        notes.append((start, max(0.05, dur), midi, 0.8, False))
                    elif el.find('unpitched') is not None:
                        notes.append((start, max(0.05, dur), 38, 0.8, True))
                    if not chord:
                        last_start = t
                        t += dur
    if not notes:
        raise ValueError('this MusicXML file has no notes')
    return dict(notes=notes, bpm=bpm or 120.0, timesig=timesig, keysig=keysig)


# ----------------------------------------------------------------------------- analysis
MODES = ('major', 'minor', 'dorian', 'mixolydian', 'phrygian')


def _bass_line(notes, step=1.0):
    """Lowest pitched note on each beat."""
    lows = {}
    for b, l, m, v, drum in notes:
        if drum:
            continue
        k = int(b // step)
        if k not in lows or m < lows[k]:
            lows[k] = m
    return [lows[k] for k in sorted(lows)]


def _key(notes, keysig, bpb=4.0):
    """Home note + mode: scale fit of the notes, then which note the bass, the first and the last chords call home."""
    chroma = np.zeros(12)
    for b, l, m, v, drum in notes:
        if not drum:
            chroma[m % 12] += l * (0.5 + v)
    if chroma.sum() == 0:
        return 0, 'major', chroma
    chroma /= chroma.sum()
    bass = _bass_line(notes)
    bchroma = np.zeros(12)
    for m in bass:
        bchroma[m % 12] += 1
    bchroma /= max(1, bchroma.sum())
    dchroma = np.zeros(12)                        # bass note under each bar's downbeat: the strongest "home" cue
    downs = []
    for k in range(int(max(b + l for b, l, m, v, d in notes) // bpb) + 1):
        under = [m for b, l, m, v, d in notes if not d and m < 60 and b <= k * bpb + 0.05 and b + l > k * bpb]
        if under:
            dchroma[min(under) % 12] += 1
            downs.append(min(under) % 12)
    dchroma /= max(1, dchroma.sum())
    first = downs[0] if downs else (bass[0] % 12 if bass else None)     # songs and loops usually open on the home chord
    last = bass[-1] % 12 if bass else None
    best = (-9, 0, 'major')
    for r in range(12):
        for mode in MODES:
            pcs = [(r + x) % 12 for x in SCALES[mode]]
            fit = sum(chroma[p] for p in pcs) - 1.5 * sum(chroma[p] for p in range(12) if p not in pcs)
            third, fifth = (r + SCALES[mode][2]) % 12, (r + 7) % 12
            home = 0.5 * bchroma[r] + 0.9 * dchroma[r] + 0.35 * chroma[r] + 0.15 * chroma[third] + 0.1 * chroma[fifth]
            home += 0.12 * (first == r) + 0.08 * (last == r)
            prior = {'major': 0.05, 'minor': 0.05}.get(mode, 0.0)   # plain major/minor unless the notes say otherwise
            score = fit + home + prior
            if keysig is not None:
                sf, minor = keysig
                if r == (7 * sf + (9 if minor else 0)) % 12 and (mode in ('minor', 'dorian', 'phrygian')) == bool(minor):
                    score += 0.15
            if score > best[0]:
                best = (score, r, mode)
    return best[1], best[2], chroma


def _progression(notes, root, scale, beats_per_bar):
    """Best-fitting diatonic triad per bar (bass notes count double), then the most common 4-chord loop."""
    sc = SCALES[scale]
    end = max(b + l for b, l, m, v, d in notes)
    nbars = max(1, int(np.ceil(end / beats_per_bar)))
    degs = []
    for bar in range(min(nbars, 128)):
        w = np.zeros(12)
        lo = 999
        b0, b1 = bar * beats_per_bar, (bar + 1) * beats_per_bar
        for b, l, m, v, drum in notes:
            if drum or b + l <= b0 or b >= b1:
                continue
            ov = min(b + l, b1) - max(b, b0)
            w[(m - root) % 12] += ov
            lo = min(lo, m)
        if w.sum() == 0:
            continue
        bass = [m for b, l, m, v, d in notes if not d and b0 <= b < b1 and m <= lo + 4]
        best, bs = None, -1e9
        for d in range(7):
            pcs = {sc[(d + k) % 7] for k in (0, 2, 4)}
            s_ = sum(w[p] for p in pcs) - 0.5 * sum(w[p] for p in range(12) if p not in pcs)
            if bass and (bass[0] - root) % 12 == sc[d]:
                s_ += 0.6 * w.sum()
            if s_ > bs:
                best, bs = d, s_
        degs.append(best)
    runs = [d for i, d in enumerate(degs) if i == 0 or d != degs[i - 1]]
    if len(runs) < 2:
        return None
    if len(runs) <= 4:
        loop = runs
    else:
        counts = Counter(tuple(runs[i:i + 4]) for i in range(len(runs) - 3)).most_common()
        top = counts[0][1]
        home = [w for w, c in counts if w[0] == 0 and c >= 0.75 * top]     # loops are written from the home chord
        loop = list(home[0] if home else counts[0][0])
    return '-'.join(str(d + 1) for d in loop)


def _swing(notes):
    off = [b % 1 for b, l, m, v, d in notes if 0.42 < b % 1 < 0.8]
    if len(off) < 12:
        return None
    pos = float(np.median(off))
    return round(min(0.72, pos), 2) if pos > 0.56 else None


def analyze_notes(parsed):
    notes = parsed['notes']
    num, den = parsed['timesig']
    bpb = num * 4 / den
    root, scale, chroma = _key(notes, parsed.get('keysig'), bpb)
    prog = _progression(notes, root, scale, bpb)
    end = max(b + l for b, l, m, v, d in notes)
    bars = max(1.0, end / bpb)
    drums = [n for n in notes if n[4]]
    pitched = [n for n in notes if not n[4]]
    dpb = len(drums) / bars                       # drum hits per bar: 8 ~ sparse, 16 ~ steady, 48+ ~ busy
    energy = np.clip(np.log2(max(dpb, 1) / 4) / 4.2, 0.05, 0.95) if drums else np.clip(np.log2(max(len(pitched) / bars, 1)) / 7, 0.1, 0.6)
    pcs_per_bar = np.mean([len({m % 12 for b, l, m, v, d in pitched if int(b // bpb) == k}) for k in range(int(bars))] or [3])
    npb = len(pitched) / bars
    complexity = float(np.clip(0.55 * (pcs_per_bar - 3) / 5 + 0.45 * np.log2(max(npb, 1) / 4) / 4, 0.05, 0.95))
    bpm = float(parsed['bpm'])
    while bpm < 60:
        bpm *= 2
    while bpm > 200:
        bpm /= 2
    key = NOTE_NAMES[root] + ('m' if scale in ('minor', 'dorian', 'phrygian') else '')
    out = dict(bpm=int(round(bpm)), key=key, scale=scale, energy=round(float(energy), 2), complexity=round(complexity, 2),
               notes=len(notes), bars=int(round(bars)), timesig=f'{num}/{den}', source='notes')
    if prog:
        out['progression'] = prog
    sw = _swing(notes)
    if sw:
        out['swing'] = sw
    return out


def analyze_file(name, data):
    if len(data) > MAX_BYTES:
        raise ValueError('file is too large')
    low = (name or '').lower()
    if low.endswith('.json'):
        d = json.loads(data.decode('utf-8'))
        opts = d.get('options', d) if isinstance(d, dict) else None
        if not isinstance(opts, dict) or 'style' not in opts:
            raise ValueError('this JSON file is not Studio Lab settings')
        return dict(source='settings', options=opts)
    if low.endswith(('.mid', '.midi', '.kar', '.smf')) or data[:4] == b'MThd':
        return analyze_notes(parse_midi(data))
    if low.endswith(('.musicxml', '.xml', '.mxl')) or data[:2] == b'PK' or b'<score-partwise' in data[:2000]:
        return analyze_notes(parse_musicxml(data))
    raise ValueError('use an audio file, a MIDI file (.mid), MusicXML (.musicxml / .mxl) or Studio Lab settings (.json)')
