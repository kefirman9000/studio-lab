"""Real-instrument sample libraries: multi-sampled orchestra, percussion and acoustic drum kits.

All but one are CC0 (public domain) recordings by Versilian Studios and Karoryfer Samples; the Salamander concert grand is
CC-BY 3.0 by Alexander Holm (free for any use, credit him). Each is fetched straight from its GitHub repository
at a pinned commit. Every file is checked against the git SHA-1 listed in samplelibs.json before it's kept, and
only audio is stored (nothing runs). Songs made with them are entirely yours.

Libraries
  strings     violins, violas, celli and basses (sustain, spiccato, pizzicato, tremolo) + a solo violin
  winds       horn, trumpet, trombone, tuba, flute, oboe, clarinet, bassoon, piccolo (sustain + staccato), timpani
  percussion  congas, bongos, shakers, tambourine, real claps, cowbell, claves, guiro, woodblock, triangle ...
  drums       Virtuosity Drums - a real acoustic kit, close "studio" sound and a vintage "lofi" mic
  archtop     Karoryfer Shinyguitar (microphone) - the acoustic guitar
  twang       Karoryfer Black And Green Guitars - twangy hollowbody electric, sustained + staccato (country leads)
  grandpiano  Salamander Grand Piano V3 - a Yamaha C5 concert grand, 5 velocity layers (classical, film, jazz, ballads)

The player picks the recorded note nearest to the one asked for (re-pitching only a few semitones), a velocity layer
that matches how hard the note is played, a different round-robin take each time, and - for orchestral sounds - the
articulation a player would use: short notes are played spiccato / staccato instead of as a cut-off sustain.
"""
import hashlib
import io
import json
import os
import struct
import subprocess
from .proc import NOWIN
import sys
import threading
import urllib.parse
import urllib.request
import wave
import zlib

import numpy as np

from .dsp import SR
from . import updater

ROOT = updater.ROOT
REAL_DIR = os.path.join(ROOT, 'sound_library', 'real')
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samplelibs.json')
LIB_ORDER = ['drums', 'kit70s', 'kitbrush', 'kitrusty', 'kitunruly', 'snares', 'percussion', 'strings', 'winds', 'keys', 'grandpiano', 'colors',
             'archtop', 'twang', 'ebass', 'dbass']
