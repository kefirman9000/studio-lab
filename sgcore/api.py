"""High-level entry point used by the CLI and the app."""
import json
import os
import shutil
import time

import numpy as np

from . import dsp
from .compose import Options, compose
from .windows import preview_window, section_window, section_loop
from .render import Renderer, master

OUTPUTS = ('wav', 'mp3', 'midi', 'stems', 'lmms', 'waveform', 'pack', 'daw')


def have_ffmpeg():
    """MP3 export available: ffmpeg on PATH, or the lameenc encoder (bundled with the installer)."""
    return dsp.mp3_encoder() is not None


def song_title(song):
    return f"{song['style']}_{song['key'].name().replace(' ', '-').replace('#', 's')}_{song['bpm']}bpm_seed{song['seed']}"


def _sec_at(song, beat):
    if song.get('tempo_map'):
        from .windows import tempo_seconds
        return tempo_seconds(song['tempo_map'], beat)
    return beat * 60 / song['bpm']


def describe(song):
    dur = _sec_at(song, song['total_bars'] * 4)
    k = song['key']
    return dict(style=song['style'], key=k.name(), bpm=song['bpm'], bars=song['total_bars'],
                duration=f"{int(dur // 60)}:{int(dur % 60):02d}", seconds=round(dur, 1), seed=song['seed'],
                form=' > '.join(f"{s['name']}({s['bars']})" for s in song['sections']),
                chords=k.roman(song['prog_main']), chords_alt=k.roman(song['prog_alt']),
                instruments=_instruments(song), inst_ids=_inst_ids(song), main_ids=_main_ids(song), tracks=_tracks(song),
                meter=song.get('meter', '4/4'),
                bpm_quarter=round(song['bpm'] * 1.5) if song.get('meter') == '3/4' else song['bpm'],
                arrangement=_arrangement(song),
                genre_fit=_fit(song),
                fusion=song['st'].get('fusion') if song['opts'].blend or song['opts'].blend_parts else None,
                sections=[dict(index=x['index'], name=x['name'], bar=x['bar'], bars=x['bars'], src=x['src'], copy=x['copy'],
                               layers=x['layers'], edited=x.get('edited', False),
                               start=round(_sec_at(song, x['bar'] * 4), 2)) for x in song['sections']],
                mood=song['opts'].mood,
                tempo_range=[round(min(v for _, v in song['tempo_map'])), round(max(v for _, v in song['tempo_map']))]
                if song.get('tempo_map') else None)


def _nice(name):
    """'sf:cello' -> 'cello (recorded)', 'supersaw_lead' -> 'Supersaw lead', VST sounds by their saved name."""
    if not isinstance(name, str):
        return name
    if name.startswith(('vst:', 'user:')):
        return _inst_label(name)
    from .instruments import INSTRUMENT_INFO
    if name.startswith('real:'):
        from . import samplelibs as sl
        lab = next((c[1] for c in sl.CHOICES if c[0] == name[5:]), None)
        if lab:
            return lab + ' (real)'
        from . import soundfont as sfm
        hit = sfm.SAMPLED.get(name[5:])
        return (hit[2] if hit else name[5:]) + ' (real)'
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
        if t.get('switch_of') == 'bass' and 'bass' in out:
            out['bass'] += ' / ' + _nice(t['inst'])          # bass voices that trade bars in the drop
        elif t.get('switch_of') in out:                      # instrument rotation between sections
            where = ' & '.join({'A': 'verses', 'B': 'choruses', 'C': 'breaks'}[g] for g in t.get('groups', ()))
            out[t['switch_of']] += f' · {where}: ' + _nice(t['inst'])
    return out


TRACK_ROLE_LABEL = {'kick': 'Kick', 'snare': 'Snare / clap', 'top': 'Hats & percussion', 'bass': 'Bass', 'chords': 'Chords',
                    'pad': 'Pad', 'arp': 'Arp', 'lead': 'Lead', 'fx': 'FX / texture'}


DRUM_PART = {'chat': 'Closed hi-hat', 'ohat': 'Open hi-hat', 'rim': 'Rimshot', 'shaker': 'Shaker', 'clap': 'Clap', 'tamb': 'Tambourine',
             'ride': 'Ride cymbal', 'crash': 'Crash cymbal', 'conga': 'Congas', 'snap': 'Finger snaps', 'woodblock': 'Wood block',
             'tabla': 'Tabla', 'cowbell808': 'Cowbell', 'tom_hi': 'High tom (fills)', 'tom_mid': 'Mid tom (fills)',
             'tom_lo': 'Low tom (fills)', 'bride': 'Build-up ride', 'lkick': 'Layered kick', 'lsnare': 'Layered snare',
             'vinyl': 'Vinyl crackle', 'texture': 'Background texture', 'timp': 'Timpani', 'bodhran': 'Bodhran',
             'taiko': 'Taiko drums', 'bdrum': 'Orchestral bass drum', 'bayan': 'Tabla (bass drum)', 'manjira': 'Manjira (hand cymbals)', 'dholak': 'Dholak (bass)', 'dholak_ta': 'Dholak (treble)', 'chipkick': 'Chip kick',
             'tom': 'Tom-toms', 'kick': 'Kick', 'snare': 'Snare', 'anvil': 'Anvil', 'chiphat': 'Chip hi-hat',
             'chipsnare': 'Chip snare', 'sleigh': 'Sleigh bells', 'timbale': 'Timbales'}


