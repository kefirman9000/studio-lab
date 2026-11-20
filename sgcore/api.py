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
    if name == 'sung':
        return 'Singer'
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
             'taiko': 'Taiko drums', 'bdrum': 'Orchestral bass drum', 'bayan': 'Tabla (bass drum)', 'manjira': 'Manjira (hand cymbals)', 'dholak': 'Dholak (bass)', 'dholak_ta': 'Dholak (treble)', 'bongo': 'Bongo (high)', 'bongo_lo': 'Bongo (low)', 'chipkick': 'Chip kick',
             'tom': 'Tom-toms', 'kick': 'Kick', 'snare': 'Snare', 'anvil': 'Anvil', 'chiphat': 'Chip hi-hat',
             'chipsnare': 'Chip snare', 'sleigh': 'Sleigh bells', 'triangle': 'Triangle', 'windchime': 'Wind chimes', 'timbale': 'Timbales'}


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
    mcfg = dict(song['st']['master'])
    out = master(mix, mcfg, log=log)
    if getattr(opts, 'production_pass', False) and not loop:
        out, info['production_pass'] = production_pass(mix, mcfg, out, log=log)
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
    try:
        from .render import mix_report
        info['mix_report'] = mix_report(out, song, tone=song['st']['master'].get('tone'), low_env=getattr(r, 'low_env', None),
                                        dyn_eq=getattr(master, 'last_dyn_eq', None))
        mr = info['mix_report']
        log(f"   mix check: {mr['true_peak']} dBTP, PLR {mr['plr']} dB, correlation {mr['correlation']}, low-end side "
            f"{mr['low_side_db']} dB, section contrast {mr['section_contrast']} dB" + (' - ' + '; '.join(mr['warnings']) if mr['warnings'] else ' - OK'))
    except Exception as e:                                 # the report is a bonus - never fail a render for it
        log(f'   (mix check skipped: {e})')
    if 'wav24' in outputs or 'flac' in outputs:          # the master at full resolution: 24-bit, no dither
        w24 = dsp.write_wav(os.path.join(outdir, title + '_24bit.wav'), out, bits=24)
        if 'flac' in outputs:
            fl = dsp.write_flac(w24, w24[:-4] + '.flac')
            if fl:
                files['flac'] = fl
        if 'wav24' in outputs:
            files['wav24'] = w24
        else:
            os.remove(w24)
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
    info['part_effects'] = song.get('part_effects') or {}
    info['drum_picks'] = song.get('drum_picks') or {}
    info.update(files=files, loudness=round(loud, 1), peak=round(peak, 1), render_seconds=round(time.time() - t0, 1),
                preview=preview)
    log(f'   done in {time.time() - t0:.0f}s')
    if progress:
        progress(1.0)
    return info


def song_notes(opts):
    """The song editor's note timeline: compose only (no audio) and return every sound's notes, the sections and each
    sound's programmed volume line (full level where its part plays, silent where it rests)."""
    if isinstance(opts, dict):
        opts = Options.from_dict(opts)
    song = compose(opts)
    tracks = _tracks(song)
    notes = {}
    for e in song['events']:
        notes.setdefault(e.track, []).append([round(float(e.beat), 3), round(float(e.dur), 3),
                                              None if e.midi is None else int(e.midi), round(float(e.vel), 2)])
    secs = [dict(name=x['name'], bar=x['bar'], bars=x['bars'], layers=x['layers']) for x in song['sections']]
    by_name = {t['name']: t for t in song['st']['tracks']}
    prog = {}
    for tr in tracks:
        lay = (by_name.get(tr['id']) or {}).get('layer', tr['layer'])
        pts = []
        for x in secs:
            v = 0.0 if lay in x['layers'] else -60.0
            pts += [[x['bar'] * 4.0, v], [(x['bar'] + x['bars']) * 4.0 - 0.01, v]]
        prog[tr['id']] = pts
    return dict(tracks=tracks, notes=notes, sections=secs, beats=song['total_bars'] * 4, bpm=song['bpm'],
                programmed=prog, automation=dict(getattr(opts, 'automation', None) or {}),
                note_edits=getattr(opts, 'note_edits', None) or {})


def production_pass(mix, cfg, out, log=print):
    """A second mastering pass, driven by the mix check: what an engineer would change after listening back.
    Too wide / phasey -> narrower; squashed -> less limiting and a quieter target; tone far from the genre's references
    -> a stronger tone match; harsh highs that build up -> a stronger dynamic EQ. Masters again from the same mix (fast:
    nothing is re-rendered) and keeps the new master only if the new check is better. -> (master, [changes])."""
    from .render import mix_report, master
    rep = mix_report(out, tone=cfg.get('tone'))
    c = dict(cfg)
    changes = []
    if rep['correlation'] < 0.3 or rep['mono_drop'] > 1.5:
        c['width'] = float(c.get('width', 1.0)) * 0.8
        c['min_corr'] = 0.45                              # (the width guard's target: the wide parts stop cancelling)
        changes.append('narrower stereo (it lost level in mono)')
    if rep['plr'] < 8.0:
        c['max_gr'] = max(1.0, float(c.get('max_gr', 3.0)) - 1.5)
        c['lufs'] = float(c.get('lufs', -10)) - 1.0
        changes.append('less limiting, 1 dB quieter (it was squashed)')
    if rep.get('tone_dev') and max(abs(d) for d in rep['tone_dev'][:8]) > 4.5 and c.get('tone'):
        c['tone_amount'] = 0.9
        changes.append('stronger tone match to the genre references')
    if rep.get('dyn_eq', {}).get('3600_time', 0) > 0.35:
        c['dyn_eq'] = 1.4
        changes.append('more de-harshing in the loud parts')
    if not changes:
        log('   production pass: the mix check is clean - nothing to change')
        return out, []
    y = master(mix, c, log=lambda *a: None)
    rep2 = mix_report(y, tone=c.get('tone'))
    if len(rep2['warnings']) <= len(rep['warnings']):
        log('   production pass: ' + '; '.join(changes))
        return y, changes
    log('   production pass: tried ' + '; '.join(changes) + ' - the first master was better, kept it')
    return out, []