LICENSES = {'CC0-1.0': 'CC0 (public domain)', 'CC-BY-3.0': 'CC-BY 3.0 (free for any use - credit the author)'}
KIT_LIBS = ('drums', 'kit70s', 'kitbrush', 'kitrusty', 'kitunruly')
BLURB = {
    'drums': 'A real acoustic drum kit (kick, snare, hats, ride, crash, toms) with 3 mic sounds: clean studio, big rock room and '
             'vintage lo-fi. Plays the rock, funk, disco, jazz and soul kits and the re-played breaks (jungle break, fast funk break, laid-back funk break ...).',
    'kit70s': 'A dry, warm 70s soul / funk drum kit (Karoryfer Gogodze Phu Vol II, recorded to sound like early-70s records): '
              'funk, Motown, soul jazz, neo-soul, blues, reggae, disco-funk.',
    'kitbrush': 'A real drum kit played with brushes (Karoryfer Swirly Drums): jazz, swing, bebop, bossa nova, soul ballads, '
                'quiet storm, country waltz and western swing.',
    'kitrusty': 'A big, raw vintage rock kit (Karoryfer Big Rusty Drums - an oversized 1980s kit with a 24" kick): rock, indie, '
                'punk and jam band.',
    'kitunruly': 'Two more real kits (Karoryfer Unruly Drums): a tight, punchy modern studio kit (pop, modern country) and a '
                 'dirty one with a saturated kick and trashy snare - pick them in the drum kit menu.',
    'snares': 'A collection of real snares (Karoryfer Frankensnare) that replace a kit\'s own: a crisp steel piccolo for drum & '
              'bass, an ash piccolo for jungle, a dead muffled 70s snare for soft rock and a huge one for 80s ballads.',
    'percussion': 'Real congas, bongos, shakers, tambourine, claps, cowbell, claves, guiro, woodblock, triangle - used in every genre that has them '
                  '(organic house, afro, latin, disco, pop ...).',
    'strings': 'A real string orchestra: violin, viola, cello and bass sections that play sustain, spiccato, pizzicato and tremolo, '
               'plus a solo violin. Replaces the General MIDI strings everywhere.',
    'winds': 'Real French horn, trumpet, trombone, tuba, flute, oboe, clarinet, bassoon and piccolo (sustain + staccato) and timpani, '
             'plus a harmon-muted trumpet (cool jazz, noir, lo-fi) and a muted horn.',
    'grandpiano': 'A big, open concert grand (Salamander Grand Piano V3, a Yamaha C5 recorded by Alexander Holm, 5 velocity '
                  'layers): classical, film and neoclassical piano, piano ballads, jazz trios, gospel and piano house. '
                  'License CC-BY 3.0 - songs are yours, just credit "Salamander Grand Piano by Alexander Holm".',
    'keys': 'A real Steinway grand piano (every genre that plays piano), a Yamaha upright for lo-fi / boom-bap / vintage styles, '
            'a Flemish harpsichord, a pipe organ for orchestral and baroque styles, and a Yamaha TX81Z FM piano.',
    'colors': 'Concert harp, marimba, vibraphone, xylophone, glockenspiel, tubular bells, kalimba, tenor sax (sustain + staccato), '
              'harmonica, ocarina and sleigh bells - recorded, used wherever a genre plays them.',
    'archtop': 'A real guitar (Karoryfer Shinyguitar, microphone recording): the strummed and picked acoustic guitar in country, '
               'folk, bluegrass and every genre that asks for an acoustic guitar.',
    'twang': 'A real twangy hollowbody electric (Karoryfer Black And Green Guitars, "twang" and staccato playing): the Telecaster-'
             'style country lead, chicken-pickin\' fills and slapback twang in classic, modern and outlaw country. Also plays every '
             'clean or distorted electric guitar part (funk, reggae, Motown, R&B, jazz, rock, metal ...) through an amp.',
    'ebass': 'A real electric bass (Karoryfer Growlybass, a Squier Jazz bass; sustained + staccato): rock, funk, disco, Motown, '
             'reggae, blues, pop, R&B, smooth jazz and every genre with an electric bass.',
    'dbass': 'A real upright double bass, played pizzicato (Karoryfer Meatbass): jazz, swing, bebop, country, bluegrass, boom bap '
             'and every genre with an upright bass.',
}
MAX_LEN = {'ring': 4.5, 'sus': 7.0, 'trem': 6.0, 'hit': 4.0, 'slap': 2.0, 'short': 2.0, 'pizz': 2.5}
_lock = threading.Lock()
_man = None
_idx = {}
_cache = {}


def manifest():
    global _man
    if _man is None:
        with open(MANIFEST) as f:
            _man = json.load(f)
    return _man


def _dir(lib):
    return os.path.join(REAL_DIR, lib)


def _local(lib, f):
    return os.path.join(_dir(lib), f['sha'] + '.wav')


def installed(lib):
    return os.path.isfile(os.path.join(_dir(lib), 'installed.json'))


def status():
    out = []
    for lib in LIB_ORDER:
        L = manifest()['libs'][lib]
        inst = installed(lib)
        missing = [f for f in L['files'] if not os.path.isfile(_local(lib, f))] if inst else []
        out.append(dict(id=lib, title=L['title'], by=L['by'], mb=round(L['bytes'] / 1e6), files=len(L['files']),
                        installed=inst, update_mb=round(sum(f['s'] for f in missing) / 1e6, 1) if len(missing) > 3 else 0,
                        blurb=BLURB[lib], license=LICENSES.get(L.get('license', 'CC0-1.0'), L.get('license')),
                        source=f"https://github.com/{L['repo']}"))
    return out


