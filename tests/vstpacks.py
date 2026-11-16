"""Offline tests for the VST pack downloader and the genre rigs (no internet, no plugins needed).
   python -m tests.vstpacks"""
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sgcore import vstpacks, vstrigs, vsthost
from sgcore.compose import Options, compose
from sgcore.styles import STYLES


def rel(tag, names, pre=False):
    return dict(tag_name=tag, prerelease=pre, draft=False,
                assets=[dict(name=n, browser_download_url='https://github.com/x/y/releases/download/' + tag + '/' + n, size=1) for n in names])


def test_pick_asset():
    surge = vstpacks.BY_ID['surge']
    rels = [rel('Nightly', ['surge-xt-win64-NIGHTLY-pluginsonly.zip'], pre=True),
            rel('1.3.4', ['surge-xt-win64-1.3.4-setup.exe', 'surge-xt-win64-1.3.4-pluginsonly.zip', 'surge-xt-macOS-1.3.4.dmg',
                          'surge-xt-linux-x86_64-1.3.4.tar.gz', 'surge-xt-linux-1.3.4-x86_64.deb', 'surge-xt-win64-1.3.4-setup.exe.sha256'])]
    assert vstpacks.pick_asset(surge, rels, 'windows')['name'] == 'surge-xt-win64-1.3.4-pluginsonly.zip'   # stable beats nightly
    assert vstpacks.pick_asset(surge, rels, 'mac')['name'].endswith('.dmg')
    assert vstpacks.pick_asset(surge, rels, 'linux')['name'].endswith('.tar.gz')
    dg = [dict(tag_name='v1', prerelease=False, draft=False, assets=[
        dict(name='jc303-win64-plugins.zip', browser_download_url='https://github.com/a', size=1, digest='sha256:' + 'ab' * 32),
        dict(name='jc303-win64-plugins.zip.sha256', browser_download_url='https://github.com/b', size=1)])]
    pa = vstpacks.pick_asset(vstpacks.BY_ID['jc303'], dg, 'windows')
    assert pa['sha256'] == 'ab' * 32 and pa['sha256_url'] == 'https://github.com/b'
    only_exe = [rel('1.3.4', ['surge-xt-win64-1.3.4-setup.exe'])]
    assert vstpacks.pick_asset(surge, only_exe, 'windows') is None              # installers are never picked
    jc = [rel('v0.12.3', ['jc303-win64-plugins.zip', 'jc303-macos-universal-plugins.zip', 'jc303-linux64-plugins.zip'])]
    for osn, want in (('windows', 'win64'), ('mac', 'macos'), ('linux', 'linux64')):
        assert want in vstpacks.pick_asset(vstpacks.BY_ID['jc303'], jc, osn)['name']
    assert 'dpf' not in vstpacks.BY_ID                                          # retired after an antivirus alert
    nightly_only = [rel('Nightly', ['dexed-1.0.1-win.zip'], pre=True)]
    assert vstpacks.pick_asset(vstpacks.BY_ID['dexed'], nightly_only, 'windows')          # falls back to pre-release
    assert vstpacks.pick_asset(vstpacks.BY_ID['jc303'], [rel('v1', ['source.tar.gz'])], 'windows') is None
    print('ok  asset picking')