# ----------------------------------------------------------------------------- 1.84: audition one sound
AUDITION_FIG = {   # role -> [(beat, dur, semitones above the root)] - a tiny figure that shows what the sound does
    'bass': [(0, 0.75, 0), (1, 0.5, 0), (1.5, 0.5, 7), (2, 1.5, 3)],
    'lead': [(0, 0.5, 12), (0.5, 0.5, 15), (1, 0.5, 19), (1.5, 1.5, 17)],
    'arp': [(i * 0.25, 0.25, (0, 7, 12, 15, 19, 15, 12, 7)[i % 8]) for i in range(12)],
    'chords': [(0, 1.5, x) for x in (0, 3, 7, 10)] + [(2, 1.5, x) for x in (-4, 0, 3, 7)],
    'pad': [(0, 3.0, x) for x in (0, 3, 7, 14)],
}
ROOT = {'bass': 33, 'lead': 60, 'arp': 60, 'chords': 57, 'pad': 57}


def audition(inst=None, role='lead', kit=None, voice=None, bpm=124):
    """A short WAV (bytes) of one sound: an instrument playing a little figure for its role, or one drum voice (kick /
    snare / clap / hats) from any kit hit a few times - so a sound can be heard before rendering a song."""
    import tempfile
    from .compose import TONE_DEFAULTS
    from .theory import Ev
    from .dsp import write_wav, SR
    from . import drumkits
    from .instruments import KITS
    song = dict(st={'kitparams': {}, 'tracks': []}, opts=Options(), bpm=bpm, total_bars=2, seed=1)
    out = np.zeros((2, int(SR * 4.2)))
    if voice:
        m = drumkits.MENU.get(kit) or (kit, '', '', kit, None, None)
        preset = m[3] if m[3] in KITS else '909'
        song['st']['kitparams'] = {d: dict(v) for d, v in KITS[preset].items()}
        if m[4] and not m[5]:
            song['st']['real_kit'] = m[4]
        r = Renderer(song, log=lambda *a: None)
        names = drumkits.VOICES.get(voice, (voice,))
        hits = {'kick': [0, 1, 2, 2.75], 'snare': [1, 3], 'clap': [1, 3], 'hats': [i * 0.5 for i in range(8)]}.get(voice, [0, 1, 2, 3])
        for i, b in enumerate(hits):
            nm = names[1] if voice == 'hats' and i == len(hits) - 1 and len(names) > 1 else names[0]
            ev = Ev(nm, b, 0.25, None, 0.95 if b == int(b) else 0.75)
            sig = r._real_drum(nm, ev, i) if song['st'].get('real_kit') else None
            if sig is None:
                sig = r._drum(nm, nm, var=i % 3)
            sig = np.asarray(sig, float)
            sig = sig if sig.ndim == 2 else np.vstack([sig, sig])
            s = int(b * 60 / bpm * SR)
            k = min(sig.shape[1], out.shape[1] - s)
            out[:, s:s + k] += sig[:, :k]
    else:
        role = role if role in AUDITION_FIG else 'lead'
        tcfg = dict(name='audition', inst=inst, layer=role, p=dict(TONE_DEFAULTS.get(inst, {})))
        r = Renderer(song, log=lambda *a: None)
        p = r._params(tcfg)
        for i, (b, d, iv) in enumerate(AUDITION_FIG[role]):
            ev = Ev('audition', b, d, ROOT[role] + iv, 0.85 if i % 2 == 0 else 0.72)
            sig = np.asarray(r._note(tcfg, ev, p), float)
            sig = sig if sig.ndim == 2 else np.vstack([sig, sig])
            s = int(b * 60 / bpm * SR)
            k = min(sig.shape[1], out.shape[1] - s)
            out[:, s:s + k] += sig[:, :k] * (0.6 if role in ('chords', 'pad') else 1.0)
    pk = float(np.max(np.abs(out))) or 1.0
    out = out / pk * 0.7
    nz = np.nonzero(np.max(np.abs(out), axis=0) > 1e-4)[0]
    out = out[:, :min(out.shape[1], (nz[-1] + int(0.05 * SR)) if len(nz) else out.shape[1])]
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        path = f.name
    try:
        write_wav(path, out)
        with open(path, 'rb') as fh:
            return fh.read()
    finally:
        os.remove(path)
