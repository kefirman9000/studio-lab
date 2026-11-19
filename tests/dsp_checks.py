"""Fast checks of the DSP building blocks the master depends on (a few seconds).
   python -m tests.dsp_checks"""
import os
import sys
import tempfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from sgcore import dsp  # noqa: E402
from sgcore.dsp import SR  # noqa: E402
from sgcore import render  # noqa: E402


def _sine(f, sec, db, stereo=True):
    t = np.arange(int(sec * SR)) / SR
    x = 10 ** (db / 20) * np.sin(2 * np.pi * f * t)
    return np.vstack([x, x]) if stereo else x


def test_lufs_reference_tones():
    # EBU Tech 3341: a 997 Hz stereo sine at -23 dBFS reads -23 LUFS (+-0.1)
    for db in (-23.0, -18.0, -10.0):
        v = dsp.lufs(_sine(997, 20, db))
        assert abs(v - db) < 0.1, (db, v)


def test_lufs_matches_pyloudnorm():
    try:
        import pyloudnorm as pyln
    except ImportError:
        print('   (pyloudnorm not installed - comparison skipped)')
        return
    rng = np.random.default_rng(3)
    meter = pyln.Meter(SR)
    for k in range(4):                      # pink-ish noise with loud and quiet parts (tests the gating too)
        n = rng.standard_normal((2, SR * 12))
        n = np.cumsum(n, axis=1)
        n -= dsp.lp(n, 20)
        n /= np.max(np.abs(n))
        env = np.repeat([0.05, 1.0, 0.3, 1.0], SR * 3)[None, :]
        x = n * env * 10 ** (-(6 + 3 * k) / 20)
        a, b = dsp.lufs(x), meter.integrated_loudness(x.T)
        assert abs(a - b) < 0.2, (k, a, b)


def test_loudness_range():
    x = np.hstack([_sine(997, 15, -30), _sine(997, 15, -15)])
    lra, st_max = render.loudness_range(x)
    assert 13 < lra < 16, lra
    assert abs(st_max - -15) < 0.5, st_max


def test_wav24_roundtrip():
    x = _sine(440, 0.5, -6)
    with tempfile.TemporaryDirectory() as d:
        p = dsp.write_wav(os.path.join(d, 'a.wav'), x, bits=24)
        with wave.open(p) as w:
            assert w.getsampwidth() == 3 and w.getnchannels() == 2
            raw = np.frombuffer(w.readframes(w.getnframes()), np.uint8).reshape(-1, 3)
        v = (raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16))
        v = np.where(v >= 1 << 23, v - (1 << 24), v).reshape(-1, 2).T / 8388607
        assert np.max(np.abs(v - x)) < 2e-7


def test_oversampled_saturation_less_aliasing():
    x = _sine(7919, 1.0, -1)                # a bright tone driven hard: its harmonics fold back at 1x
    f = lambda u: np.tanh(u * 4) / np.tanh(4)
    def alias_db(y):
        P = np.abs(np.fft.rfft(y[0] * np.hanning(y.shape[1]))) ** 2
        fr = np.fft.rfftfreq(y.shape[1], 1 / SR)
        harm = np.zeros_like(fr, bool)
        for k in range(1, 40, 2):
            h = 7919 * k
            if h < SR / 2:
                harm |= np.abs(fr - h) < 30
        return 10 * np.log10(P[~harm & (fr > 50)].sum() / P[harm].sum())
    assert alias_db(render.oversampled(f, x, 2)) < alias_db(f(x)) - 6


def test_dynamic_eq_only_acts_on_buildup():
    rng = np.random.default_rng(1)
    n = rng.standard_normal((2, SR * 8)) * 0.05
    calm = n.copy()
    y, st = render.dynamic_eq(calm)
    assert max(v for k, v in st.items() if isinstance(k, int)) < 0.5                    # an even song: left alone
    mud = n.copy()
    mud[:, SR * 4:SR * 6] += _sine(300, 2, -32)            # two seconds of low-mid build-up (overall level ~same)
    y, st = render.dynamic_eq(mud)
    assert st.get(300, 0) > 1.0, st
    e = lambda z, a, b: 10 * np.log10(np.mean(dsp.bp(z, 250, 360)[:, a:b] ** 2))
    assert e(y, SR * 4, SR * 6) < e(mud, SR * 4, SR * 6) - 1.0     # the build-up is cut
    assert abs(e(y, SR, SR * 3) - e(mud, SR, SR * 3)) < 0.3         # the rest isn't


