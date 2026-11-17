"""Sample pack export: tempo-synced loops for every part, one-shots and MIDI loops."""
import os
import shutil
import tempfile

import numpy as np

from . import dsp
from .windows import loop_window
from .theory import voice_chord
from .instruments import DRUMS, INSTRUMENTS
from .render import Renderer, master


def _norm(x, peak_db=-1.0):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.vstack([x, x])
    pk = np.max(np.abs(x)) or 1.0
    return x * (10 ** (peak_db / 20) / pk)


def write_pack(folder, song, bars=8, log=print):
    key = song['key']
    tag = f"{song['bpm']}bpm_{key.name().replace(' ', '')}"
    loops = os.path.join(folder, 'Loops')
    shots = os.path.join(folder, 'One-shots')
    midis = os.path.join(folder, 'MIDI')
    for d in (loops, shots, midis):
        os.makedirs(d, exist_ok=True)
    # ---- loops: render an exact N-bar window, one file per part + full mix
    win = loop_window(song, bars)
    n = int(round(win['total_bars'] * 4 * 60 / song['bpm'] * dsp.SR))
    tmp = tempfile.mkdtemp()
    r = Renderer(win, log=lambda *a: None)
    mix = r.render(tmp)
    for s in r.stems:
        if s.get('bus') or s['name'] in ('reverb_delay',):
            continue
        a = np.fromfile(s['path'], dtype='<f4', offset=58).reshape(-1, 2).T[:, :n]
        if np.max(np.abs(a)) < 1e-5:
            continue
        dsp.write_wav(os.path.join(loops, f"{song['style']}_{s['name']}_loop_{tag}.wav"), _norm(a, -1.0))
    full = master(mix, song['st']['master'], log=lambda *a: None)[:, :n]
    dsp.write_wav(os.path.join(loops, f"{song['style']}_FULL_loop_{tag}.wav"), full)
    shutil.rmtree(tmp, ignore_errors=True)
    # ---- MIDI loops
    from .exporters import write_part_midis
    write_part_midis(midis, win)
    # ---- one-shots
    st = song['st']
    kit = st.get('kitparams', {})
    for t in st['tracks']:
        name, inst = t['name'], t['inst']
        if inst in DRUMS:
            y = DRUMS[inst](kit.get(inst, {}))
            dsp.write_wav(os.path.join(shots, f"{song['style']}_{name}.wav"), _norm(y, -0.5))
            continue
        if inst not in INSTRUMENTS:
            continue
        p = dict(t['p'], spb=60.0 / song['bpm'])
        if t['layer'] == 'bass':
            m = key.deg(0, 2)
            y = INSTRUMENTS[inst](m, 0.6, p, None, 0.5)
            dsp.write_wav(os.path.join(shots, f"{song['style']}_{name}_{key.name().split()[0]}.wav"), _norm(y))
        else:
            notes = voice_chord(key, 0, 3, 62) if t['layer'] in ('chords', 'pad') else [key.deg(0, 4)]
            dur = 2.0 if t['layer'] == 'pad' else 0.8
            parts = [INSTRUMENTS[inst](m, dur, p, None, 0.5) for m in notes]
            ln = max(x.shape[-1] for x in parts)
            acc = np.zeros((2, ln))
            for x in parts:
                x = x if x.ndim == 2 else np.vstack([x, x])
                acc[:, :x.shape[1]] += x
            label = 'chord' if len(notes) > 1 else 'note'
            dsp.write_wav(os.path.join(shots, f"{song['style']}_{name}_{label}_{key.name().split()[0]}.wav"), _norm(acc))
    with open(os.path.join(folder, 'README.txt'), 'w') as f:
        f.write(f"Sample pack - {song['style']}, {song['bpm']} BPM, key {key.name()}\n\n"
                f"Loops/     {bars}-bar loops of every part plus the full mix, cut exactly on the bar.\n"
                "One-shots/ single drum hits, plus notes/chords of each instrument at the song's root note.\n"
                "MIDI/      the same loops as MIDI, one file per part.\n")
    log(f'   sample pack: {folder}')
    return folder
