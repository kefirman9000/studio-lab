"""(2.20) Learn from multitrack songs (stems + per-part MIDI): what each part does, how the song is built, how it's mixed.

    python tools/stem_report.py <folder> [--json out.json]

The folder can hold several songs: files are grouped by name ("Song_v1.flac", "Song_v1_bass.flac", "Song_v1_bass.mid",
...; an upload prefix like "a3bcac31-" is ignored). Needs ffmpeg for audio. Nothing is copied into the app - only the
measurements, which tune the genres.

Per song: tempo (from the MIDI tempo map and the audio length), key / scale, length, the form (which parts play in each
8-bar block), and per part: register, notes per bar, rhythm grid, note lengths, chords (polyphony), how repetitive it
is; per stem: level against the full mix (while it plays), brightness, dynamics; the drum stem's kick / snare / hat
positions on the 16-step grid.
"""
import collections
import json
import os
import re
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SR = 22050
NAMES = 'C C# D D# E F F# G G# A A# B'.split()


def song_key(fn):
    b = os.path.basename(fn)
    b = re.sub(r'^[0-9a-f]{6,10}-', '', b)
    stem = os.path.splitext(b)[0]
    m = re.match(r'(.+?_v\d+)(?:_(.+))?$', stem)
    return (m.group(1), m.group(2) or 'mix') if m else (stem, 'mix')


NI_STEMS = ['mix', 'drums', 'bass', 'other', 'vocals']     # stream order of a Native Instruments .stem.mp4


def load_audio(path):
    stream = None
    if '#' in path:                                      # "file.stem.mp4#2" = its third audio stream
        path, stream = path.rsplit('#', 1)
    try:
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path] + (['-map', f'0:a:{stream}'] if stream else []) +
                             ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.float32)
    except Exception:
        return None


def tempo_map(data):
    """[(tick, us_per_quarter)] and ticks per quarter from a MIDI file."""
    tpq = int.from_bytes(data[12:14], 'big')
    out, i = [], 14
    from sgcore.refparse import _vlq
    while i < len(data) - 8 and data[i:i + 4] == b'MTrk':
        ln = int.from_bytes(data[i + 4:i + 8], 'big')
        j, end, tick, run = i + 8, i + 8 + ln, 0, None
        while j < end:
            d, j = _vlq(data, j)
            tick += d
            st = data[j]
            if st == 0xFF:
                typ = data[j + 1]
                ln2, k = _vlq(data, j + 2)
                if typ == 0x51 and ln2 == 3:
                    out.append((tick, int.from_bytes(data[k:k + 3], 'big')))
                j = k + ln2
            elif st in (0xF0, 0xF7):
                ln2, k = _vlq(data, j + 1)
                j = k + ln2
            else:
                if st & 0x80:
                    run = st
                    j += 1
                j += 1 if (run & 0xF0) in (0xC0, 0xD0) else 2
        i = end
    return tpq, sorted(out) or [(0, 500000)]


def beats_to_sec(beats, tmap, tpq):
    """Seconds at a beat position, following the tempo changes."""
    t, sec, last_us = 0.0, 0.0, tmap[0][1]
    for tick, us in tmap:
        b = tick / tpq
        if b >= beats:
            break
        sec += (b - t) * last_us / 1e6
        t, last_us = b, us
    return sec + (beats - t) * last_us / 1e6


