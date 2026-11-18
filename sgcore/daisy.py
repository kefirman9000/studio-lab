"""'Daisy Bell (A Bicycle Built for Two)' (Harry Dacre, 1892 - public domain) sung by a creepy early-computer voice.

The voice is a small formant singing synthesizer written for this: a buzzing pulse source at the exact note pitch (no
vibrato - perfectly, eerily steady), shaped by three moving vocal-tract resonances for each vowel, with noise for the
consonants (s, sh, f, h, the bursts of b / d / g / k / p / t). Then it is made to sound like a machine: an octave-down
double, sample-rate and bit reduction, and a short metallic room. The second chorus winds down like a computer losing
power - slower and slower, sinking in pitch - and stops.

The accompaniment is an old-computer music box: a square-wave waltz bass, celesta oom-pah-pah chords and a quiet organ.
"""
import os
import time

import numpy as np
from scipy import signal

from .dsp import SR, write_wav
from .instruments import INSTRUMENTS

# ----------------------------------------------------------------------------- the song (C major, 3/4)
# each sung syllable: (phonemes, midi note, beats). Phonemes: vowels i I e E ae a O o U u V @ R(er), diphthongs aI eI oU;
# consonants b d g p t k m n l r j w v f s z S(sh) T(th) D(dh) h tS dZ
MELODY = [
    ('d eI', 79, 3), ('z i', 76, 3), ('d eI', 72, 3), ('z i', 67, 3),
    ('g I v', 69, 1), ('m i', 71, 1), ('j O r', 72, 1), ('ae n', 69, 2), ('s R', 72, 1), ('d u', 67, 6),
    ('aI m', 74, 3), ('h ae f', 79, 3), ('k r eI', 76, 3), ('z i', 72, 3),
    ('O l', 69, 1), ('f O r', 71, 1), ('D @', 72, 1), ('l V v', 74, 2), ('@ v', 76, 1), ('j u', 74, 6),
    ('I t', 76, 1), ('w oU n t', 77, 1), ('b i', 76, 1), ('@', 74, 1), ('s t aI', 79, 2), ('l I S', 76, 1), ('m a r', 74, 2),
    ('r I dZ', 72, 3),
    ('aI', 74, 1), ('k ae n t', 76, 1), ('@', 72, 1), ('f O r d', 69, 2), ('@', 72, 1), ('k a r', 69, 1), ('r I dZ', 67, 4),
    ('b V t', 67, 1),
    ('j u l', 72, 2), ('l U k', 76, 1), ('s w i t', 74, 2), ('V p', 67, 1), ('a n', 72, 2), ('D @', 76, 1),
    ('s i t', 74, 2), ('@ v', 76, 1), ('@', 77, 1), ('b aI', 79, 1), ('s @', 76, 1), ('k @ l', 72, 2), ('b I l t', 74, 1),
    ('f O r', 67, 3), ('t u', 72, 6),
]
LYRICS = ('Daisy, Daisy, give me your answer, do. I\'m half crazy, all for the love of you. It won\'t be a stylish '
          'marriage, I can\'t afford a carriage, but you\'ll look sweet upon the seat of a bicycle built for two.')
# one chord per 3/4 bar (root midi, quality)
C, F, G, A, D = 48, 53, 55, 57, 50
CHORDS = [(C, ''), (C, ''), (C, ''), (C, '7'), (F, ''), (F, ''), (C, ''), (C, ''), (G, '7'), (G, '7'), (C, ''), (A, 'm'),
          (D, '7'), (D, '7'), (G, '7'), (G, '7'), (C, ''), (C, ''), (C, ''), (C, ''), (A, 'm'), (F, ''), (C, ''), (G, '7'),
          (C, ''), (G, '7'), (C, ''), (G, '7'), (C, ''), (C, ''), (G, '7'), (C, ''), (C, '')]
QUAL = {'': (0, 4, 7), '7': (0, 4, 7, 10), 'm': (0, 3, 7)}

# ----------------------------------------------------------------------------- the voice
VOWELS = {'i': (310, 2790, 3310), 'I': (430, 2480, 3070), 'e': (480, 2350, 3000), 'E': (610, 2330, 2990),
          'ae': (820, 2000, 2850), 'a': (850, 1220, 2810), 'O': (590, 920, 2710), 'o': (500, 900, 2700),
          'U': (470, 1160, 2680), 'u': (370, 950, 2670), 'V': (720, 1350, 2780), '@': (600, 1500, 2700),
          'R': (490, 1350, 1700)}
