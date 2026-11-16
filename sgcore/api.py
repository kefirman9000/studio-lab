"""High-level entry point used by the CLI and the app."""
import json
import os
import re
import shutil
import subprocess
import time

import numpy as np

from . import dsp
from .compose import Options, compose, preview_window, section_window, loop_window
from .render import Renderer, master
from .styles import STYLES

OUTPUTS = ('wav', 'mp3', 'midi', 'stems', 'lmms', 'waveform', 'pack', 'daw')


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
                instruments=_instruments(song),
                meter=song.get('meter', '4/4'),
                bpm_quarter=round(song['bpm'] * 1.5) if song.get('meter') == '3/4' else song['bpm'],
                arrangement=_arrangement(song),
                fusion=song['st'].get('fusion') if song['opts'].blend or song['opts'].blend_parts else None,
                sections=[dict(index=x['index'], name=x['name'], bar=x['bar'], bars=x['bars'], src=x['src'], copy=x['copy'],
                               layers=x['layers'], edited=x.get('edited', False),
                               start=round(x['bar'] * 4 * 60 / song['bpm'], 2)) for x in song['sections']],
                mood=song['opts'].mood)


def _nice(name):
    """'sf:cello' -> 'cello (recorded)', 'supersaw_lead' -> 'Supersaw lead', VST sounds by their saved name."""
    if not isinstance(name, str):
        return name
    if name.startswith(('vst:', 'user:')):
        return _inst_label(name)
    from .instruments import INSTRUMENT_INFO
    if name.startswith('sf:'):
        from . import soundfont as sfm
        hit = sfm.SAMPLED.get(name[3:])
        return (hit[2] if hit else name[3:]) + ' (recorded)'
    return INSTRUMENT_INFO.get(name, name).split(' (')[0]


def _instruments(song):
    """{part: 'Supersaw lead + Bell (8va)'} - the main instrument of each part plus any layer doubling it."""
    out = {}
    tracks = song['st']['tracks']
    for t in tracks:
        if t['layer'] in ('bass', 'chords', 'pad', 'arp', 'lead') and not t.get('double_of') and not t.get('counter'):
            out.setdefault(t['layer'], _nice(t['inst']))
    for t in tracks:
        src = next((x for x in tracks if x['name'] == t.get('double_of')), None)
        if src and src['layer'] in out:
            o = {12: ' (8va)', -12: ' (8vb)'}.get(t.get('octave', 0), '')
            out[src['layer']] += ' + ' + _nice(t['inst']) + o
        if t.get('counter'):
            out['counter'] = _nice(t['inst'])
    return out


def _arrangement(song):
    """Short tags for the result card: what makes this take different."""
    st = song['st']
    tags = []
    if song.get('meter', '4/4') != '4/4':
        tags.append(song['meter'])
    dev = st.get('lead_device')
    if dev and dev != 'hook':
        tags.append({'call': 'call & response lead', 'riff': 'riff lead', 'arp': 'arpeggio lead', 'ostinato': 'ostinato lead',
                     'bell': 'bell melody', 'chops': 'vocal-chop lead'}.get(dev, dev + ' lead'))
    if any(t.get('counter') for t in st['tracks']):
        tags.append('counter-melody')
    n = sum(1 for t in st['tracks'] if t.get('double_of'))
    if n:
        tags.append(f'{n} layered part' + ('s' if n > 1 else ''))
    if song.get('harm_alts'):
        tags.append('secondary dominants')
    if st.get('voicing') not in (None, 'close'):
        tags.append(st['voicing'] + ' voicings')
    if any(s_.get('key_change') for s_ in song['sections']):
        tags.append('key change')
    if any(s_.get('picardy') for s_ in song['sections']):
        tags.append('major-chord ending')
    return tags


def _inst_label(name):
    if isinstance(name, str) and name.startswith('vst:'):
        try:
            from . import vsthost
            snd = vsthost.get_sound(name[4:])
            return 'VST: ' + (snd or {}).get('name', name[4:])
        except Exception:
            return name
    if isinstance(name, str) and name.startswith('user:'):
        return 'my sample: ' + name[5:]
    return name


def generate(opts, outdir, outputs=('wav',), preview=False, log=print, progress=None, prefs=None, section=None):
    """Compose + render + master + write requested outputs. Returns dict with info and file paths."""
    if isinstance(opts, dict):
        opts = Options.from_dict(opts)
    dsp.seed_rng(opts.seed)
    t0 = time.time()
    song = compose(opts)
    info = describe(song)
    full_song = song
    if section is not None and 0 <= int(section) < len(song['sections']):
        song = section_window(song, int(section))
        preview = True
        info['previewed_section'] = int(section)
    elif preview:
        song = preview_window(song)
    title = song_title(song) + (f'_sec{int(section)}_{abs(hash(json.dumps(opts.sections, sort_keys=True, default=str))) % 10**6}'
                                if section is not None else ('_preview' if preview else ''))
    os.makedirs(outdir, exist_ok=True)
    log(f"== {info['style']} | {info['key']} | {info['bpm']} BPM | {info['duration']} | seed {opts.seed}")
    log(f"   form: {info['form']}")
    log(f"   chords: {info['chords']}  (alt {info['chords_alt']})")
    if info.get('fusion'):
        log('   fusion: ' + ', '.join(f'{p}<-{s}' for p, s in info['fusion'].items()))
    stems_dir = None
    outputs = set(outputs)
    if not preview and ({'stems', 'waveform', 'daw'} & outputs):
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
            files['parts'] = exporters.write_part_midis(os.path.join(outdir, title + '_parts'), full)
        if 'pack' in outputs:
            from .samplepack import write_pack
            files['pack'] = write_pack(os.path.join(outdir, title + '_samplepack'), full, log=log)
        if 'lmms' in outputs:
            files['lmms'] = exporters.write_lmms(os.path.join(outdir, title + '.mmp'), full)
        if 'waveform' in outputs:
            files['waveform'] = exporters.write_waveform(os.path.join(outdir, title + '_waveform'), full, r, wav)
        if 'daw' in outputs:
            files['daw'] = exporters.write_daw_pack(os.path.join(outdir, title + '_DAW'), full, r, wav, log=log)
        if stems_dir and 'stems' in outputs:
            files['stems'] = stems_dir
        elif stems_dir:
            shutil.rmtree(stems_dir, ignore_errors=True)
        if isinstance(files.get('parts'), dict):
            info['parts'] = files.pop('parts')
        with open(os.path.join(outdir, title + '_settings.json'), 'w') as f:
            json.dump(dict(options=opts.to_dict(), info=info), f, indent=2)
        from . import plugins
        files['guide'] = plugins.write_guide(os.path.join(outdir, title + '_PLUGIN_GUIDE.txt'), song, prefs)
    if 'wav' not in outputs and 'mp3' in files and not preview:
        os.remove(wav)
        files.pop('wav')
    if not preview and song.get('plugin_recs'):
        info['plugins'] = {k: v['picks'] for k, v in song['plugin_recs'].items()}
    if getattr(r, 'vst_failures', None):
        info['warnings'] = r.vst_failures
    info.update(files=files, loudness=round(loud, 1), peak=round(peak, 1), render_seconds=round(time.time() - t0, 1),
                preview=preview)
    log(f'   done in {time.time() - t0:.0f}s')
    if progress:
        progress(1.0)
    return info
