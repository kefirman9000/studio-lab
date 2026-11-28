"""(2.30) Release exports: stock-music cutdowns, a seamless full-song loop and a release folder.

- cutdowns: 60 / 30 / 15 second edits of the finished master that start and end like a song - the opening bars,
  then the hook (the first drop / chorus) and the song's own last bars with their ring-out. Every join is on a bar
  line with a short equal-power crossfade, so the beat never skips. Stock libraries ask for these next to the full track.
- seamless_loop: the whole song cut exactly at its last bar, with everything that rings past the end (reverb, delay,
  the last notes) folded back onto the start - it repeats without a gap or a click (for long loop videos).
- write_release: one folder per song with the master, the cutdowns, the loop and a release.json that describes the
  song (title, genre, tempo, key, length, loudness, files) for an uploader to read.
Nothing is re-rendered: all of it is cut from the master that was just made.
"""
import json
import os
import shutil

import numpy as np

from .dsp import SR

HOOK = ('drop', 'chorus', 'hook', 'main', 'theme', 'peak')
LENGTHS = (60, 30, 15)


def _idx(r, beat):
    return int(round(r._bt(beat) * SR))


def hook_bar(song):
    """The bar where the song's hook first arrives: the first drop / chorus, else the section that plays loudest."""
    secs = song.get('sections') or []
    for s in secs:
        if any(h in str(s.get('name', '')).lower() for h in HOOK):
            return int(s['bar'])
    lv = [(s['opts'].get('level', 0.0), -i, s) for i, s in enumerate(secs) if isinstance(s.get('opts'), dict)]
    if lv:
        return int(max(lv, key=lambda x: x[:2])[2]['bar'])
    return 0


def _join(a, b, xf):
    """a then b with an equal-power crossfade of xf samples over the join."""
    if a is None or a.shape[-1] == 0:
        return b
    xf = int(min(xf, a.shape[-1], b.shape[-1]))
    if xf <= 0:
        return np.concatenate([a, b], axis=-1)
    t = np.linspace(0, np.pi / 2, xf)
    mid = a[..., -xf:] * np.cos(t) + b[..., :xf] * np.sin(t)
    return np.concatenate([a[..., :-xf], mid, b[..., xf:]], axis=-1)


def cutdowns(out, song, r, lengths=LENGTHS, xf_ms=40, max_tail=4.0):
    """{seconds: audio} - an edit of each length that fits in the song (a 60 s edit of a 70 s song is skipped).
    `out` is the master before the lead-in / tail trims, so beat 0 is sample 0."""
    total = int(song['total_bars'])
    bar = r._bt(4) - r._bt(0)
    if bar <= 0 or total < 4:
        return {}
    music_end = _idx(r, total * 4)
    tail = out[..., music_end:music_end + int(max_tail * SR)]
    if tail.shape[-1] > 256:                                   # fade what's left of the ring-out so it ends cleanly
        tail = tail * np.linspace(1, 0, tail.shape[-1]) ** 2
    hb = min(hook_bar(song), total - 4)
    xf = int(xf_ms / 1000 * SR)
    res = {}
    for L in lengths:
        if out.shape[-1] / SR < L + 2 * bar:
            continue
        end_bars = 1 if L <= 15 else 2
        intro_bars = 0 if L <= 15 or hb < 2 else 2
        end_s = end_bars * bar + tail.shape[-1] / SR
        body = int((L - end_s - intro_bars * bar) // bar)      # whole bars: as close to the length as fits under it
        if body < 2 and intro_bars:
            intro_bars, body = 0, int((L - end_s) // bar)
        if body < 2:
            continue
        b1 = min(hb + body, total - end_bars)
        if b1 - hb < 2:
            continue
        x = out[..., 0:_idx(r, intro_bars * 4)] if intro_bars else None
        x = _join(x, out[..., _idx(r, hb * 4):_idx(r, b1 * 4)], xf)
        x = _join(x, out[..., _idx(r, (total - end_bars) * 4):music_end], xf)
        x = np.concatenate([x, tail], axis=-1)
        res[L] = x
    return res


def seamless_loop(out, song, r):
    """The whole song, cut at its last bar, with the ring-out folded back onto the start: it repeats seamlessly."""
    from .api import wrap_loop
    return wrap_loop(out, r._bt(int(song['total_bars']) * 4))


def write_release(folder, title, name, info, files, extra_files, song):
    """Copy the song's files into `folder` and describe it in release.json. -> folder."""
    os.makedirs(folder, exist_ok=True)
    listed = {}
    for k, p in list(files.items()) + list(extra_files.items()):
        if isinstance(p, str) and os.path.isfile(p):
            dst = os.path.join(folder, os.path.basename(p))
            if os.path.abspath(dst) != os.path.abspath(p):
                shutil.copy2(p, dst)
            listed[k] = os.path.basename(p)
        elif isinstance(p, str) and os.path.isdir(p) and k == 'stems':
            dst = os.path.join(folder, 'stems')
            if not os.path.exists(dst):
                shutil.copytree(p, dst)
            listed[k] = 'stems/'
    from .styles import STYLES
    st = STYLES.get(str(song.get('style') or '').split('+')[0]) or {}
    meta = dict(
        title=name, genre=st.get('label') or str(info.get('style') or '').replace('_', ' ').title(), genre_id=info.get('style'),
        category=song['st'].get('category'), bpm=info.get('bpm'), key=info.get('key'),
        duration_seconds=info.get('seconds'), loudness_lufs=info.get('loudness'), peak_dbfs=info.get('peak'),
        instruments=info.get('instruments'), made_with='Studio Lab', seed=info.get('seed'),
        files=listed, cutdowns={k: v for k, v in listed.items() if k.startswith('cut')},
    )
    with open(os.path.join(folder, 'release.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, default=str)
    return folder