DIPH = {'aI': ('a', 'i'), 'eI': ('e', 'i'), 'oU': ('o', 'U')}
APPROX = {'l': (380, 1100, 2700), 'r': (420, 1250, 1600), 'j': (300, 2600, 3200), 'w': (330, 750, 2500),
          'm': (280, 1100, 2400), 'n': (280, 1700, 2600)}
# consonants: (duration s, voicing 0..1, noise level, noise band (lo, hi) Hz, burst)
CONS = {'s': (0.11, 0.0, 0.5, (4500, 9500), False), 'z': (0.09, 0.5, 0.35, (4000, 9000), False),
        'S': (0.11, 0.0, 0.5, (1800, 5500), False), 'f': (0.09, 0.0, 0.25, (1200, 8000), False),
        'v': (0.07, 0.6, 0.12, (1200, 6000), False), 'T': (0.08, 0.0, 0.18, (1500, 8000), False),
        'D': (0.06, 0.6, 0.1, (1500, 6000), False), 'h': (0.08, 0.0, 0.3, (600, 4000), False),
        'b': (0.06, 0.25, 0.4, (300, 1500), True), 'p': (0.08, 0.0, 0.5, (300, 1500), True),
        'd': (0.06, 0.25, 0.45, (2500, 6000), True), 't': (0.08, 0.0, 0.55, (2500, 7000), True),
        'g': (0.06, 0.25, 0.4, (1400, 3200), True), 'k': (0.08, 0.0, 0.5, (1400, 3500), True),
        'tS': (0.12, 0.0, 0.55, (1800, 5500), True), 'dZ': (0.11, 0.35, 0.45, (1800, 5500), True)}
BLOCK = 64
# per-vowel level so every vowel sings at the same loudness (measured against 'a'; a parallel formant bank makes
# open and front vowels louder than closed ones)
VGAIN = {'i': 1.89, 'I': 0.47, 'e': 0.55, 'E': 1.29, 'ae': 1.35, 'O': 0.92, 'o': 0.58, 'U': 0.49, 'u': 0.99, 'V': 1.41, '@': 1.17, 'R': 0.57}


def _segments(phonemes, dur):
    """Split one syllable into timed segments: [(kind, data, seconds)] - consonants take their own length, the vowel
    (or diphthong) fills what's left, a final consonant closes the note."""
    ph = phonemes.split()
    vi = next((i for i, p in enumerate(ph) if p in VOWELS or p in DIPH), 0)
    onset, nucleus, coda = ph[:vi], ph[vi], ph[vi + 1:]

    def clen(p):
        return CONS[p][0] if p in CONS else 0.06
    fixed = sum(clen(p) for p in onset + coda)
    vlen = max(0.06, dur - fixed)
    seg = [(p, clen(p)) for p in onset]
    if nucleus in DIPH:
        a, b = DIPH[nucleus]
        off = min(0.14, 0.3 * vlen)                       # hold the main vowel; glide to the second only at the very end
        seg += [(a, vlen - off), (b, off)]
    else:
        seg.append((nucleus, vlen))
    seg += [(p, clen(p)) for p in coda]
    return seg