def _tracks(song):
    """Every part that actually plays in this song (main parts, extras, layers, section switches, build-up drums ...),
    so the editor can show and change each one."""
    used = {}
    for e in song['events']:
        used[e.track] = used.get(e.track, 0) + 1
    out = []
    for t in song['st']['tracks']:
        n = used.get(t['name'], 0)
        if not n and t['layer'] != 'fx':
            continue
        if t['name'] == t['layer']:
            what = TRACK_ROLE_LABEL.get(t['layer'], t['layer'])
        elif t.get('switch_of'):
            what = f"{TRACK_ROLE_LABEL.get(t['switch_of'], t['switch_of'])} (other sections)"
        elif t.get('double_of'):
            what = f"{TRACK_ROLE_LABEL.get(t['layer'], t['layer'])} layer"
        elif t.get('counter'):
            what = 'Counter-melody'
        else:
            what = DRUM_PART.get(t['name']) or DRUM_PART.get(t['inst']) or t['name'].replace('_', ' ').capitalize()
        if t['name'] == t['inst'] and t['name'] in DRUM_PART and t['name'] != t['layer']:
            what = DRUM_PART[t['name']]
        out.append(dict(id=t['name'], layer=t['layer'], inst=t['inst'], sound=_nice(t['inst']), part=what, notes=n,
                        drum=t['layer'] in ('kick', 'snare', 'top') or t['layer'] == 'fx'))
    return out


def _main_ids(song):
    """{part: the instrument id its main track played} - what 'Keep my picks' holds for the next song. A sound swapped
    for a recorded or plugin version reports what was asked for (so it can be asked for again)."""
    out = {}
    for t in song['st']['tracks']:
        if t['layer'] in ('bass', 'chords', 'pad', 'arp', 'lead') and t['name'] == t['layer'] and not t.get('off'):
            inst = t['inst']
            if inst.startswith('real:'):
                inst = t.get('real_from') or inst
            elif inst.startswith('vst:') and t.get('fallback') and not t.get('user_pick'):
                inst = t['fallback']
            out[t['layer']] = inst
    return out


def _inst_ids(song):
    """{part: [instrument ids]} actually used (main + rotation), for 'don't repeat what I just heard'."""
    out = {}
    for t in song['st']['tracks']:
        role = t.get('switch_of') or t['layer']
        if role in ('bass', 'chords', 'pad', 'arp', 'lead') and not t.get('double_of') and not t.get('counter'):
            out.setdefault(role, [])
            if t['inst'] not in out[role]:
                out[role].append(t['inst'])
    return out


def _fit(song):
    try:
        from .fitness import genre_fit
        return genre_fit(song)
    except Exception:
        return None


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
    n = sum(1 for t in st['tracks'] if t.get('double_of') and not (t['layer'] == 'bass' and t['inst'] == 'sinebass'))
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


def trim_lead_in(out, keep=1.0, rel_db=-40.0):
    """Cut quiet space before the music starts so at most `keep` seconds remain. 'Starts' = the first moment the mix
    gets within `rel_db` of its loud parts (so a barely-audible pad fade-in or a lone room tail counts as empty).
    Only the finished mix is trimmed; stems and MIDI keep the full timeline so they still line up in a DAW."""
    from .dsp import SR
    x = np.asarray(out)
    mono = np.abs(x).max(axis=0) if x.ndim == 2 else np.abs(x)
    w = int(0.02 * SR)
    n = len(mono) // w
    if n < 10:
        return out, 0.0
    rms = np.sqrt(np.mean((mono[:n * w].reshape(n, w)) ** 2, axis=1)) + 1e-12
    ref = np.percentile(rms, 95)
    hits = np.nonzero(rms > ref * 10 ** (rel_db / 20))[0]
    if not len(hits):
        return out, 0.0
    start = hits[0] * w
    cut = start - int(keep * SR)
    if cut <= int(0.05 * SR):
        return out, 0.0
    y = x[:, cut:].copy() if x.ndim == 2 else x[cut:].copy()
    f = min(int(0.03 * SR), y.shape[-1])
    ramp = np.linspace(0.0, 1.0, f) ** 2
    if y.ndim == 2:
        y[:, :f] *= ramp
    else:
        y[:f] *= ramp
    return y, cut / SR