def part_stats(notes, bars):
    if not notes:
        return None
    ps = [n[2] for n in notes]
    on = [n[0] for n in notes]
    grid = collections.Counter(int(round((b % 4) * 4)) % 16 for b in on)
    durs = collections.Counter(round(n[1], 3) for n in notes)
    starts = collections.Counter(round(b, 3) for b in on)
    chordy = sum(1 for v in starts.values() if v > 1) / max(1, len(starts))
    active = sorted({int(b // 4) for b in on})
    # how often a bar repeats the bar 4 bars earlier (same rhythm and pitches)
    by_bar = collections.defaultdict(list)
    for n in notes:
        by_bar[int(n[0] // 4)].append((round(n[0] % 4, 2), n[2]))
    rep = [sorted(by_bar[b]) == sorted(by_bar.get(b - 4, [])) for b in active if b - 4 in by_bar]
    return dict(notes=len(notes), low=min(ps), high=max(ps), median=int(np.median(ps)),
                per_bar=round(len(notes) / max(1, len(active)), 1), active_bars=len(active), of_bars=bars,
                grid16=[grid.get(i, 0) for i in range(16)],
                lengths=[(d, c) for d, c in durs.most_common(4)], chords=round(chordy, 2),
                repeats_4_bars_back=round(sum(rep) / len(rep), 2) if rep else None)


def drum_grid(x, bpm, offset=0.0):
    from scipy import signal
    hop = 256
    out = {}
    for name, lo, hi in (('kick', 0, 140), ('snare', 1500, 5000), ('hat', 7000, 10500)):
        sos = signal.butter(4, hi / (SR / 2), output='sos') if lo == 0 else \
            signal.butter(4, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos')
        y = signal.sosfilt(sos, x)
        e = np.sqrt(np.convolve(y ** 2, np.ones(hop) / hop, 'same'))[::hop]
        d = np.maximum(0, np.diff(e, prepend=e[0]))
        if d.max() <= 0:
            continue
        pk, _ = signal.find_peaks(d, height=0.3 * d.max(), distance=max(2, int(0.06 * SR / hop)))
        t = pk * hop / SR - offset
        step = 60.0 / bpm / 4
        pos = np.round(t / step).astype(int) % 16
        c = np.bincount(pos, minlength=16)
        out[name] = (c / max(1, c.sum()) * 100).round().astype(int).tolist()
    return out


def stem_audio_stats(x, mix):
    n = min(len(x), len(mix))
    x, mix = x[:n], mix[:n]
    blk = SR // 4
    k = n // blk
    if k < 4:
        return None
    xr = np.sqrt((x[:k * blk].reshape(k, blk) ** 2).mean(1) + 1e-12)
    mr = np.sqrt((mix[:k * blk].reshape(k, blk) ** 2).mean(1) + 1e-12)
    on = xr > xr.max() * 0.05
    if not on.any():
        return None
    rel = 20 * np.log10(np.median(xr[on]) / np.median(mr[on]))
    spec = np.abs(np.fft.rfft(x[:min(n, SR * 60)] * np.hanning(min(n, SR * 60))))
    f = np.fft.rfftfreq(min(n, SR * 60), 1 / SR)
    cen = float((spec * f).sum() / max(1e-9, spec.sum()))
    xa = x[:k * blk][on.repeat(blk)]
    crest = 20 * np.log10(np.abs(xa).max() / (np.sqrt((xa ** 2).mean()) + 1e-9) + 1e-9)
    return dict(level_vs_mix_db=round(float(rel), 1), brightness_hz=int(cen), crest_db=round(float(crest), 1),
                plays_pct=int(on.mean() * 100))


def mix_stats(mix):
    from scipy import signal
    rms = 20 * np.log10(np.sqrt((mix ** 2).mean()) + 1e-12)
    out = dict(rms_db=round(float(rms), 1), peak_db=round(float(20 * np.log10(np.abs(mix).max() + 1e-12)), 1))
    for name, lo, hi in (('lows_<150', 20, 150), ('mids_150-2k', 150, 2000), ('highs_>2k', 2000, 10000)):
        sos = signal.butter(4, [lo / (SR / 2), hi / (SR / 2)], 'band', output='sos')
        y = signal.sosfilt(sos, mix)
        out[name] = round(float(20 * np.log10(np.sqrt((y ** 2).mean()) + 1e-12) - rms), 1)
    return out


def analyze_song(files):
    from sgcore.refparse import parse_midi, analyze_notes
    mids = {p: f for (p, k), f in files.items() if k == 'mid'}
    auds = {p: f for (p, k), f in files.items() if k == 'aud'}
    rep = dict(parts={}, stems={})
    mix = load_audio(auds['mix']) if 'mix' in auds else None
    dur = len(mix) / SR if mix is not None else None
    notes, tmaps = {}, []
    for part, f in sorted(mids.items()):
        data = open(f, 'rb').read()
        p = parse_midi(data)
        notes[part] = [n for n in p['notes'] if not n[4]]
        tmaps.append(tempo_map(data))
    allnotes = [n for v in notes.values() for n in v]
    if allnotes:
        tpq, tmap = tmaps[0]
        end = max(n[0] + n[1] for n in allnotes)
        bpms = [60e6 / us for _, us in tmap]
        rep['tempo'] = dict(start=round(bpms[0], 1), low=round(min(bpms), 1), high=round(max(bpms), 1),
                            changes=len(tmap) - 1)
        if dur:
            rep['tempo']['average_from_audio'] = round(end / max(1e-6, beats_to_sec(end, tmap, tpq)) * 60, 1)
        a = analyze_notes(dict(notes=allnotes, bpm=bpms[0], timesig=(4, 4), keysig=None))
        rep['key'] = f"{str(a.get('key')).rstrip('m')} {a.get('scale')}"
        rep['progression'] = a.get('progression')
        bars = int(np.ceil(end / 4))
        rep['bars'] = bars
        for part, ns in notes.items():
            rep['parts'][part] = part_stats(ns, bars)
        # the form: which parts play in each 8-bar block
        rep['form'] = {part: ''.join('#' if any(blk * 32 <= n[0] < blk * 32 + 32 for n in ns) else '.'
                                     for blk in range((bars + 7) // 8)) for part, ns in notes.items()}
        pcs = collections.Counter(n[2] % 12 for n in allnotes)
        rep['pitch_classes'] = ' '.join(f'{NAMES[k]}:{v}' for k, v in pcs.most_common())
    if dur:
        try:                                             # what the app hears in it: tempo, key, closest genres
            from sgcore.analysis import analyze
            from sgcore import genrematch
            from sgcore.styles import STYLES
            from sgcore.styles import LABELS as _LABELS
            seg = mix[:SR * 150]
            a = analyze(seg, SR)
            genrematch.analyze_reference(np.asarray(seg, np.float64), SR, a)
            rep['heard'] = dict(bpm=a.get('bpm'), key=a.get('key'),
                                genres=[(g['id'], g['match']) for g in genrematch.suggest(a, STYLES, _LABELS, top=6)])
        except Exception as e:                           # noqa: BLE001
            rep['heard'] = dict(error=str(e))
        rep['length_s'] = round(dur, 1)
        rep['mix'] = mix_stats(mix)
        for part, f in sorted(auds.items()):
            if part == 'mix':
                continue
            x = load_audio(f)
            if x is None:
                continue
            rep['stems'][part] = stem_audio_stats(x, mix)
            if 'drum' in part:
                bpm = (rep.get('tempo') or {}).get('average_from_audio') or (rep.get('tempo') or {}).get('start') or \
                    (rep.get('heard') or {}).get('bpm')
                if bpm:
                    rep['drum_grid_pct'] = drum_grid(x, bpm)
    return rep


def group(folder):
    songs = collections.defaultdict(dict)
    for f in sorted(os.listdir(folder)):
        p = os.path.join(folder, f)
        if f.lower().endswith(('.stem.mp4', '_stem.mp4')):   # one file: the mix and four stems
            s = re.sub(r'^[0-9a-f]{6,10}-', '', f)[:-9]
            for i, part in enumerate(NI_STEMS):
                songs[s][(part, 'aud')] = f'{p}#{i}'
            continue
        if os.path.isfile(p) and f.lower().endswith(('.mid', '.midi', '.flac', '.wav', '.mp3', '.ogg')):
            s, part = song_key(f)
            kind = 'mid' if f.lower().endswith(('.mid', '.midi')) else 'aud'
            songs[s][(part, kind)] = p
    return songs


def show(name, r):
    print(f'\n=== {name} ===')
    t = r.get('tempo', {})
    print(f"tempo {t.get('start')} BPM (range {t.get('low')}-{t.get('high')}, {t.get('changes')} changes, "
          f"average {t.get('average_from_audio')}) | key {r.get('key')} | {r.get('bars')} bars | {r.get('length_s')} s | "
          f"progression {r.get('progression')}")
    if r.get('heard'):
        print('the app hears', r['heard'])
    if r.get('mix'):
        print('mix', r['mix'])
    for part, form in (r.get('form') or {}).items():
        print(f'  form {part:10s} {form}')
    for part, s in (r.get('parts') or {}).items():
        if s:
            g = ''.join(' ' if v == 0 else ('x' if v > max(s['grid16']) * 0.5 else '.') for v in s['grid16'])
            print(f"  {part:10s} {s['low']}-{s['high']} (median {s['median']}) {s['per_bar']}/bar in {s['active_bars']} bars "
                  f"grid[{g}] lengths {s['lengths'][:3]} chords {s['chords']} repeats {s['repeats_4_bars_back']}")
    for part, s in (r.get('stems') or {}).items():
        if s:
            print(f"  stem {part:10s} {s['level_vs_mix_db']:+.1f} dB vs mix, brightness {s['brightness_hz']} Hz, "
                  f"crest {s['crest_db']} dB, plays {s['plays_pct']}%")
    for k, v in (r.get('drum_grid_pct') or {}).items():
        print(f'  drums {k:5s} ' + ' '.join(f'{x:2d}' for x in v))


def main():
    folder = sys.argv[1]
    out = {}
    for name, files in group(folder).items():
        if not any(f.lower().endswith(('.mid', '.midi')) or '.stem.mp4#' in f for f in files.values()):
            continue                                     # a multitrack song: its parts' MIDI, or a .stem.mp4
        out[name] = analyze_song(files)
        show(name, out[name])
    if '--json' in sys.argv:
        with open(sys.argv[sys.argv.index('--json') + 1], 'w') as f:
            json.dump(out, f, indent=1, default=str)


if __name__ == '__main__':
    main()