# ----------------------------------------------------------------------------- download + verify + convert
def git_blob_sha1(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def _fetch_http(repo, commit, path):
    url = f'https://raw.githubusercontent.com/{repo}/{commit}/' + urllib.parse.quote(path)
    req = urllib.request.Request(url, headers={'User-Agent': 'StudioLab'})
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:                                # flaky connection: try again
            last = e
    raise last


def _read_wav_any(data):
    """PCM 16/24/32-bit or float32 WAV (incl. WAVE_FORMAT_EXTENSIBLE) -> float32 (channels, n), rate."""
    if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise ValueError('not a WAV file')
    pos, fmt, raw = 12, None, None
    while pos + 8 <= len(data):
        cid, size = data[pos:pos + 4], struct.unpack('<I', data[pos + 4:pos + 8])[0]
        body = data[pos + 8:pos + 8 + size]
        if cid == b'fmt ':
            tag, ch, rate, _, _, bits = struct.unpack('<HHIIHH', body[:16])
            if tag == 0xFFFE and len(body) >= 26:
                tag = struct.unpack('<H', body[24:26])[0]
            fmt = (tag, ch, rate, bits)
        elif cid == b'data':
            raw = body
        pos += 8 + size + (size & 1)
    if not fmt or raw is None:
        raise ValueError('WAV without fmt/data')
    tag, ch, rate, bits = fmt
    if tag == 3 and bits == 32:
        x = np.frombuffer(raw[:len(raw) // 4 * 4], '<f4').astype(np.float32)
    elif tag == 1 and bits == 16:
        x = np.frombuffer(raw[:len(raw) // 2 * 2], '<i2').astype(np.float32) / 32768
    elif tag == 1 and bits == 24:
        b = np.frombuffer(raw[:len(raw) // 3 * 3], np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        v = np.where(v & 0x800000, v - 0x1000000, v)
        x = v.astype(np.float32) / 8388608
    elif tag == 1 and bits == 32:
        x = np.frombuffer(raw[:len(raw) // 4 * 4], '<i4').astype(np.float32) / 2147483648
    else:
        raise ValueError(f'unsupported WAV format {tag}/{bits}-bit')
    x = x[:len(x) // ch * ch].reshape(-1, ch).T
    return x, rate


def _flac_decoder(log):
    """A FLAC reader: pedalboard (if VST support is installed) or soundfile - installed on first use."""
    try:
        from pedalboard.io import AudioFile

        def dec(data):
            with AudioFile(io.BytesIO(data)) as f:
                return f.read(f.frames).astype(np.float32), int(f.samplerate)
        return dec
    except Exception:
        pass
    try:
        import soundfile as _sf  # noqa: F401
    except Exception:
        log('Installing the FLAC reader (soundfile) ...')
        cmd = [sys.executable, '-m', 'pip', 'install', '--user', 'soundfile']
        p = subprocess.run(cmd, capture_output=True, text=True, **NOWIN)
        if p.returncode != 0:
            raise RuntimeError('could not install soundfile: ' + (p.stderr or '')[-400:])
        import importlib
        import site
        importlib.invalidate_caches()
        try:
            sys.path.append(site.getusersitepackages())
        except Exception:
            pass
    import soundfile

    def dec(data):
        y, rate = soundfile.read(io.BytesIO(data), dtype='float32', always_2d=True)
        return y.T.copy(), int(rate)
    return dec


def _resample(x, rate):
    if rate == SR:
        return x
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(int(rate), SR)
    return resample_poly(x, SR // g, int(rate) // g, axis=1).astype(np.float32)


def _store(path, x, art):
    """Canonical form: stereo, 44.1 kHz, 16-bit, trimmed to the length a song can use, silence at the start removed."""
    if x.shape[0] == 1:
        x = np.vstack([x, x])
    x = x[:2]
    env = np.max(np.abs(x), axis=0)
    pk = float(env.max()) if env.size else 0.0
    if pk > 0:
        on = int(np.argmax(env > pk * 0.02))
        x = x[:, max(0, on - int(0.002 * SR)):]
    n = min(x.shape[1], int(MAX_LEN.get(art, 4.0) * SR))
    x = x[:, :n].copy()
    fade = min(n, int(0.08 * SR))
    if fade and n == int(MAX_LEN.get(art, 4.0) * SR):
        x[:, -fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    y = (np.clip(x, -1, 1) * 32767).astype('<i2').T.copy()
    tmp = path + '.part'
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())
    os.replace(tmp, path)


def install(lib, log=print, progress=None, fetch=None):
    """Download, verify and convert one library. Resumes where it stopped; files already in place are kept."""
    L = manifest()['libs'][lib]
    fetch = fetch or _fetch_http
    os.makedirs(_dir(lib), exist_ok=True)
    files = L['files']
    todo = [f for f in files if not os.path.isfile(_local(lib, f))]
    lic = LICENSES.get(L.get('license', 'CC0-1.0'), L.get('license'))
    log(f"{L['title']} - {len(files)} recordings, {L['bytes'] / 1e6:.0f} MB, {lic}, from github.com/{L['repo']}")
    if len(todo) < len(files):
        log(f'   {len(files) - len(todo)} already downloaded')
    dec = None
    done_bytes = sum(f['s'] for f in files if f not in todo)
    total = max(1, L['bytes'])
    from concurrent.futures import ThreadPoolExecutor
    bad = []

    def get(f):
        data = fetch(L['repo'], L['commit'], f['p'])
        if git_blob_sha1(data) != f['sha']:
            raise RuntimeError(f"checksum mismatch for {f['p']} - refusing it")
        return data
    with ThreadPoolExecutor(6) as ex:
        for f, data in zip(todo, ex.map(lambda f: _safe(get, f), todo)):
            if isinstance(data, Exception):
                bad.append((f['p'], str(data)))
                continue
            try:
                if f['p'].lower().endswith('.flac'):
                    dec = dec or _flac_decoder(log)
                    x, rate = dec(data)
                else:
                    x, rate = _read_wav_any(data)
                _store(_local(lib, f), _resample(x, rate), f['a'])
            except Exception as e:
                bad.append((f['p'], str(e)))
            done_bytes += f['s']
            if progress:
                progress(min(0.99, done_bytes / total))
    if bad:
        for p, e in bad[:5]:
            log(f'   ✗ {p}: {e}')
        if len(bad) > max(3, len(files) // 50):
            raise RuntimeError(f'{len(bad)} files failed - run the install again to retry them')
        log(f'   {len(bad)} files skipped (the rest of the library works)')
    with open(os.path.join(_dir(lib), 'installed.json'), 'w') as fh:
        json.dump(dict(commit=L['commit'], files=len(files) - len(bad), license=L.get('license', 'CC0-1.0'), source=L['repo']), fh)
    with _lock:
        _idx.pop(lib, None)
    log('   installed ✓')
    return True


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        return e


def remove(lib):
    import shutil
    shutil.rmtree(_dir(lib), ignore_errors=True)
    with _lock:
        _idx.pop(lib, None)


# ----------------------------------------------------------------------------- playback
def _index(lib):
    with _lock:
        if lib in _idx:
            return _idx[lib]
        out = {}
        if installed(lib):
            for f in manifest()['libs'][lib]['files']:
                if os.path.isfile(_local(lib, f)):
                    out.setdefault((f['i'], f['a']), []).append(f)
        _idx[lib] = out
        return out


def _load(lib, f):
    key = (lib, f['sha'])
    x = _cache.get(key)
    if x is None:
        with wave.open(_local(lib, f), 'rb') as w:
            raw = w.readframes(w.getnframes())
        x = np.frombuffer(raw, '<i2').astype(np.float32).reshape(-1, 2).T / 32768
        _cache[key] = x
    return x


def lib_of(inst):
    for lib in LIB_ORDER:
        if any(k[0] == inst for k in _index(lib)):
            return lib
    return None


def has(inst, art=None):
    for lib in LIB_ORDER:
        idx = _index(lib)
        if any(k[0] == inst and (art is None or k[1] == art) for k in idx):
            return True
    return False


def _layer(entries, vel):
    """Velocity layer (1..N) for a 0-1 velocity."""
    ds = sorted({e['v'] for e in entries})
    i = min(len(ds) - 1, int(max(0.0, min(0.999, vel)) * len(ds)))
    return ds[i]


def _pick(entries, vel, rr_key):
    v = _layer(entries, vel)
    cand = [e for e in entries if e['v'] == v] or entries
    cand = sorted(cand, key=lambda e: e.get('r', 1))
    k = int(rr_key) if str(rr_key).isdigit() else zlib.crc32(str(rr_key).encode())
    return cand[k % len(cand)]


def hit(inst, vel=0.8, rr_key='0'):
    """One-shot (drums / percussion): mono float32, peak 1."""
    for lib in LIB_ORDER:
        es = _index(lib).get((inst, 'hit')) or _index(lib).get((inst, 'slap'))
        if es:
            f = _pick(es, vel, rr_key)
            x = _load(lib, f).mean(axis=0)
            pk = float(np.max(np.abs(x)))
            return (x / pk).astype(np.float32) if pk > 1e-5 else None
    return None


def _repitch(x, semis):
    if abs(semis) < 1e-3:
        return x
    r = 2 ** (semis / 12.0)
    n = x.shape[1]
    idx = np.arange(0, n - 1, r)
    i0 = idx.astype(np.int64)
    fr = (idx - i0).astype(np.float32)
    return x[:, i0] * (1 - fr) + x[:, i0 + 1] * fr


def note(inst, art, midi, dur, vel=0.8, rr_key='0', release=0.25):
    """A pitched note: nearest recorded pitch in the velocity layer, re-pitched, cut to the note length with a release."""
    for lib in LIB_ORDER:
        es = _index(lib).get((inst, art))
        if not es:
            continue
        pitched = [e for e in es if e.get('n') is not None]
        if not pitched:
            return None
        best = min(abs(e['n'] - midi) for e in pitched)
        near = [e for e in pitched if abs(e['n'] - midi) == best]
        f = _pick(near, vel, rr_key)
        x = _repitch(_load(lib, f), midi - f['n'])
        if art == 'ring':                                    # plucked / struck: let it ring, damp after a while
            n = min(x.shape[1], int(max(dur + 1.2, 1.4) * SR))
            x = x[:, :n].copy()
            rl = min(n, int(0.12 * SR))
            x[:, -rl:] *= np.linspace(1, 0, rl, dtype=np.float32)
            return x.astype(np.float32)
        if art in ('sus', 'trem'):
            n = min(x.shape[1], int((dur + release) * SR))
            x = x[:, :n].copy()
            rl = min(n, int(release * SR))
            if rl:
                x[:, -rl:] *= np.linspace(1, 0, rl, dtype=np.float32) ** 1.5
        else:                                               # shorts ring out naturally, a little damped on long gaps
            n = min(x.shape[1], int(max(dur * 1.6, 0.25) * SR))
            x = x[:, :n].copy()
            rl = min(n, int(0.06 * SR))
            x[:, -rl:] *= np.linspace(1, 0, rl, dtype=np.float32)
        return x.astype(np.float32)
    return None


# app instrument -> how the real library plays it: (kind, spec)
#   section: register-split string section;  brass: register-split brass section;  solo: one instrument
SECTION = [(55, 'violins'), (48, 'violas'), (36, 'celli'), (0, 'basses')]
BRASS = [(60, 'trumpet'), (53, 'horn'), (41, 'trombone'), (0, 'tuba')]
ORCH = {
    'strings': ('section', 'sus'), 'slowstrings': ('section', 'sus'), 'spiccato': ('section', 'short'),
    'pizz': ('section', 'pizz'), 'tremolo': ('section', 'trem'),
    'violins': ('solo', 'violins'), 'violin': ('solo', 'violin'), 'fiddle': ('solo', 'violin'), 'viola': ('solo', 'violas'), 'violas': ('solo', 'violas'), 'cello': ('solo', 'celli'),
    'contrabass': ('solo', 'basses'),
    'brass': ('brass', 'sus'), 'trumpetsection': ('brass', 'sus'), 'horn': ('solo', 'horn'), 'trumpet': ('solo', 'trumpet'),
    'trombone': ('solo', 'trombone'), 'tuba': ('solo', 'tuba'), 'flute': ('solo', 'flute'), 'oboe': ('solo', 'oboe'),
    'clarinet': ('solo', 'clarinet'), 'bassoon': ('solo', 'bassoon'), 'piccolo': ('solo', 'piccolo'),
    # keys & colours
    'piano': ('solo', 'grand'), 'concertgrand': ('solo', 'salgrand'), 'upright_piano': ('solo', 'upright_piano'),
    'mutedtrumpet': ('solo', 'mutetrumpet'), 'mutehorn': ('solo', 'mutehorn'), 'harpsichord': ('solo', 'harpsichord'),
    'pipeorgan': ('solo', 'pipeorgan'), 'fmpiano': ('solo', 'fmpiano'),
    'harp': ('ring', 'harp'), 'marimba': ('ring', 'marimba'), 'vibes': ('ring', 'vibes'), 'xylophone': ('ring', 'xylophone'),
    'glock': ('ring', 'glock'), 'tubular': ('ring', 'tubular'), 'kalimba': ('ring', 'kalimba'),
    'sax': ('solo', 'sax'), 'tenorsax': ('solo', 'sax'), 'harmonica': ('solo', 'harmonica'), 'sopsax': ('solo', 'sax'), 'ebass': ('solo', 'ebass'), 'fingerbass': ('solo', 'ebass'),
    'pickbass': ('solo', 'ebass'), 'upright': ('solo', 'dbass'), 'acbass': ('solo', 'dbass'), 'guitar': ('solo', 'twang'),
    'mutedgtr': ('solo', 'twang'), 'cleanguitar': ('solo', 'twang'), 'acguitar': ('ring', 'acguitar'), 'twang': ('solo', 'twang'), 'ocarina': ('solo', 'ocarina'),
}
# styles whose piano is a worn upright rather than a concert grand
UPRIGHT_STYLES = {'piano_miniature', 'lofi', 'boombap', 'hauntology', 'vaporwave', 'memphis_phonk', 'blues', 'soul_ballad', 'folk', 'western', 'motown'}
# styles whose piano is the big Salamander concert grand (when installed) rather than the Steinway B
CONCERT_GRAND_STYLES = {'film_piano', 'neoclassical', 'romantic', 'classical_period', 'cinematic', 'cinematic_journey', 'cinematic_journey_low',
                        'storybook_score', 'festive_cinematic', 'minimalism', 'piano_house_90s', 'gospel', 'modern_gospel', 'jazz', 'modal_jazz',
                        'bebop', 'soul_jazz', 'smooth_jazz', 'neo_soul', 'ambient', 'celtic_new_age', 'chamber_pop', 'emotive_deep_house'}
# styles whose trumpet plays with a harmon mute
MUTE_TRUMPET_STYLES = {'jazz', 'modal_jazz', 'jazz_hop', 'jazz_rap', 'lofi', 'trip_hop', 'smooth_jazz', 'electro_swing', 'ethio_jazz',
                       'soul_jazz', 'neo_soul'}
PIPE_ORGAN_STYLES = {'christmas_carol_choir', 'baroque_organ', 'epic_choir', 'baroque', 'cinematic', 'tension', 'hybrid_trailer', 'symphonic_metal', 'adventure', 'romantic'}
SHORT_NOTE = 0.24          # seconds: notes this short are played with the short articulation (spiccato / staccato)


def plays(name):
    """Can the installed libraries play this app instrument?"""
    spec = ORCH.get(name)
    if not spec:
        return False
    kind, what = spec
    if kind == 'section':
        return has('violins', what) and has('celli', what)
    if kind == 'brass':
        return has('trumpet', 'sus') and has('trombone', 'sus')
    if kind == 'ring':
        return has(what, 'ring')
    return has(what, 'sus')


def orch_note(name, midi, dur, vel, rr_key):
    kind, what = ORCH[name]
    if kind in ('section', 'brass'):
        table = SECTION if kind == 'section' else BRASS
        art = what if kind == 'section' else 'sus'
        order = [i for lo, i in table if midi >= lo] + [i for lo, i in reversed(table) if midi < lo]
        inst = next((i for i in order if has(i, art)), order[0])        # the section for this register, else the nearest one
    elif kind == 'ring':
        inst, art = what, 'ring'
    else:
        inst, art = what, 'sus'
    if art == 'sus' and dur < SHORT_NOTE and has(inst, 'short'):
        art = 'short'
    x = note(inst, art, midi, dur, vel, rr_key, release=0.35 if inst in ('violins', 'violas', 'celli', 'basses') else 0.22)
    if x is None and art != 'sus':
        x = note(inst, 'sus', midi, dur, vel, rr_key)
    if x is not None and kind == 'section' and art in ('sus', 'trem') and inst in ('violins', 'violas'):
        # sections double the line below: celli / violas an octave down give the real ensemble weight
        lower = next((i for lo, i in table if lo <= midi - 12), None)
        if lower and lower != inst and midi - 12 >= 36:
            y = note(lower, art, midi - 12, dur, vel * 0.8, rr_key + 'lo', release=0.35)
            if y is not None:
                m = min(x.shape[1], y.shape[1])
                x = x.copy()
                x[:, :m] += 0.35 * y[:, :m]
    return x


# which real drum kit plays a style's drums
LOFI_KIT_STYLES = {'lofi', 'boombap', 'hauntology', 'vaporwave', 'soul_ballad', 'jazzhop'}
PERC = {'orchcrash': 'orchcrash', 'timp': 'timpani', 'sleigh': 'sleigh', 'claves': 'claves', 'bongo': 'bongo', 'guiro': 'guiro', 'conga': 'conga', 'shaker': 'shaker', 'tamb': 'tamb', 'cowbell': 'cowbell', 'claves': 'claves', 'guiro': 'guiro',
        'woodblock': 'woodblock', 'triangle': 'triangle', 'cabasa': 'cabasa', 'bongo': 'bongo', 'agogo': 'agogo'}
KIT_PARTS = {'kick': 'kick', 'snare': 'snare', 'rim': 'rim', 'chat': 'chat', 'ohat': 'ohat', 'ride': 'ride', 'crash': 'crash',
             'tom': 'tom', 'clap': 'clap', 'cymbal': 'crash'}


# the individual instruments you can pick in the Sound dropdowns: (id, label, library, parts it suits)
CHOICES = [
    ('violins', 'Violins (section)', 'strings', ('lead', 'chords', 'pad', 'arp')),
    ('violin', 'Solo violin', 'strings', ('lead', 'arp')),
    ('viola', 'Violas (section)', 'strings', ('lead', 'chords', 'pad', 'arp')),
    ('cello', 'Cellos (section)', 'strings', ('lead', 'bass', 'chords', 'pad')),
    ('contrabass', 'Double basses', 'strings', ('bass',)),
    ('strings', 'String section - sustain', 'strings', ('chords', 'pad', 'lead', 'bass')),
    ('spiccato', 'String section - spiccato', 'strings', ('chords', 'arp', 'bass', 'lead')),
    ('pizz', 'String section - pizzicato', 'strings', ('arp', 'chords', 'bass', 'lead')),
    ('tremolo', 'String section - tremolo', 'strings', ('pad', 'chords')),
    ('horn', 'French horn', 'winds', ('lead', 'pad', 'chords')),
    ('trumpet', 'Trumpet', 'winds', ('lead',)),
    ('mutedtrumpet', 'Muted trumpet (harmon)', 'winds', ('lead',)),
    ('mutehorn', 'Muted French horn', 'winds', ('lead', 'pad', 'chords')),
    ('trombone', 'Trombone', 'winds', ('lead', 'bass', 'chords')),
    ('tuba', 'Tuba', 'winds', ('bass',)),
    ('brass', 'Brass section', 'winds', ('lead', 'chords', 'pad')),
    ('flute', 'Flute', 'winds', ('lead', 'arp')),
    ('piccolo', 'Piccolo', 'winds', ('lead', 'arp')),
    ('oboe', 'Oboe', 'winds', ('lead',)),
    ('clarinet', 'Clarinet', 'winds', ('lead', 'arp', 'chords')),
    ('bassoon', 'Bassoon', 'winds', ('bass', 'lead')),
    ('piano', 'Grand piano (Steinway)', 'keys', ('chords', 'lead', 'arp', 'pad', 'bass')),
    ('concertgrand', 'Concert grand piano (Salamander)', 'grandpiano', ('chords', 'lead', 'arp', 'pad', 'bass')),
    ('upright_piano', 'Upright piano', 'keys', ('chords', 'lead', 'arp')),
    ('harpsichord', 'Harpsichord', 'keys', ('chords', 'arp', 'lead')),
    ('pipeorgan', 'Pipe organ', 'keys', ('chords', 'pad', 'lead')),
    ('fmpiano', 'FM piano (TX81Z)', 'keys', ('chords', 'arp', 'lead')),
    ('harp', 'Concert harp', 'colors', ('arp', 'chords', 'lead')),
    ('marimba', 'Marimba', 'colors', ('arp', 'lead', 'chords')),
    ('vibes', 'Vibraphone', 'colors', ('arp', 'lead', 'chords')),
    ('xylophone', 'Xylophone', 'colors', ('arp', 'lead')),
    ('glock', 'Glockenspiel', 'colors', ('arp', 'lead')),
    ('tubular', 'Tubular bells', 'colors', ('lead', 'arp')),
    ('kalimba', 'Kalimba', 'colors', ('arp', 'lead')),
    ('sax', 'Tenor sax', 'colors', ('lead',)),
    ('harmonica', 'Harmonica', 'colors', ('lead',)),
    ('sopsax', 'Soprano sax (high sax)', 'colors', ('lead',)),
    ('acguitar', 'Acoustic guitar', 'archtop', ('chords', 'arp', 'lead', 'bass')),
    ('twang', 'Twang electric guitar', 'twang', ('lead', 'arp', 'chords')),
    ('ebass', 'Electric bass', 'ebass', ('bass',)),
    ('upright', 'Upright double bass', 'dbass', ('bass',)),
    ('ocarina', 'Ocarina', 'colors', ('lead',)),
]


def choices(role=None):
    """Installed real-orchestra instruments as dropdown entries (all of them, or the ones that suit one part)."""
    out = []
    for iid, label, lib, roles in CHOICES:
        if installed(lib) and (role is None or role in roles) and plays(iid):
            out.append(dict(id='real:' + iid, name=label + ' (real)', group='Real orchestra (no setup)'))
    return out