def trim_tail(out, keep=2.5, rel_db=-60.0):
    from .dsp import SR
    """Drop dead silence after the last sound (a reverb tail fading below `rel_db` of the loud parts), keeping `keep` s."""
    x = np.asarray(out)
    mono = np.abs(x).max(axis=0) if x.ndim == 2 else np.abs(x)
    w = int(0.05 * SR)
    n = len(mono) // w
    if n < 10:
        return out, 0.0
    rms = np.sqrt(np.mean((mono[:n * w].reshape(n, w)) ** 2, axis=1)) + 1e-12
    hits = np.nonzero(rms > np.percentile(rms, 95) * 10 ** (rel_db / 20))[0]
    if not len(hits):
        return out, 0.0
    end = min(x.shape[-1], (hits[-1] + 1) * w + int(keep * SR))
    cut = x.shape[-1] - end
    if cut <= int(0.5 * SR):
        return out, 0.0
    y = x[..., :end].copy()
    f = min(int(1.0 * SR), y.shape[-1])
    y[..., -f:] *= np.linspace(1.0, 0.0, f) ** 2
    return y, cut / SR


def wrap_loop(x, seconds):
    """Cut audio to exactly one loop and fold everything that rings past the end (reverb, delays, long notes) back
    onto the start, so it repeats without a gap or a click."""
    from .dsp import SR
    n = int(round(seconds * SR))
    if n <= 0 or x.shape[-1] <= n:
        return x
    y = x[..., :n].copy()
    tail = x[..., n:2 * n]
    y[..., :tail.shape[-1]] += tail
    pk = float(np.max(np.abs(y)))
    ceiling = 10 ** (-1.0 / 20)
    if pk > ceiling:
        y *= ceiling / pk
    return y


def generate(opts, outdir, outputs=('wav',), preview=False, log=print, progress=None, prefs=None, section=None, loop=False):
    """Compose + render + master + write requested outputs. Returns dict with info and file paths."""
    if isinstance(opts, dict):
        opts = Options.from_dict(opts)
    dsp.seed_rng(opts.seed)
    t0 = time.time()
    song = compose(opts)
    info = describe(song)
    full_song = song
    loop = bool(loop) and section is not None and 0 <= int(section) < len(song['sections'])
    if loop:
        song = section_loop(song, int(section))
        preview = True
        info['previewed_section'] = int(section)
        info['loop'] = True
    elif section is not None and 0 <= int(section) < len(song['sections']):
        song = section_window(song, int(section))
        preview = True
        info['previewed_section'] = int(section)
    elif preview:
        song = preview_window(song)
    from .names import song_name, slug
    name = song_name(full_song)
    info['name'] = name
    title = slug(name) + '_' + song_title(song) + ('_loop' if loop else '') + (f'_sec{int(section)}_{abs(hash(json.dumps(opts.sections, sort_keys=True, default=str))) % 10**6}'
                                if section is not None else ('_preview' if preview else ''))
    os.makedirs(outdir, exist_ok=True)
    log(f"== \"{name}\"")
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
    if loop:
        out = wrap_loop(out, r._bt(song['total_bars'] * 4))
        info['loop_seconds'] = round(out.shape[-1] / dsp.SR, 3)
    out, trimmed = (out, 0.0) if loop else trim_lead_in(out)
    if trimmed > 0.05:
        log(f'   trimmed {trimmed:.1f} s of near-silent lead-in (at most 1 s left before the music)')
        info['trimmed_lead_in'] = round(trimmed, 2)
    out, tail = (out, 0.0) if loop else trim_tail(out)
    if tail > 0.5:
        info['trimmed_tail'] = round(tail, 2)
    files = {}
    wav = os.path.join(outdir, title + '.wav')
    dsp.write_wav(wav, out)
    files['wav'] = wav
    loud = dsp.lufs(out)
    peak = 20 * np.log10(np.max(np.abs(out)) + 1e-12)
    log(f'   master: {loud:.1f} LUFS, peak {peak:.1f} dBFS')
    if 'mp3' in outputs and have_ffmpeg():
        mp3 = dsp.write_mp3(wav, wav[:-4] + '.mp3', 320, dict(title=name, genre=info['style'], artist='Studio Lab'))
        if mp3:
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
    if song['st'].get('orch_note'):
        info['orch_note'] = song['st']['orch_note']
    from . import drumkits
    k = drumkits.MENU.get(song['st'].get('kit_id') or '')
    if k:
        info['kit'] = k[2] + (' (real drums)' if song['st'].get('real_kit') else '')
    info.update(files=files, loudness=round(loud, 1), peak=round(peak, 1), render_seconds=round(time.time() - t0, 1),
                preview=preview)
    log(f'   done in {time.time() - t0:.0f}s')
    if progress:
        progress(1.0)
    return info