def _resonate(x, freqs, bws, n, gains=(1.0, 0.55, 0.3)):
    """A parallel bank of three formant resonators (centres move block by block) - each sees the full source, so every
    vowel comes out at a steady level (a series chain cancels itself out between distant formants)."""
    out = np.zeros_like(x)
    for k in range(3):
        y = np.zeros_like(x)
        zi = np.zeros(2)
        r = np.exp(-np.pi * bws[k] / SR)
        for s in range(0, n, BLOCK):
            e = min(n, s + BLOCK)
            th = 2 * np.pi * freqs[k][s // BLOCK] / SR
            a = [1.0, -2 * r * np.cos(th), r * r]
            g = abs(1 - 2 * r * np.cos(th) * np.exp(-1j * th) + r * r * np.exp(-2j * th))   # unity gain at the peak
            y[s:e], zi = signal.lfilter([g], a, x[s:e], zi=zi)
        out += gains[k] * y
    return out


def sing(notes, rng=None, formant_scale=1.0, tilt=0.6):
    """notes: [(start_s, dur_s, midi_float, phonemes)] -> mono voice. Pitch is held dead steady on each note (a fast
    25 ms glide between notes, no vibrato) - the uncanny, perfectly-in-tune machine."""
    rng = rng or np.random.default_rng(1892)
    end = max(s + d for s, d, m, p in notes) + 0.6
    n = int(end * SR) + BLOCK
    nb = n // BLOCK + 1
    f0 = np.zeros(n)
    vamp = np.zeros(n)
    nband = []                                            # (start, end, lo, hi, level, burst)
    targ = [np.full(nb, 500.0), np.full(nb, 1500.0), np.full(nb, 2600.0)]
    prev = None
    for start, dur, midi, ph in notes:
        i0, i1 = int(start * SR), int((start + dur) * SR)
        hz = 440.0 * 2 ** ((midi - 69) / 12)
        g = min(int(0.025 * SR), i1 - i0)
        f0[i0:i1] = hz
        if prev:                                          # quick portamento from the last note
            f0[i0:i0 + g] = np.linspace(prev, hz, g)
        prev = hz
        segs = _segments(ph, dur)
        lead = 0.0
        for p, d in segs:                                 # onset consonants go just before the beat, like a singer's
            if p in VOWELS or p in DIPH:
                break
            lead += d
        lead = min(lead, 0.12)
        t = max(0.0, start - lead)
        for p, d in segs:
            a, b = int(t * SR), int((t + d) * SR)
            if p in VOWELS or p in APPROX:
                fm = VOWELS.get(p) or APPROX[p]
                for k in range(3):
                    targ[k][a // BLOCK:b // BLOCK + 1] = fm[k] * formant_scale
                lvl = (1.0 if p in VOWELS else (0.45 if p in ('m', 'n') else 0.7)) * VGAIN.get(p, 1.0)
                vamp[a:b] = lvl
            else:
                cd, voi, nl, band, burst = CONS[p]
                vamp[a:b] = voi
                nband.append((a, b, band[0], band[1], nl, burst))
            t += d
        vamp[i1 - int(0.015 * SR):i1] *= np.linspace(1, 0.3, int(0.015 * SR))   # a tiny release between notes
    # formants glide (coarticulation): ~25 ms smoothing at block rate
    k_s = np.exp(-BLOCK / (0.025 * SR))
    for k in range(3):
        targ[k] = signal.lfilter([1 - k_s], [1, -k_s], targ[k], zi=[targ[k][0] * k_s])[0]
    vamp = signal.lfilter([1 - 0.995], [1, -0.995], vamp)
    # buzzy glottal source: a band-limited-ish sawtooth (the classic speech-synth buzz) with a little tilt
    ph_ = np.cumsum(f0 / SR)
    src = (2 * (ph_ % 1.0) - 1.0) * (f0 > 0)
    src = signal.lfilter([1.0], [1, -tilt], src) * 0.4      # more tilt = a softer, rounder, less buzzy voice
    voice = _resonate(src * vamp, targ, (120, 150, 200), n)
    # every sung syllable at the same loudness: a narrow resonance makes a note louder or softer depending on whether one
    # of its harmonics happens to land on it, so each note's vowel is levelled to one target (smoothly, ~12 ms)
    gain = np.ones(n)
    for start, dur, midi, ph in notes:
        i0, i1 = int(start * SR), min(n, int((start + dur) * SR))
        sel = vamp[i0:i1] > 0.5
        if sel.sum() < 64:
            continue
        r = float(np.sqrt(np.mean(voice[i0:i1][sel] ** 2)))
        gain[i0:i1] = np.clip(0.25 / (r + 1e-9), 0.05, 20.0)
    kg = np.exp(-1 / (0.012 * SR))
    gain = signal.lfilter([1 - kg], [1, -kg], gain, zi=[gain[0] * kg])[0]
    voice = voice * gain
    # consonant noise
    noise = np.zeros(n)
    for a, b, lo, hi, lvl, burst in nband:
        if b <= a:
            continue
        sos = signal.butter(2, [lo / (SR / 2), min(0.99, hi / (SR / 2))], 'band', output='sos')
        w = signal.sosfilt(sos, rng.standard_normal(b - a))
        env = np.ones(b - a)
        if burst:                                         # closure (silence), then the release burst
            c = int((b - a) * 0.55)
            env[:c] = 0.0
            env[c:] = np.exp(-np.linspace(0, 6, b - a - c))
        else:
            r = max(1, int(0.01 * SR))
            env[:r] *= np.linspace(0, 1, r)
            env[-r:] *= np.linspace(1, 0, r)
        w = w / (np.sqrt(np.mean(w ** 2)) + 1e-9)
        noise[a:b] += w * env * lvl
    y = voice + noise * 0.09                              # consonants ~10 dB under the vowels, as in real singing
    return y / (np.max(np.abs(y)) + 1e-9)


def robotize(y, crush_hz=16000, bits=10):
    """The machine: sample-and-hold to a low sample rate, bit reduction, an octave-down double and a short metallic comb."""
    hold = max(1, int(SR / crush_hz))
    y = np.repeat(y[::hold], hold)[:len(y)]
    q = 2 ** (bits - 1)
    y = np.round(y * q) / q
    sos = signal.butter(4, 7000 / (SR / 2), output='sos')
    y = signal.sosfilt(sos, y)
    # octave-down double: half-speed copy would change timing, so ring-modulate a copy for the hollow sub-voice
    comb = y.copy()
    dly = int(0.0073 * SR)
    for _ in range(3):
        comb[dly:] += 0.45 * comb[:-dly]
    return 0.75 * y + 0.25 * comb / (np.max(np.abs(comb)) + 1e-9)


# ----------------------------------------------------------------------------- tempo map: the second chorus winds down
def _timeline(bpm, wind_down=True, deep=False):
    """[(start_s, dur_s, beat_index, chorus)] for every beat of: 4 intro bars, chorus 1, 2 bars, chorus 2."""
    spb = 60.0 / bpm
    beats = []
    t = 0.0
    total = 12 + 99 + 6 + 99
    for b in range(total):
        f, drop = 1.0, 0.0
        second = b >= 12 + 99 + 6
        if second and wind_down:
            k = (b - (12 + 99 + 6)) / 99.0                # 0 .. 1 through chorus 2
            start, slow, sink = (0.2, 3.2, 14.0) if deep else (0.45, 2.2, 9.0)
            if k > start:                                  # the machine starts to fail (the deep voice: sooner, further)
                x = (k - start) / (1 - start)
                f = 1.0 + slow * x ** 1.6                  # up to 3-4x slower
                drop = -sink * x ** 1.8                    # sinking 9-14 semitones
        beats.append((t, spb * f, drop))
        t += spb * f
    return beats


VOICES = {
    'machine': dict(label='Creepy machine (high, buzzy, crushed)', bpm=104, transpose=0, formant=1.0, tilt=0.6, crush=(16000, 10),
                    shadow=(-12, 0.3, (11025, 8))),
    'deep': dict(label='Deep, calm computer (slow, winding down)', bpm=86, transpose=-12, formant=0.86, tilt=0.86, crush=(44100, 16),
                 shadow=(-12, 0.12, (44100, 16))),
}


def render(out_dir, bpm=None, log=print, wind_down=True, voice='machine'):
    """Render the song -> dict(files=..., duration=...). voice: 'machine' (the creepy, buzzy, bit-crushed early speech synth)
    or 'deep' (a low, calm, smooth computer voice - slower, and it starts to wind down early in the second chorus)."""
    from . import api
    vname = voice if voice in VOICES else 'machine'
    V = VOICES[vname]
    bpm = bpm or V['bpm']
    rng = np.random.default_rng(1892)
    tl = _timeline(bpm, wind_down, deep=(vname == 'deep'))

    def at(beat):                                         # beat (float) -> (seconds, pitch drop)
        i = min(int(beat), len(tl) - 1)
        s, d, drop = tl[i]
        return s + (beat - i) * d, drop

    log('Building the voice …')
    notes = []
    for chorus, first in ((0, 12), (1, 12 + 99 + 6)):
        b = first
        for ph, midi, beats in MELODY:
            s0, drop = at(b)
            s1, _ = at(b + beats)
            notes.append((s0, max(0.08, s1 - s0 - 0.02), midi + V['transpose'] + drop, ph))
            b += beats
    sung = sing(notes, rng, V['formant'], V['tilt'])
    voice_ = robotize(sung, *V['crush']) if V['crush'][0] < SR else sung
    # a hollow octave-down shadow of the voice (same timing) for the uncanny doubled sound
    sh_t, sh_g, sh_c = V['shadow']
    shadow = sing([(s, d, m + sh_t, p) for s, d, m, p in notes], rng, V['formant'] * 0.9, V['tilt'])
    shadow = (robotize(shadow, *sh_c) if sh_c[0] < SR else shadow) * (sh_g / 0.3)
    voice = voice_
    log('Building the music box …')
    n = len(voice) + int(3 * SR)
    acc = np.zeros((2, n))

    def put(inst, midi, s, d, gain, pan=0.0, p=None):
        y = np.asarray(INSTRUMENTS[inst](float(midi), d, p or {}), dtype=np.float64)
        if y.ndim == 1:
            y = np.vstack([y, y])
        i = int(s * SR)
        y = y[:, :max(0, n - i)]
        acc[0, i:i + y.shape[1]] += y[0] * gain * (1 - pan)
        acc[1, i:i + y.shape[1]] += y[1] * gain * (1 + pan)

    bars = [(0, 4, 0)] + [(12 + bar * 3, 1, bar) for bar in range(33)] + [(111, 2, 32)] + \
        [(117 + bar * 3, 1, bar) for bar in range(33)]
    for b0, count, ci in bars:
        for rep in range(count):
            beat = b0 + rep * 3
            root, q = CHORDS[min(ci, len(CHORDS) - 1)] if count == 1 else (C, '')
            s0, drop = at(beat)
            if s0 * SR >= n - SR:
                continue
            dur3 = at(beat + 3)[0] - s0
            put('chipbass' if vname == 'machine' else 'sinebass', root - 12 + drop, s0, dur3 * 0.45, 0.30)
            for k in (1, 2):                              # oom - pah - pah
                sk, dk = at(beat + k)
                for iv in QUAL[q]:
                    put('celesta', root + 12 + iv + dk, sk, (at(beat + k + 1)[0] - sk) * 0.6, 0.07, pan=-0.3 + 0.2 * iv / 10)
            put('organ', root + drop, s0, dur3 * 0.95, 0.025 if vname == 'machine' else 0.045, pan=0.2)
    v = np.vstack([voice, voice])
    sh = np.vstack([shadow, shadow])
    vox = np.zeros_like(acc)
    vox[:, :v.shape[1]] = v + 0.3 * sh * np.array([[0.7], [1.3]])
    rms = lambda a: float(np.sqrt(np.mean(a[a != 0] ** 2))) if np.any(a) else 1.0
    acc *= (rms(vox) / rms(acc)) * 10 ** (-9 / 20)        # the voice sits ~9 dB above the music box
    mix = acc + vox
    # a short, metallic room on everything
    rev = np.zeros_like(mix)
    for dl, g in ((0.031, 0.32), (0.047, 0.26), (0.071, 0.2), (0.103, 0.14)):
        d = int(dl * SR)
        rev[:, d:] += g * mix[:, :-d]
    mix = mix + 0.35 * rev
    end = int((at(len(tl) - 1)[0] + 2.0) * SR)
    mix = mix[:, :min(mix.shape[1], end)]
    fade = int(1.5 * SR)
    mix[:, -fade:] *= np.linspace(1, 0, fade)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
    os.makedirs(out_dir, exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    wav = os.path.join(out_dir, f'Daisy_Bell_{vname}_voice_{stamp}.wav')
    write_wav(wav, mix)
    files = dict(wav=wav)
    if api.have_ffmpeg():
        from .dsp import write_mp3
        mp3 = write_mp3(wav, wav[:-4] + '.mp3', 256, dict(title='Daisy Bell (A Bicycle Built for Two)', artist='Studio Lab',
                                                          composer='Harry Dacre (1892)'))
        if mp3:
            files['mp3'] = mp3
    secs = mix.shape[1] / SR
    log(f'Done: {secs:.0f} s')
    return dict(files=files, duration=f'{int(secs // 60)}:{int(secs % 60):02d}', seconds=secs, bpm=bpm, voice=vname,
                voice_label=V['label'], key='C major' if not V['transpose'] else 'C major (octave down)',
                meter='3/4', lyrics=LYRICS)
