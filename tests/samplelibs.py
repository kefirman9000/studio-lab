"""Real-instrument libraries, offline: a tiny fake library goes through the same install / verify / play path."""
import os
import shutil
import struct
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sgcore import samplelibs as sl  # noqa: E402
from sgcore.dsp import SR  # noqa: E402


def wav24(freq, secs=1.0, amp=0.5, ch=2, rate=48000):
    n = int(secs * rate)
    x = (np.sin(2 * np.pi * freq * np.arange(n) / rate) * amp * 8388607).astype(np.int32)
    x = np.repeat(x[:, None], ch, axis=1).ravel()
    b = np.stack([(x & 0xff), (x >> 8) & 0xff, (x >> 16) & 0xff], axis=1).astype(np.uint8).tobytes()
    fmt = struct.pack('<HHIIHH', 1, ch, rate, rate * ch * 3, ch * 3, 24)
    body = b'WAVE' + b'fmt ' + struct.pack('<I', len(fmt)) + fmt + b'data' + struct.pack('<I', len(b)) + b
    return b'RIFF' + struct.pack('<I', len(body)) + body


def main():
    tmp = tempfile.mkdtemp()
    old_dir, old_man = sl.REAL_DIR, sl._man
    try:
        sl.REAL_DIR = tmp
        blobs, files = {}, []
        # strings: violins at A4 (69) and E5 (76), two dynamics, two round robins; spiccato at A4; celli at C3
        for n, f0 in ((69, 440.0), (76, 659.26)):
            for v, amp in ((1, 0.2), (2, 0.6)):
                for r in (1, 2):
                    p = f'Strings/Violin Section/susVib/VlnEns_susVib_{n}_v{v}_{r}.wav'
                    blobs[p] = wav24(f0 * (1 + 0.001 * r), 1.5, amp)
                    files.append(dict(p=p, i='violins', a='sus', n=n, v=v, r=r))
        blobs['spic.wav'] = wav24(440.0, 0.4, 0.5)
        files.append(dict(p='spic.wav', i='violins', a='short', n=69, v=1, r=1))
        blobs['cello.wav'] = wav24(130.81, 1.5, 0.5)
        files.append(dict(p='cello.wav', i='celli', a='sus', n=48, v=1, r=1))
        files.append(dict(p='cello.wav', i='celli', a='short', n=48, v=1, r=1))
        for r in (1, 2, 3):
            p = f'Claps/Clap_rr{r}.wav'
            blobs[p] = wav24(1000 + 100 * r, 0.3, 0.7, ch=1)
            files.append(dict(p=p, i='clap', a='hit', v=1, r=r))
        for f in files:
            f['sha'] = sl.git_blob_sha1(blobs[f['p']])
            f['s'] = len(blobs[f['p']])
        sl._man = {'libs': {lib: dict(repo='x/y', commit='c0ffee', title=lib, by='test', files=[], bytes=0) for lib in sl.LIB_ORDER}}
        sl._man['libs']['strings'].update(files=[f for f in files if f['i'] in ('violins', 'celli')],
                                          bytes=sum(f['s'] for f in files if f['i'] != 'clap'))
        sl._man['libs']['percussion'].update(files=[f for f in files if f['i'] == 'clap'])
        sl._idx.clear()
        sl._cache.clear()

        # a tampered download is refused
        bad = dict(blobs)
        bad['spic.wav'] = bad['spic.wav'][:-10] + b'0123456789'
        log = []
        sl.install('strings', log.append, fetch=lambda repo, commit, p: bad[p])
        assert any('checksum mismatch' in x for x in log), log
        assert not os.path.isfile(os.path.join(tmp, 'strings', [f for f in files if f['p'] == 'spic.wav'][0]['sha'] + '.wav'))
        # the real install (resumes, verifies, converts 24-bit / 48 kHz to 16-bit / 44.1 kHz stereo)
        sl.install('strings', lambda *a: None, fetch=lambda repo, commit, p: blobs[p])
        sl.install('percussion', lambda *a: None, fetch=lambda repo, commit, p: blobs[p])
        assert sl.installed('strings') and sl.installed('percussion')
        x = sl._load('strings', sl._man['libs']['strings']['files'][0])
        assert x.shape[0] == 2 and abs(x.shape[1] / SR - 1.5) < 0.02
        print('ok  install: checksum refusal, resume, 24-bit 48 kHz -> 16-bit 44.1 kHz')

        # nearest recorded note, re-pitched; loud notes use the loud layer; round robins differ; short notes -> spiccato
        loud = sl.note('violins', 'sus', 71, 1.0, 0.95, 'a')
        soft = sl.note('violins', 'sus', 71, 1.0, 0.1, 'a')
        assert np.abs(loud).max() > 2 * np.abs(soft).max()
        a, b = sl.note('violins', 'sus', 69, 1.0, 0.95, '0'), sl.note('violins', 'sus', 69, 1.0, 0.95, '1')
        assert not np.allclose(a, b)
        spec = np.abs(np.fft.rfft(sl.note('violins', 'sus', 71, 1.0, 0.9, 'a')[0][:16384]))
        peak = np.argmax(spec) * SR / 16384
        assert abs(peak - 493.9) < 6, peak                                  # B4 from the A4 recording
        sl._idx.clear()
        short = sl.orch_note('strings', 69, 0.12, 0.8, 'x')
        assert short is not None and short.shape[1] < 0.4 * SR
        low = sl.orch_note('strings', 40, 1.0, 0.8, 'x')                    # section split: E2 goes to the celli
        spec = np.abs(np.fft.rfft(low[0][:16384]))
        assert abs(np.argmax(spec) * SR / 16384 - 82.4) < 4
        assert sl.plays('strings') and sl.plays('spiccato') and not sl.plays('flute')
        hits = {sl.hit('clap', 0.8, str(k)).tobytes() for k in range(3)}
        assert len(hits) == 3
        ids = {c['id'] for c in sl.choices('pad')}
        assert 'real:strings' in ids and 'real:flute' not in ids, ids                # only installed instruments are offered
        print('ok  playback: nearest note, velocity layers, round robins, spiccato for short notes, section split')

        # songs use them: strings parts become real, acoustic kits get real claps
        from sgcore.compose import compose, Options
        from sgcore.render import Renderer
        s = compose(Options(style='orchestral', seed=3))
        real = [t for t in s['st']['tracks'] if t['inst'].startswith('real:')]
        assert any(t['inst'] == 'real:strings' for t in real), [t['inst'] for t in s['st']['tracks']]
        assert all(t.get('fallback') for t in real)
        s2 = compose(Options(style='orchestral', seed=3, engine='synth'))
        assert not any(t['inst'].startswith('real:') for t in s2['st']['tracks'])
        r = Renderer(s, log=lambda *a: None)
        t = next(t for t in s['st']['tracks'] if t['inst'] == 'real:strings')
        evs = [e for e in s['events'] if e.track == t['name']][:4]
        sigs = [r._note(t, e, None) for e in evs]
        assert all(x is not None and x.shape[0] == 2 for x in sigs)
        print('ok  songs: orchestral parts play the real library (not with the synth engine), with fallbacks')
    finally:
        sl.REAL_DIR, sl._man = old_dir, old_man
        sl._idx.clear()
        sl._cache.clear()
        shutil.rmtree(tmp, ignore_errors=True)
    print('all good')


if __name__ == '__main__':
    main()