def test_safe_unpack(tmp):
    z = os.path.join(tmp, 'a.zip')
    with zipfile.ZipFile(z, 'w') as f:
        f.writestr('JC303/JC303.vst3/Contents/x86_64-win/JC303.vst3', b'MZ')
        f.writestr('JC303/readme.txt', b'hi')
        f.writestr('../evil.txt', b'no')
        f.writestr('/abs.txt', b'no')
    out = os.path.join(tmp, 'zx')
    vstpacks.unpack(z, out)
    assert not os.path.exists(os.path.join(tmp, 'evil.txt')) and not os.path.exists('/abs.txt')
    b = vstpacks.find_bundles(out)
    assert len(b) == 1 and b[0].endswith('JC303/JC303.vst3'), b                      # nested inner .vst3 not double-counted
    t = os.path.join(tmp, 'a.tar.gz')
    with tarfile.open(t, 'w:gz') as f:
        for name, data in (('pk/Surge XT.vst3/Contents/x', b'1'), ('pk/Surge XT Effects.vst3/Contents/x', b'1')):
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            f.addfile(ti, io.BytesIO(data))
        ti = tarfile.TarInfo('pk/link')
        ti.type, ti.linkname = tarfile.SYMTYPE, '/etc/passwd'
        f.addfile(ti)
    out = os.path.join(tmp, 'tx')
    vstpacks.unpack(t, out)
    assert not os.path.lexists(os.path.join(out, 'pk', 'link'))
    picked = [x for x in vstpacks.find_bundles(out) if vstpacks.wanted(vstpacks.BY_ID['surge'], x)]
    assert [os.path.basename(x) for x in picked] == ['Surge XT.vst3'], picked
    # .deb = ar archive with data.tar.gz
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w:gz') as f:
        ti = tarfile.TarInfo('./usr/lib/vst3/Dexed.vst3/Contents/x')
        ti.size = 1
        f.addfile(ti, io.BytesIO(b'1'))
    payload = data.getvalue()
    deb = os.path.join(tmp, 'd.deb')
    with open(deb, 'wb') as f:
        f.write(b'!<arch>\n')
        for nm, blob in (('debian-binary', b'2.0\n'), ('data.tar.gz', payload)):
            f.write(f'{nm + "/":<16}{0:<12}{0:<6}{0:<6}{100644:<8}{len(blob):<10}`\n'.encode())
            f.write(blob + (b'\n' if len(blob) % 2 else b''))
    out = os.path.join(tmp, 'dx')
    vstpacks.unpack(deb, out)
    assert [os.path.basename(x) for x in vstpacks.find_bundles(out)] == ['Dexed.vst3']
    # only the pack's own plugins are written to disk - other plugins in the same download never touch the disk
    z2 = os.path.join(tmp, 'bundle.zip')
    with zipfile.ZipFile(z2, 'w') as f:
        f.writestr('Pk/JC303.vst3/Contents/x86_64-win/JC303.vst3', b'MZ' + bytes(20000))
        f.writestr('Pk/SoulForce.vst3/Contents/x86_64-win/SoulForce.vst3', b'MZ' + bytes(20000))
        f.writestr('Pk/readme.txt', b'x')
    out = os.path.join(tmp, 'kx')
    vstpacks.unpack(z2, out, keep=vstpacks.keeper(vstpacks.BY_ID['jc303']))
    written = [os.path.relpath(os.path.join(r, n), out) for r, d, fs in os.walk(out) for n in fs]
    assert written == [os.path.join('Pk', 'JC303.vst3', 'Contents', 'x86_64-win', 'JC303.vst3')], written
    assert vstpacks.complete(os.path.join(out, 'Pk', 'JC303.vst3'))
    os.makedirs(os.path.join(tmp, 'Hollow.vst3', 'Contents', 'x86_64-win'))
    assert not vstpacks.complete(os.path.join(tmp, 'Hollow.vst3'))             # binary removed by antivirus
    print('ok  safe unpacking (zip / tar / deb, traversal + symlinks blocked)')


def test_install_flow(tmp):
    """Full install with the network replaced by a local file."""
    src = os.path.join(tmp, 'jc303-win64-plugins.zip')
    with zipfile.ZipFile(src, 'w') as f:
        f.writestr('jc303/JC303.vst3', b'MZ' + bytes(20000))
        f.writestr('jc303/JC303.clap', b'x')
    plug = os.path.join(tmp, 'plugins')
    old = (vstpacks.PLUGIN_DIR, vstpacks.RECORD, vstpacks.resolve, vstpacks.download)
    try:
        vstpacks.PLUGIN_DIR, vstpacks.RECORD = plug, os.path.join(plug, '.packs.json')
        good = vstpacks.sha256_of(src)
        vstpacks.download = lambda url, dst, progress=None, expected=0: shutil.copy(src, dst)
        vstpacks.resolve = lambda pid, osname=None: dict(url='https://github.com/x', name='jc303-win64-plugins.zip', size=1, version='v9',
                                                         sha256='0' * 64)
        try:
            vstpacks.install('jc303', log=lambda *a: None)
            raise AssertionError('a file with the wrong checksum was installed')
        except RuntimeError as e:
            assert 'checksum' in str(e)
        assert not os.path.exists(os.path.join(plug, 'JC303.vst3'))
        vstpacks.resolve = lambda pid, osname=None: dict(url='https://github.com/x', name='jc303-win64-plugins.zip', size=1, version='v9',
                                                         sha256=good)
        r = vstpacks.install('jc303', log=lambda *a: None)
        assert not os.path.exists(os.path.join(plug, 'JC303.clap'))
        assert r['ok'] and os.path.isfile(os.path.join(plug, 'JC303.vst3')), r
        assert json.load(open(vstpacks.RECORD))['jc303']['version'] == 'v9'
        vstpacks.remove('jc303')
        assert not os.path.exists(os.path.join(plug, 'JC303.vst3'))
    finally:
        vstpacks.PLUGIN_DIR, vstpacks.RECORD, vstpacks.resolve, vstpacks.download = old
    assert not vstpacks._host_ok('http://github.com/a') and not vstpacks._host_ok('https://evil.example/a.zip')
    print('ok  install / record / remove')


