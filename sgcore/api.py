"""High-level entry point used by the CLI and the app."""
import json
import os
import re
import shutil
import subprocess
import time

import numpy as np

from . import dsp
from .compose import Options, compose, preview_window
from .render import Renderer, master
from .styles import STYLES

OUTPUTS = ('wav', 'mp3', 'midi', 'stems', 'lmms', 'waveform')


def have_ffmpeg():
    return shutil.which('ffmpeg') is not None


def song_title(song):
    return f"{song['style']}_{song['key'].name().replace(' ', '-').replace('#', 's')}_{song['bpm']}bpm_seed{song['seed']}"


def describe(song):
    dur = song['total_bars'] * 4 * 60 / song['bpm']
    k = song['key']
    return dict(style=song['style'], key=k.name(), bpm=song['bpm'], bars=song['total_bars'],
                duration=f"{int(dur // 60)}:{int(dur % 60):02d}", seconds=round(dur, 1), seed=song['seed'],
                form=' > '.join(f"{s['name']}({s['bars']})" for s in song['sections']),
                chords=k.roman(song['prog_main']), chords_alt=k.roman(song['prog_alt']),
                instruments={t['layer']: t['inst'] for t in song['st']['tracks']
                             if t['layer'] in ('bass', 'chords', 'pad', 'arp', 'lead')},
                fusion=song['st'].get('fusion') if song['opts'].blend or song['opts'].blend_parts else None,
                mood=song['opts'].mood)


def generate(opts, outdir, outputs=('wav',), preview=False, log=print, progress=None, prefs=None):
    """Compose + render + master + write requested outputs. Returns dict with info and file paths."""
    if isinstance(opts, dict):
        opts = Options.from_dict(opts)
    dsp.seed_rng(opts.seed)
    t0 = time.time()
    song = compose(opts)
    info = describe(song)
    if preview:
        song = preview_window(song)
    title = song_title(song) + ('_preview' if preview else '')
    os.makedirs(outdir, exist_ok=True)
    log(f"== {info['style']} | {info['key']} | {info['bpm']} BPM | {info['duration']} | seed {opts.seed}")
    log(f"   form: {info['form']}")
    log(f"   chords: {info['chords']}  (alt {info['chords_alt']})")
    if info.get('fusion'):
        log('   fusion: ' + ', '.join(f'{p}<-{s}' for p, s in info['fusion'].items()))
    stems_dir = None
    outputs = set(outputs)
    if not preview and ({'stems', 'waveform'} & outputs):
        stems_dir = os.path.join(outdir, title + '_stems')
        os.makedirs(stems_dir, exist_ok=True)
    r = Renderer(song, log=log)
    mix = r.render(stems_dir, progress=progress)
    r.premaster_peak = float(np.max(np.abs(mix)))
    out = master(mix, song['st']['master'], log=log)
    files = {}
    wav = os.path.join(outdir, title + '.wav')
    dsp.write_wav(wav, out)
    files['wav'] = wav
    loud = dsp.lufs(out)
    peak = 20 * np.log10(np.max(np.abs(out)) + 1e-12)
    log(f'   master: {loud:.1f} LUFS, peak {peak:.1f} dBFS')
    if 'mp3' in outputs and have_ffmpeg():
        mp3 = wav[:-4] + '.mp3'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-codec:a', 'libmp3lame', '-b:a', '320k', mp3], check=True)
        files['mp3'] = mp3
    if not preview:
        from . import exporters
        full = song
        from .plugins import song_recommendations
        p = prefs or {}
        song['plugin_recs'] = song_recommendations(song, p.get('owned', []), p.get('daws') or ['lmms', 'waveform'],
                                                   p.get('os', 'windows'), p.get('found'))
        if 'midi' in outputs:
            files['midi'] = exporters.write_midi(os.path.join(outdir, title + '.mid'), full)
        if 'lmms' in outputs:
            files['lmms'] = exporters.write_lmms(os.path.join(outdir, title + '.mmp'), full)
        if 'waveform' in outputs:
            files['waveform'] = exporters.write_waveform(os.path.join(outdir, title + '_waveform'), full, r, wav)
        if stems_dir and 'stems' in outputs:
            files['stems'] = stems_dir
        elif stems_dir:
            shutil.rmtree(stems_dir, ignore_errors=True)
        with open(os.path.join(outdir, title + '_settings.json'), 'w') as f:
            json.dump(dict(options=opts.to_dict(), info=info), f, indent=2)
        from . import plugins
        files['guide'] = plugins.write_guide(os.path.join(outdir, title + '_PLUGIN_GUIDE.txt'), song, prefs)
    if 'wav' not in outputs and 'mp3' in files and not preview:
        os.remove(wav)
        files.pop('wav')
    if not preview and song.get('plugin_recs'):
        info['plugins'] = {k: v['picks'] for k, v in song['plugin_recs'].items()}
    info.update(files=files, loudness=round(loud, 1), peak=round(peak, 1), render_seconds=round(time.time() - t0, 1),
                preview=preview)
    log(f'   done in {time.time() - t0:.0f}s')
    if progress:
        progress(1.0)
    return info