def test_master_neutral_width_and_true_peak():
    rng = np.random.default_rng(2)
    x = rng.standard_normal((2, SR * 6)) * 0.1
    x[1] = 0.7 * x[0] + 0.3 * x[1]
    y = render.master(x.copy(), dict(lufs=-9, width=1.0), log=lambda *a: None)
    from scipy import signal
    tp = 20 * np.log10(np.max(np.abs(signal.resample_poly(y, 4, 1, axis=-1))))
    assert tp <= -0.99, tp
    assert abs(render.loud_part_lufs(y) - -9) < 0.6, render.loud_part_lufs(y)


def test_ladder_filter():
    from sgcore import fastdsp
    if not fastdsp.HAVE_NUMBA:
        print('   (numba not installed - ladder skipped)')
        return
    rng = np.random.default_rng(0)
    x = rng.standard_normal(SR) * 0.3
    y = fastdsp.ladder(x, 1000.0, 0.3, 1.2, SR)
    assert np.isfinite(y).all()
    P = np.abs(np.fft.rfft(y)) ** 2
    f = np.fft.rfftfreq(len(y), 1 / SR)
    lo, hi = P[(f > 80) & (f < 300)].mean(), P[(f > 7000) & (f < 9000)].mean()
    assert 10 * np.log10(lo / hi) > 60                       # 24 dB / oct: three octaves up is far down
    s = fastdsp.ladder(x * 0.01, np.geomspace(200, 8000, SR), 1.0, 1.0, SR)
    assert np.isfinite(s).all() and np.max(np.abs(s)) < 2.0   # self-oscillation stays bounded


def test_analog_notes_vary_and_respond_to_velocity():
    from sgcore import va
    from sgcore.instruments import INSTRUMENTS
    va.CHARACTER = 'analog'
    def hf(v):
        out = []
        for _ in range(8):
            va.NOTE = {'vel': v}
            y = np.asarray(INSTRUMENTS['stab'](60, 0.4, {'vel': v, 'spb': 0.5}), float).mean(axis=0)
            va.NOTE = None
            P = np.abs(np.fft.rfft(y)) ** 2
            f = np.fft.rfftfreq(len(y), 1 / SR)
            out.append(10 * np.log10(P[f > 2000].sum() / P[f < 2000].sum()))
        return np.mean(out)
    assert hf(1.0) > hf(0.6) + 2.0                           # harder = brighter, not only louder
    a = np.asarray(INSTRUMENTS['pluck_saw'](60, 0.3, {'spb': 0.5}))
    b = np.asarray(INSTRUMENTS['pluck_saw'](60, 0.3, {'spb': 0.5}))
    assert a.shape == b.shape and not np.allclose(a, b)      # every take differs
    va.CHARACTER = 'classic'
    c = np.asarray(INSTRUMENTS['stab'](60, 0.4, {'spb': 0.5}))
    va.CHARACTER = 'analog'
    assert np.isfinite(c).all()


def test_fdn_reverb():
    from sgcore import fastdsp
    if not fastdsp.HAVE_NUMBA:
        print('   (numba not installed - FDN skipped)')
        return
    ir = fastdsp.fdn_ir(2.0, SR, size=1.0, bright=0.5, predelay=0.02, seed=1)
    assert np.isfinite(ir).all() and abs(np.sum(ir ** 2) / 2 - 1) < 1e-6
    def t60(band):
        y = dsp.bp(ir, *band).mean(0) ** 2
        e = 10 * np.log10(np.cumsum(y[::-1])[::-1] + 1e-20)
        e -= e[0]
        return np.argmax(e < -30) / SR * 2
    assert t60((5000, 9000)) < t60((200, 500))               # highs die away faster than lows


def test_new_part_effects():
    from sgcore.compose import Options, compose
    from sgcore.render import Renderer
    from sgcore import fx2, part_effects
    r = Renderer(compose(Options(style='house', seed=3, length=0.5)), log=lambda *a: None)
    x = (np.random.default_rng(0).standard_normal((2, r.length)) * 0.1).astype(np.float32)
    for pid, (_, cfg) in part_effects.PRESETS.items():
        if any(k in fx2.KEYS for k in cfg):
            y = fx2.apply(x, dict(cfg), r)
            assert y.shape == x.shape and np.isfinite(y).all(), pid
            assert np.sqrt(np.mean((y - x) ** 2)) > 0.01 * np.sqrt(np.mean(x ** 2)), pid      # it does something
            t = dict(cfg)
            assert pid in part_effects.describe(t), (pid, part_effects.describe(t))


if __name__ == '__main__':
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print('ok  ', name)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print('FAIL', name, repr(e))
    print('FAILED' if fails else 'all passed')
    sys.exit(1 if fails else 0)
