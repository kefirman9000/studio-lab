"""Sampled instruments: a small SoundFont (.sf2) player written in numpy.

Studio Lab can download the free GeneralUser GS bank (real recorded strings, brass, woodwinds, pianos,
guitars, acoustic drum kits ...). When it is installed, orchestral / acoustic parts are played from
those recordings instead of synthesised approximations.
"""
import os
import struct
import threading
import urllib.request

import numpy as np
from scipy import signal

from .dsp import SR
from . import updater

ROOT = updater.ROOT
LIB_DIR = os.path.join(ROOT, 'sound_library')
GUGS_FILE = 'GeneralUser-GS.sf2'
# The author asks people not to hot-link his website; this GitHub repo is his official copy for automated packaging.
GUGS_URL = 'https://github.com/mrbumpy409/GeneralUser-GS/raw/main/GeneralUser-GS.sf2'
GUGS_SIZE = 32319396


# ----------------------------------------------------------------------------- library management
def library_path():
    """Best .sf2 to use: GeneralUser GS if present, else the largest .sf2 the user dropped in."""
    if not os.path.isdir(LIB_DIR):
        return None
    p = os.path.join(LIB_DIR, GUGS_FILE)
    if os.path.isfile(p) and os.path.getsize(p) > 1_000_000:
        return p
    sf = [os.path.join(LIB_DIR, f) for f in os.listdir(LIB_DIR) if f.lower().endswith('.sf2')]
    sf = [f for f in sf if os.path.getsize(f) > 100_000]
    return max(sf, key=os.path.getsize) if sf else None


def installed():
    return library_path() is not None


def download(log=print, progress=None):
    os.makedirs(LIB_DIR, exist_ok=True)
    dst = os.path.join(LIB_DIR, GUGS_FILE)
    tmp = dst + '.part'
    log('Downloading GeneralUser GS (free sampled instruments, ~31 MB) ...')
    req = urllib.request.Request(GUGS_URL, headers={'User-Agent': 'StudioLab'})
    with urllib.request.urlopen(req, timeout=60) as r, open(tmp, 'wb') as f:
        total = int(r.headers.get('Content-Length') or GUGS_SIZE)
        got = 0
        while True:
            b = r.read(1 << 16)
            if not b:
                break
            f.write(b)
            got += len(b)
            if progress:
                progress(min(0.99, got / total))
    with open(tmp, 'rb') as f:
        h = f.read(12)
    if h[:4] != b'RIFF' or h[8:12] != b'sfbk':
        if True:
            os.remove(tmp)
            raise RuntimeError('downloaded file is not a SoundFont')
    os.replace(tmp, dst)
    global _BANK
    _BANK = None
    log('Sound library installed.')
    return dst


# ----------------------------------------------------------------------------- SF2 parsing
GEN_DEFAULTS = {8: 13500, 21: -12000, 22: 0, 25: -12000, 26: -12000, 27: -12000, 28: -12000, 30: -12000,
                33: -12000, 34: -12000, 35: -12000, 36: -12000, 38: -12000, 56: 100, 58: -1, 43: (0, 127), 44: (0, 127)}
RANGE_GENS = (43, 44)
ADDR_GENS = (0, 1, 2, 3, 4, 12, 45, 50)