def test_rigs(tmp):
    for pid, p in vstrigs.PATCHES.items():
        assert p['player'] in vstrigs.PLAYERS, pid
        assert set(p.get('required', [])) <= {k.split('|')[0] for k in p['params']}, pid
    for inst, cands in vstrigs.ROLE_PATCHES.items():
        assert all(c in vstrigs.PATCHES for c in cands), inst
    fake = lambda names: [dict(name=n, path=os.path.join(tmp, n + '.vst3'), format='vst3') for n in names]
    every = fake(['Surge XT', 'Surge XT Effects', 'TAL-NoiseMaker', 'Dexed', 'JC303', 'Nekobi', 'Kars'])
    pick = lambda inst, style: vstrigs.choose(inst, style, STYLES[style]['category'], every, [])
    assert pick('acid', 'acid_house')[1] == 'jc303.acid'
    assert pick('sawbass', 'synthwave')[1] == 'tal.saw_bass'                    # 80s styles -> TAL
    assert pick('supersaw', 'trance')[1] == 'surge.supersaw'                    # trance -> Surge
    assert pick('epiano', 'city_pop')[1] == 'dexed.epiano'                      # FM keys work in Classic styles
    assert pick('piano', 'jazz') is None and pick('strings', 'orchestral') is None
    only_303 = fake(['Nekobi'])
    assert vstrigs.choose('sawbass', 'synthwave', 'Electronic', only_303, []) is None   # no 303 bass in synthwave
    assert vstrigs.choose('sawbass', 'techno', 'Electronic', only_303, [])[1] == 'nekobi.bass'
    mine = [dict(id='u1', name='Serum supersaw', path=os.path.join(tmp, 'Serum.vst3'), ok=True),
            dict(id='u2', name='Vital lead', path=os.path.join(tmp, 'Vital.vst3'), ok=True),
            dict(id='a1', name='Surge XT · Supersaw', path='x', ok=True, auto=True)]
    assert vstrigs.choose('supersaw', 'trance', 'Electronic', every, mine)[1] == 'u1'   # your named sound beats the rig
    assert vstrigs.choose('leadsaw', 'synthwave', 'Electronic', every, mine)[1] == 'u2'
    assert vstrigs.choose('sawbass', 'synthwave', 'Electronic', every, mine)[1] == 'tal.saw_bass'
    assert vstrigs.choose('epiano', 'lofi', 'Electronic', every, [dict(id='x', name='Keyscape Rhodes', path='k', ok=True)])[1] == 'x'
    bbc = [dict(id='bbc1', name='BBC strings legato', path=os.path.join(tmp, 'BBC_Symphony_Orchestra__64_Bit_.vst3'), ok=True)]
    assert vstrigs.choose('strings', 'orchestral', 'Orchestral', every, bbc)[1] == 'bbc1'
    assert vstrigs.choose('horn', 'orchestral', 'Orchestral', every, bbc) is None
    old_broken = vsthost.broken
    vsthost.broken = lambda: {os.path.join(tmp, 'JC303.vst3'): 'Unable to scan plugin'}
    assert pick('acid', 'acid_house')[1] == 'nekobi.acid'                       # a plugin that won't load is skipped
    vsthost.broken = old_broken
    assert vstrigs.recipe_for('tal.saw_bass', -0.12)['params']['Filter Cutoff'] < vstrigs.PATCHES['tal.saw_bass']['params']['Filter Cutoff']
    # end to end through compose (plugin files are fakes: nothing is rendered here)
    old = (vsthost.SOUNDS, vsthost.available, vstrigs.plugins_on_disk)
    try:
        vsthost.SOUNDS = os.path.join(tmp, 'sounds')
        vsthost.available = lambda: True
        vstrigs.plugins_on_disk = lambda refresh=False: every
        song = compose(Options(style='acid_house', seed=3, vst_rig=True, variety=0))
        bass = next(t for t in song['st']['tracks'] if t['layer'] == 'bass')
        assert bass['inst'] == 'vst:auto_jc303_acid' and bass['fallback'] == 'acid', bass
        song = compose(Options(style='acid_house', seed=3, vst_rig=True, variety=0, instruments={'bass': 'reese'}))
        assert next(t for t in song['st']['tracks'] if t['layer'] == 'bass')['inst'] == 'reese'   # your pick wins
        plain = compose(Options(style='acid_house', seed=3, variety=0))
        assert not any(t['inst'].startswith('vst:') for t in plain['st']['tracks'])
        for s in STYLES:                                                      # every style composes with the rig on
            compose(Options(style=s, seed=5, vst_rig=True))
    finally:
        vsthost.SOUNDS, vsthost.available, vstrigs.plugins_on_disk = old
    print('ok  genre rigs')


def main():
    tmp = tempfile.mkdtemp()
    try:
        test_pick_asset()
        test_safe_unpack(tmp)
        test_install_flow(tmp)
        test_rigs(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('all good')


if __name__ == '__main__':
    main()