class Bank:
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            data = f.read()
        if data[:4] != b'RIFF' or data[8:12] != b'sfbk':
            raise ValueError('not a SoundFont 2 file')
        chunks = {}
        pos = 12
        while pos < len(data) - 8:
            cid, size = data[pos:pos + 4], struct.unpack('<I', data[pos + 4:pos + 8])[0]
            if cid == b'LIST':
                kind = data[pos + 8:pos + 12]
                p2, end = pos + 12, pos + 8 + size
                while p2 < end - 8:
                    sid, ssz = data[p2:p2 + 4], struct.unpack('<I', data[p2 + 4:p2 + 8])[0]
                    chunks[(kind, sid)] = (p2 + 8, ssz)
                    p2 += 8 + ssz + (ssz & 1)
            pos += 8 + size + (size & 1)
        so, ssz = chunks[(b'sdta', b'smpl')]
        self.smpl = np.memmap(path, dtype='<i2', mode='r', offset=so, shape=(ssz // 2,))

        def recs(name, fmt):
            o, s = chunks[(b'pdta', name)]
            n = struct.calcsize(fmt)
            return [struct.unpack(fmt, data[o + i * n:o + (i + 1) * n]) for i in range(s // n)]

        self.phdr = recs(b'phdr', '<20sHHHIII')
        self.pbag = recs(b'pbag', '<HH')
        self.pgen = recs(b'pgen', '<HH')
        self.inst = recs(b'inst', '<20sH')
        self.ibag = recs(b'ibag', '<HH')
        self.igen = recs(b'igen', '<HH')
        self.shdr = recs(b'shdr', '<20sIIIIIBbHH')
        self.presets = {}
        for i, h in enumerate(self.phdr[:-1]):
            self.presets[(h[2], h[1])] = i          # (bank, program) -> index
        self._zones = {}
        self._norm = {}
        self.lock = threading.Lock()

    @staticmethod
    def _gens(gen_list, a, b):
        g = {}
        for op, amt in gen_list[a:b]:
            if op in RANGE_GENS:
                g[op] = (amt & 0xFF, amt >> 8)
            else:
                g[op] = amt - 65536 if amt >= 32768 else amt
        return g

    def _zones_of(self, bags, gens, a, b, link):
        """Split a preset/instrument's bags into (global, [zones])."""
        glob, zones = {}, []
        for k in range(a, b):
            g = self._gens(gens, bags[k][0], bags[k + 1][0])
            if link not in g:
                if k == a:
                    glob = g
                continue
            zones.append(g)
        return glob, zones

    def zones(self, bank, prog):
        """Flatten preset -> instrument -> sample into a list of playable zone dicts."""
        key = (bank, prog)
        if key in self._zones:
            return self._zones[key]
        idx = self.presets.get(key)
        if idx is None:
            idx = self.presets.get((0, prog)) if bank != 128 else self.presets.get((128, 0))
        if idx is None:
            self._zones[key] = []
            return []
        pg_glob, pzones = self._zones_of(self.pbag, self.pgen, self.phdr[idx][3], self.phdr[idx + 1][3], 41)
        out = []
        for pz in pzones:
            pz = {**pg_glob, **pz}
            ii = pz[41]
            ig_glob, izones = self._zones_of(self.ibag, self.igen, self.inst[ii][1], self.inst[ii + 1][1], 53)
            for iz in izones:
                g = dict(GEN_DEFAULTS)
                g.update(ig_glob)
                g.update(iz)
                for op, v in pz.items():                    # preset generators are offsets (ranges intersect)
                    if op in (41, 53) or op in ADDR_GENS or op in (54, 57, 58, 46, 47):
                        continue
                    if op in RANGE_GENS:
                        lo, hi = g[op]
                        g[op] = (max(lo, v[0]), min(hi, v[1]))
                    else:
                        g[op] = g.get(op, GEN_DEFAULTS.get(op, 0)) + v
                if g[43][0] > g[43][1] or g[44][0] > g[44][1]:
                    continue
                s = self.shdr[g[53]]
                g['_s'] = s
                out.append(g)
        self._zones[key] = out
        return out


_BANK = None
_BANK_LOCK = threading.Lock()


def bank():
    global _BANK
    with _BANK_LOCK:
        if _BANK is None:
            p = library_path()
            if not p:
                return None
            _BANK = Bank(p)
        return _BANK


# ----------------------------------------------------------------------------- voice rendering
def _tc(v):
    return float(2.0 ** (max(-12000, min(8000, v)) / 1200.0))


def _env_db(n, n_on, g, key, hold_gen=35, decay_gen=36, sust_gen=37, rel_gen=38, delay_gen=33, att_gen=34,
            k_hold=39, k_dec=40, vol=True):
    """Envelope (linear amplitude for vol env, 0..1 for mod env)."""
    dl = _tc(g.get(delay_gen, -12000))
    at = _tc(g.get(att_gen, -12000))
    ho = _tc(g.get(hold_gen, -12000) + g.get(k_hold, 0) * (60 - key))
    de = _tc(g.get(decay_gen, -12000) + g.get(k_dec, 0) * (60 - key))
    re = min(_tc(g.get(rel_gen, -12000)), 8.0)
    if vol:
        sus_db = -max(0, min(1440, g.get(sust_gen, 0))) / 10.0       # cB attenuation -> dB
    else:
        sus_db = 1.0 - max(0, min(1000, g.get(sust_gen, 0))) / 1000.0  # 0.1% units -> level
    t = np.arange(n) / SR
    on_t = n_on / SR
    if vol:
        lvl = np.zeros(n)
        a0, a1, a2 = dl, dl + at, dl + at + ho
        m = (t >= a0) & (t < a1)
        lvl[m] = (t[m] - a0) / max(at, 1e-4)
        db = np.zeros(n)
        md = t >= a2
        db[md] = np.maximum(sus_db, -100.0 * (t[md] - a2) / max(de, 1e-4))
        lvl[t >= a1] = 10 ** (db[t >= a1] / 20)
        # release: drops 100 dB over the release time from wherever it was
        if n_on < n:
            l_on = lvl[min(n_on, n - 1)] if n_on < n else 0
            tr = t[n_on:] - on_t
            lvl[n_on:] = l_on * 10 ** (-100.0 * tr / max(re, 1e-3) / 20)
        return lvl
    lvl = np.zeros(n)
    a0, a1, a2 = dl, dl + at, dl + at + ho
    m = (t >= a0) & (t < a1)
    lvl[m] = (t[m] - a0) / max(at, 1e-4)
    lvl[(t >= a1) & (t < a2)] = 1.0
    md = t >= a2
    lvl[md] = np.maximum(sus_db, 1.0 - (t[md] - a2) / max(de, 1e-4))
    if n_on < n:
        l_on = lvl[min(n_on, n - 1)]
        tr = t[n_on:] - on_t
        lvl[n_on:] = np.maximum(0, l_on * (1 - tr / max(re, 1e-3)))
    return lvl


def _voice(bk, g, key, vel, dur, max_tail=3.0):
    s = g['_s']
    _, start, end, ls, le, srate, orig, corr, _, stype = s
    if stype & 0x8000 or srate <= 0:          # ROM sample - unsupported
        return None, 0.0
    start += g.get(0, 0) + 32768 * g.get(4, 0)
    end += g.get(1, 0) + 32768 * g.get(12, 0)
    ls += g.get(2, 0) + 32768 * g.get(45, 0)
    le += g.get(3, 0) + 32768 * g.get(50, 0)
    root = g.get(58, -1)
    root = orig if root < 0 else root
    if root > 127:
        root = 60
    keyn = g.get(46, -1)
    k = key if keyn < 0 else keyn
    cents = (k - root) * g.get(56, 100) + g.get(51, 0) * 100 + g.get(52, 0) + corr
    ratio = 2 ** (cents / 1200.0) * srate / SR
    mode = g.get(54, 0) & 3
    loop = mode in (1, 3) and le > ls + 8 and le <= end
    rel = min(_tc(g.get(38, -12000)), max_tail)
    n_on = int(dur * SR)
    n = n_on + int(rel * SR) + 64
    if not loop:
        n = min(n, int((end - start - 2) / ratio))
    if n <= 16:
        return None, 0.0
    pos = start + ratio * np.arange(n)
    if loop:
        span = le - ls
        over = pos >= le
        pos[over] = ls + np.mod(pos[over] - ls, span)
    i0 = np.floor(pos).astype(np.int64)
    fr = (pos - i0).astype(np.float32)
    i1 = i0 + 1
    if loop:
        i1[i1 >= le] -= (le - ls)
    i0 = np.clip(i0, 0, len(bk.smpl) - 1)
    i1 = np.clip(i1, 0, len(bk.smpl) - 1)
    lo, hi = int(min(i0.min(), i1.min())), int(max(i0.max(), i1.max())) + 1
    seg = np.asarray(bk.smpl[lo:hi], dtype=np.float32) / 32768.0
    y = seg[i0 - lo] * (1 - fr) + seg[i1 - lo] * fr
    # pitch from mod env (rare, skipped) ; volume envelope
    y *= _env_db(n, n_on, g, k).astype(np.float32)
    # filter: initial cutoff + velocity (SF2 default modulator) + mod-env sweep
    fc = g.get(8, 13500) - 2400 * (1 - vel / 127.0)
    menv_amt = g.get(11, 0)
    q_db = max(0, g.get(9, 0)) / 10.0
    if menv_amt:
        menv = _env_db(n, n_on, g, k, 27, 28, 29, 30, 25, 26, 31, 32, vol=False)
        fc_t = 8.176 * 2 ** ((fc + menv_amt * menv) / 1200.0)
        if np.min(fc_t) < 16000:
            from .dsp import svf_sweep
            y = svf_sweep(y, np.clip(fc_t, 30, 18000), q=0.707 * 10 ** (q_db / 20), block=128).astype(np.float32)
    else:
        f = 8.176 * 2 ** (fc / 1200.0)
        if f < 16000:
            b, a = signal.butter(2, max(30, f) / (SR / 2))
            y = signal.lfilter(b, a, y).astype(np.float32)
    att_db = -(0.4 * g.get(48, 0)) / 10.0       # FluidSynth-style EMU attenuation scaling
    y *= 10 ** (att_db / 20)
    pan = max(-500, min(500, g.get(17, 0))) / 500.0
    return y, pan


def render_note(bk, bnk, prog, key, vel, dur, max_tail=3.0):
    """Stereo (2, n) float32 for one note."""
    zs = [g for g in bk.zones(bnk, prog) if g[43][0] <= key <= g[43][1] and g[44][0] <= vel <= g[44][1]]
    if not zs:
        zs = [g for g in bk.zones(bnk, prog) if g[43][0] <= key <= g[43][1]][:2]
    parts = []
    for g in zs:
        y, pan = _voice(bk, g, key, vel, dur, max_tail)
        if y is not None:
            parts.append((y, pan))
    if not parts:
        return np.zeros((2, 64), np.float32)
    n = max(len(y) for y, _ in parts)
    out = np.zeros((2, n), np.float32)
    for y, pan in parts:
        a = (pan + 1) * np.pi / 4
        out[0, :len(y)] += y * np.cos(a)
        out[1, :len(y)] += y * np.sin(a)
    return out


def norm_gain(bk, bnk, prog, key=60):
    """Make every preset sit at a similar loudness so the mixer's levels still make sense."""
    k = (bnk, prog, key)
    if k not in bk._norm:
        x = render_note(bk, bnk, prog, key, 100, 1.0, max_tail=0.5)
        rms = float(np.sqrt(np.mean(x[:, :int(0.8 * SR)] ** 2) + 1e-12))
        bk._norm[k] = float(min(40.0, 0.18 / max(rms, 1e-5)))
    return bk._norm[k]


# ----------------------------------------------------------------------------- Studio Lab instruments
# name -> (bank, program, display name, release tail seconds)
SAMPLED = {
    'piano': (0, 0, 'Grand piano', 2.5), 'epiano': (0, 4, 'Electric piano', 1.5), 'clav': (0, 7, 'Clavinet', 0.4),
    'celesta': (0, 8, 'Celesta', 2.0), 'bell': (0, 14, 'Tubular bells', 3.0), 'marimba': (0, 12, 'Marimba', 1.0),
    'organ': (0, 16, 'Drawbar organ', 0.4), 'guitar': (0, 25, 'Steel guitar', 1.5), 'nylon': (0, 24, 'Nylon guitar', 1.5),
    'violin': (0, 40, 'Violin', 0.8), 'viola': (0, 41, 'Viola', 0.8), 'cello': (0, 42, 'Cello', 0.8),
    'contrabass': (0, 43, 'Contrabass', 0.8), 'tremolo': (0, 44, 'Tremolo strings', 0.8),
    'pizz': (0, 45, 'Pizzicato strings', 0.8), 'harp': (0, 46, 'Orchestral harp', 2.0), 'timpani': (0, 47, 'Timpani', 2.0),
    'strings': (0, 48, 'String ensemble', 1.0), 'slowstrings': (0, 49, 'Slow strings', 1.2),
    'choir': (0, 52, 'Choir aahs', 1.2), 'trumpet': (0, 56, 'Trumpet', 0.5), 'trombone': (0, 57, 'Trombone', 0.5),
    'tuba': (0, 58, 'Tuba', 0.5), 'horn': (0, 60, 'French horns', 0.7), 'brass': (0, 61, 'Brass section', 0.5),
    'sax': (0, 65, 'Alto sax', 0.4), 'sopranosax': (0, 64, 'Soprano sax', 0.4), 'oboe': (0, 68, 'Oboe', 0.4), 'bassoon': (0, 70, 'Bassoon', 0.4),
    'clarinet': (0, 71, 'Clarinet', 0.4), 'piccolo': (0, 72, 'Piccolo', 0.4), 'flute': (0, 73, 'Flute', 0.5),
    'acbass': (0, 32, 'Acoustic bass', 0.5), 'fingerbass': (0, 33, 'Finger bass', 0.4), 'kalimba': (0, 108, 'Kalimba', 1.0),
    'steeldrum': (0, 114, 'Steel drums', 1.0), 'taikodrum': (0, 116, 'Taiko', 1.5),
    'cleanguitar': (0, 27, 'Clean electric guitar', 1.0), 'muted': (0, 28, 'Muted guitar', 0.3),
    'odguitar': (0, 29, 'Overdriven guitar', 0.6), 'distguitar': (0, 30, 'Distortion guitar', 0.6),
    'pickbass': (0, 34, 'Picked bass', 0.4), 'slapbass': (0, 36, 'Slap bass', 0.4),
    'mutedtrumpet': (0, 59, 'Muted trumpet', 0.4), 'tenorsax': (0, 66, 'Tenor sax', 0.4),
    'harpsichord': (0, 6, 'Harpsichord', 1.0), 'spiccato': (0, 48, 'Staccato strings', 0.25),
    'accordion': (0, 21, 'Accordion', 0.4), 'bandoneon': (0, 23, 'Bandoneon', 0.4), 'banjo': (0, 105, 'Banjo', 1.0),
    'steelguitar': (0, 25, 'Steel-string guitar', 1.0), 'fiddle': (0, 110, 'Fiddle', 0.3), 'trumpetsection': (0, 61, 'Brass section', 0.4),
    'upright': (0, 32, 'Acoustic bass', 0.5), 'mutedgtr': (0, 28, 'Muted guitar', 0.3), 'vibes': (0, 11, 'Vibraphone', 1.5),
    'harmonica': (0, 22, 'Harmonica', 0.3),
    # v1.54: South / East Asian instruments the General MIDI bank has as real recordings
    'sitar': (0, 104, 'Sitar', 2.0), 'harmonium': (0, 20, 'Reed organ / harmonium', 0.4),
    'santoor': (0, 15, 'Hammered dulcimer / santoor', 2.5), 'koto': (0, 107, 'Koto', 1.2),
    'shehnai': (0, 111, 'Shehnai', 0.4), 'shamisen': (0, 106, 'Shamisen', 0.6), 'shakuhachi': (0, 77, 'Shakuhachi', 0.5),
}
# Extra realistic instruments that only exist as samples (shown in the instrument lists when the library is installed)
SAMPLED_ONLY = ['shehnai', 'shamisen', 'nylon', 'cleanguitar', 'muted', 'odguitar', 'distguitar', 'acbass', 'fingerbass', 'pickbass', 'slapbass',
                'viola', 'contrabass', 'slowstrings', 'trumpet', 'mutedtrumpet', 'trombone', 'tuba',
                'bassoon', 'piccolo', 'tenorsax']
# built-in synth stand-ins for when the library is missing (or a sample can't be played)
FALLBACK = {'nylon': 'acguitar', 'cleanguitar': 'guitar', 'muted': 'mutedgtr', 'odguitar': 'guitar', 'distguitar': 'guitar',
            'acbass': 'upright', 'fingerbass': 'ebass', 'pickbass': 'ebass', 'slapbass': 'fmbass', 'viola': 'violin',
            'contrabass': 'cello', 'slowstrings': 'strings', 'bandoneon': 'accordion', 'steelguitar': 'guitar', 'fiddle': 'violin', 'trumpetsection': 'brass',
            'mutedtrumpet': 'trumpet', 'trombone': 'horn', 'tuba': 'horn', 'bassoon': 'clarinet', 'piccolo': 'flute', 'tenorsax': 'sax', 'sopranosax': 'sax', 'taikodrum': 'timpani',
            'shehnai': 'oboe', 'shamisen': 'koto', 'concertgrand': 'piano', 'upright_piano': 'piano', 'mutehorn': 'horn'}
# electronic genres only swap instruments that are obviously acoustic
ELECTRONIC_SWAP = {'piano', 'epiano', 'guitar', 'violin', 'harp', 'flute', 'sax', 'marimba', 'kalimba', 'steeldrum',
                   'celesta', 'pizz', 'clav', 'cello', 'harpsichord', 'oboe', 'clarinet', 'spiccato', 'tremolo',
                   'upright', 'mutedgtr', 'vibes', 'harmonica', 'trumpet', 'contrabass', 'trombone', 'tuba', 'bassoon'}
# orchestra sections the General MIDI bank only has as one ensemble sound
SF_ALIAS = {'sopsax': 'sopranosax', 'violins': 'strings', 'violas': 'strings', 'acguitar': 'steelguitar', 'twang': 'cleanguitar'}


def fallback_for(name):
    from .instruments import INSTRUMENTS
    if name in INSTRUMENTS:
        return name
    return FALLBACK.get(name, 'pluck_saw')
# Built-in names that sound noticeably better sampled; 'auto' engine swaps these for acoustic genres
ACOUSTIC = {'piano', 'epiano', 'clav', 'celesta', 'marimba', 'organ', 'guitar', 'violin', 'pizz', 'harp', 'timpani',
            'strings', 'choir', 'horn', 'brass', 'sax', 'flute', 'kalimba', 'steeldrum', 'bell',
            'cello', 'tremolo', 'spiccato', 'harpsichord', 'clarinet', 'oboe', 'accordion', 'banjo',
            'upright', 'mutedgtr', 'vibes', 'harmonica', 'trumpet', 'sitar', 'harmonium', 'santoor', 'koto', 'shakuhachi'}

# GM drum notes, and which GS kit suits which Studio Lab kit
GM_DRUM = {'kick': 36, 'snare': 38, 'clap': 39, 'snap': 39, 'rim': 37, 'chat': 42, 'ohat': 46, 'ride': 51, 'crash': 49,
           'tom': 45, 'tamb': 54, 'cowbell808': 56, 'shaker': 70, 'woodblock': 76, 'conga': 63, 'timp': 41, 'taiko': 35,
           'bongo': 60, 'bongo_lo': 61}
KIT_PROGRAM = {'acoustic': 0, 'soft': 32, 'jazz': 32, 'brush': 40, 'room': 8, 'rock': 16, 'orchestra': 48}


def sampled_note(name, midi, dur, vel=100):
    bk = bank()
    if bk is None:
        raise RuntimeError('sound library not installed')
    b, prog, _, tail = SAMPLED[name]
    midi = int(max(0, min(127, midi)))
    with bk.lock:
        g = norm_gain(bk, b, prog)
        x = render_note(bk, b, prog, midi, int(vel), max(0.03, dur), max_tail=tail)
    return x * g


def sampled_drum(name, kit='acoustic'):
    bk = bank()
    if bk is None or name not in GM_DRUM:
        return None
    prog = KIT_PROGRAM.get(kit, 0)
    with bk.lock:
        x = render_note(bk, 128, prog, GM_DRUM[name], 110, 0.6 if name not in ('crash', 'ride', 'ohat') else 2.0, max_tail=2.5)
    x = x.mean(axis=0)
    pk = float(np.max(np.abs(x)))
    return (x / pk).astype(np.float32) if pk > 1e-4 else None


# ---------------------------------------------------------------------------------------------------------------
# Performance pass for orchestral samples. General-MIDI patches are single, static recordings, which is what makes
# them sound "soundfonty". Real sections are several players slightly out of tune and time with each other, notes
# swell instead of switching on, and no two bows are the same. This adds those three things.
SECTIONS = {'strings', 'slowstrings', 'tremolo', 'spiccato', 'pizz', 'choir', 'brass', 'horn', 'trumpetsection'}
SUSTAINED = {'strings', 'slowstrings', 'tremolo', 'violin', 'viola', 'cello', 'contrabass', 'choir', 'brass', 'horn',
             'trombone', 'tuba', 'trumpet', 'trumpetsection', 'flute', 'oboe', 'clarinet', 'bassoon', 'piccolo'}
PERFORMED = SECTIONS | SUSTAINED


def _shift(x, cents, delay):
    """Re-pitch by a few cents (resampling) and delay by `delay` samples."""
    n = x.shape[1]
    r = 2 ** (cents / 1200.0)
    idx = np.arange(n, dtype=np.float64) * r
    idx = idx[idx < n - 1]
    i0 = idx.astype(np.int64)
    f = (idx - i0).astype(np.float32)
    y = np.zeros_like(x)
    m = min(len(i0), n - delay)
    for c in range(x.shape[0]):
        v = x[c, i0] * (1 - f) + x[c, i0 + 1] * f
        y[c, delay:delay + m] = v[:m]
    return y


def perform(name, sig, dur, vel, rr=0):
    sr = 44100
    x = sig.astype(np.float32)
    n = x.shape[1]
    import zlib
    rnd = np.random.default_rng(zlib.crc32(f'{name}-{rr}-{int(vel)}'.encode()))
    if name in SECTIONS:
        # extra desks: detuned, a few ms late, panned apart - an ensemble instead of one sample
        out = x.copy()
        for k, (cents, ms, pan) in enumerate([(-7, 9, -0.5), (6, 16, 0.5), (-3, 23, 0.0)]):
            c = cents + float(rnd.uniform(-2.5, 2.5))
            d = int(sr * (ms + float(rnd.uniform(-3, 3))) / 1000)
            y = _shift(x, c, d)
            y[0] *= 1 - max(0, pan) * 0.6
            y[1] *= 1 + min(0, pan) * 0.6
            out += y * 0.55
        x = out / 1.9
    if name in SUSTAINED and dur > 0.35:
        # expression: soft entry and a gentle swell over the note, more for quiet playing
        soft = 1.0 - vel / 127.0
        att = min(0.35, 0.05 + 0.12 * dur * (0.4 + soft))
        na = min(n, int(att * sr))
        env = np.ones(n, dtype=np.float32)
        env[:na] = np.linspace(0.0, 1.0, na, dtype=np.float32) ** 1.6
        nb = min(n, int(dur * sr))
        if nb > na + 10:
            sw = 0.10 + 0.14 * soft                     # crescendo into the middle of the note, then relax
            t = np.linspace(0, 1, nb - na, dtype=np.float32)
            env[na:nb] *= (1 - sw) + sw * np.sin(np.pi * 0.75 * t)      # swell to 2/3 of the note, then ease
        x = x * env
    # round robin: each take a hair different in level and tuning
    if rr:
        x = _shift(x, float(rnd.uniform(-3, 3)), 0) * float(rnd.uniform(0.93, 1.05))
    return x.astype(np.float32)
