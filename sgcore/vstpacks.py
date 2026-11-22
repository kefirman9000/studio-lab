"""Auto-download free, open-source VST3 / AU instruments that the genre rigs (sgcore.vstrigs) know how to play.

Each pack lives on GitHub. At install time we ask the GitHub API for the newest release, pick the asset for this
OS/CPU, download it and copy the plugin bundles into Studio Lab's own `plugins` folder (kept across updates and
scanned automatically). Archives (zip / tar / deb / dmg / pkg) are unpacked without running anything. When a project
only ships an installer program (some Windows builds), we start the official installer and wait for it.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile

from . import updater

ROOT = updater.ROOT
PLUGIN_DIR = os.path.join(ROOT, 'plugins')
RECORD = os.path.join(PLUGIN_DIR, '.packs.json')
MAX_BYTES = 600 * 1024 * 1024
ALLOWED_HOSTS = ('github.com', 'api.github.com', 'objects.githubusercontent.com', 'release-assets.githubusercontent.com',
                 'github-releases.githubusercontent.com', 'codeload.github.com')

# asset patterns are tried in order; the first one that matches an asset of the newest usable release wins.
PACKS = [
    dict(id='surge', name='Surge XT', maker='Surge Synth Team', license='GPL-3.0', repo='surge-synthesizer/releases-xt',
         page='https://surge-synthesizer.github.io/downloads', size='~60 MB',
         plays='supersaws, pads, reese & saw basses, leads, plucks (trance, big room, future bass, house, DnB)',
         bundles=[r'^surge xt$'],
         assets={'windows': [r'win(64|-x64).*(pluginsonly|portable).*\.zip$', r'win(64|-x64).*\.zip$'],
                 'mac': [r'mac.*\.dmg$', r'mac.*\.zip$'],
                 'linux': [r'linux.*{arch}.*\.tar\.gz$', r'linux.*{arch}.*\.deb$', r'{arch}.*\.deb$']}),
    dict(id='dexed', name='Dexed', maker='Digital Suburban', license='GPL-3.0', repo='asb2m10/dexed',
         page='https://asb2m10.github.io/dexed/', size='~10 MB',
         plays='DX7 FM: electric piano, clav, marimba, bells, steel drum, FM bass (city pop, lo-fi, funk, R&B, 80s)',
         bundles=[r'^dexed$'],
         assets={'windows': [r'win.*\.zip$'], 'mac': [r'mac.*\.(dmg|zip|pkg)$'],
                 'linux': [r'linux.*\.(zip|tar\.gz|tar\.xz)$']}),
    dict(id='jc303', name='JC303', maker='midilab', license='GPL-3.0', repo='midilab/jc303', page='https://midilab.co/jc303/',
         size='~10 MB', plays='TB-303 acid bass (acid house, techno, psytrance)', bundles=[r'^jc303$'],
         assets={'windows': [r'win.*\.zip$'], 'mac': [r'mac.*\.zip$'], 'linux': [r'linux.*{arch}.*\.zip$', r'linux.*\.zip$']}),
    dict(id='ripplerx', name='RipplerX', maker='tiagolr', license='GPL-3.0', repo='tiagolr/ripplerx',
         page='https://github.com/tiagolr/ripplerx', size='~7 MB',
         plays='physically modelled marimba, vibes, kalimba, harp, music box, bells, tubular bells and gongs '
               '(afro, latin, soca, amapiano, ambient, lullaby, orchestral colours)',
         bundles=[r'^ripplerx$'],
         assets={'windows': [r'ripplerx-win.*\.zip$'], 'mac': [r'ripplerx-mac.*\.zip$'], 'linux': [r'ripplerx-linux.*\.zip$']}),
    dict(id='dragonfly', name='Dragonfly Reverb', maker='Michael Willis', license='GPL-3.0', repo='michaelwillis/dragonfly-reverb',
         page='https://michaelwillis.github.io/dragonfly-reverb/', size='~10 MB', kind='effect',
         plays='hall, plate and room reverbs - each genre\'s reverb runs through the right one (hall for orchestral & trance, '
               'plate for pop & soul, room for rock, funk & jazz)',
         bundles=[r'^dragonfly ?hall ?reverb$', r'^dragonfly ?room ?reverb$', r'^dragonfly ?plate ?reverb$'],
         assets={'windows': [r'win64.*\.zip$', r'windows.*64.*\.zip$'], 'mac': [r'mac.*\.zip$'],
                 'linux': [r'linux.*{arch}.*\.zip$', r'linux.*\.zip$']}),
    dict(id='airwindows', name='Airwindows Consolidated', maker='Chris Johnson (Airwindows) & Paul Walker', license='MIT',
         repo='baconpaul/airwin2rack', page='https://www.airwindows.com/consolidated/', size='~30 MB', kind='effect',
         plays='500+ Airwindows effects in one plugin - tape (ToTape), console, saturation, lo-fi, reverbs and more. Pick it as a '
               'part effect in Sound (e.g. tape or console warmth on a boom-bap loop, saturation on a bass)',
         bundles=[r'^airwindows ?consolidated$'],
         assets={'windows': [r'airwindows.*win.*\.zip$', r'win.*(x64|64).*\.zip$', r'win.*\.zip$'],
                 'mac': [r'mac.*\.(zip|dmg)$'], 'linux': [r'linux.*{arch}.*\.zip$', r'linux.*\.zip$']}),
    dict(id='obxf', name='OB-Xf', maker='Surge Synth Team', license='GPL-3.0', repo='surge-synthesizer/OB-Xf',
         page='https://surge-synth-team.org/ob-xf/', size='~25 MB', tags=r'^v\d',
         plays='Oberheim-style analog poly: brass stabs, big warm pads, 80s chords, fat unison leads and basses '
               '(synthwave, synthpop, italo, 80s pop, trance, progressive house, Y2K anthem trance)',
         bundles=[r'^ob ?xf$', r'^obxf$'],
         assets={'windows': [r'^ob-xf-windows-v?\d.*\.zip$'], 'mac': [r'^ob-xf-macos-.*\.dmg$'],
                 'linux': [r'^ob-xf-linux-v?\d.*\.zip$']}),
]
BY_ID = {p['id']: p for p in PACKS}
# packs no longer offered (no genre used them); kept only for the tests and so an
# existing install is recognised and can be removed
_UNUSED_PACKS = [
    dict(id='sixsines', name='Six Sines', maker='BaconPaul (Surge Synth Team)', license='GPL-3.0', repo='baconpaul/six-sines',
         page='https://github.com/baconpaul/six-sines/releases', size='~15 MB',
         plays='6-operator FM: bells, e-pianos, FM basses, glassy pads, metallic leads and FM drums',
         bundles=[r'^six sines$', r'^sixsines$'],
         assets={'windows': [r'win(dows)?.*(x64|64).*\.zip$', r'win(dows)?.*\.zip$'], 'mac': [r'mac.*\.(dmg|zip|pkg)$'],
                 'linux': [r'linux.*{arch}.*\.(zip|tar\.gz)$', r'linux.*\.(zip|tar\.gz)$']}),
    dict(id='monique', name='Monique', maker='Surge Synth Team', license='GPL-3.0', repo='surge-synthesizer/monique-monosynth',
         page='https://github.com/surge-synthesizer/monique-monosynth/releases', size='~15 MB',
         plays='morphing mono synth: fat basses, sequenced leads, acid-ish lines',
         bundles=[r'^monique$'],
         assets={'windows': [r'win.*\.zip$'], 'mac': [r'mac.*\.(dmg|zip)$'], 'linux': [r'linux.*{arch}.*\.(zip|tar\.gz)$', r'linux.*\.(zip|tar\.gz)$']}),
    dict(id='odin2', name='Odin 2', maker='TheWaveWarden', license='GPL-3.0', repo='TheWaveWarden/odin2',
         page='https://thewavewarden.com/odin2', size='~20 MB',
         plays='hybrid synth: growls, wobble and reese basses, analog leads, evolving pads',
         bundles=[r'^odin ?2$'],
         assets={'windows': [r'win.*\.zip$'], 'mac': [r'mac.*\.(zip|dmg)$'], 'linux': [r'linux.*\.(zip|tar\.gz)$']}),
]


# instruments the rigs can use but that can't be auto-downloaded (licence, account or installer app required)
KNOWN = [
    dict(id='tal', name='TAL-NoiseMaker', url='https://tal-software.com/products/tal-noisemaker',
         plays='80s / Juno-style analog basses, pads, leads, brass stabs (synthwave, synthpop, electro, house)'),
    dict(id='bbcso', name='BBC Symphony Orchestra Discover', url='https://www.spitfireaudio.com/bbc-symphony-orchestra-discover',
         plays='real orchestra - Sounds & instruments → Orchestra plugin → Detect my instruments: open it once, load each section, done'),
    dict(id='labs', name='Spitfire LABS', url='https://labs.spitfireaudio.com',
         plays='sampled pianos, strings, choir - save a sound (e.g. "LABS soft piano") and matching parts use it'),
    dict(id='chowtape', name='CHOW Tape Model', url='https://chowdsp.com/products.html',
         plays='analog tape saturation - pick it as an effect on any part (only offered with an installer, so install it yourself)'),
    dict(id='vital', name='Vital', url='https://vital.audio',
         plays='wavetable synth (free plan): modern pads, plucks, basses, future bass and melodic dubstep leads - free account needed'),
    dict(id='tyrelln6', name='TyrellN6', url='https://u-he.com/products/tyrelln6/',
         plays='Juno-style analog poly (free): warm chillwave / synthwave pads, plucks and basses'),
    dict(id='vaporizer2', name='Vaporizer2', url='https://www.vast-dynamics.com/?q=products',
         plays='free hybrid wavetable synth (open source, GPL): modern trance and progressive leads, plucks, supersaw pads and '
               'growl / wobble basses - only offered as a 400 MB installer, so install it yourself, then save a sound in it'),
    dict(id='cardinal', name='Cardinal (modular)', url='https://cardinal.kx.studio/',
         plays='free open-source modular synth rack: evolving modular pads, generative sequences and drones for ambient, IDM and '
               'spacious breaks electronica - the download is over 1 GB, so install it yourself, then save a sound in it'),
    dict(id='geonkick', name='Geonkick', url='https://geonkick.org/',
         plays='free percussion synth: designed kicks, 808s, snares and claps for techno, trance, house and dubstep - '
               'Windows only has an installer, so install it yourself, then save a kit sound in it'),
    dict(id='drumgizmo', name='DrumGizmo', url='https://drumgizmo.org/',
         plays='free multi-mic acoustic drum sampler with big real kits for rock, metal and indie - install it and a kit '
               'yourself (Studio Lab already plays its own real acoustic kits without it)'),
    dict(id='sfizz', name='sfizz (SFZ sampler)', url='https://sfz.tools/sfizz/',
         plays='plays free SFZ instrument libraries (free guitars, drums, pianos) - Studio Lab already plays the Salamander grand '
               'and the other real libraries itself; its '
               'installer is an app, so install it yourself, then save a sound in it'),
    dict(id='byod', name='BYOD (Build Your Own Distortion)', url='https://chowdsp.com/products.html',
         plays='guitar distortion - pick it as an effect on guitar parts (only offered with an installer, so install it yourself)'),
]


# ----------------------------------------------------------------------------- platform
def host_os():
    return 'windows' if sys.platform.startswith('win') else ('mac' if sys.platform == 'darwin' else 'linux')


def _arch_re():
    m = platform.machine().lower()
    return r'(arm64|aarch64)' if m in ('arm64', 'aarch64') else r'(x86_64|x86-64|amd64|x64|linux64)'


# ----------------------------------------------------------------------------- GitHub release lookup
def _get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'StudioLab', 'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def pick_asset(pack, releases, osname=None):
    """From a GitHub releases list (newest first) choose the asset for this OS. Stable releases win over pre-releases."""
    osname = osname or host_os()
    pats = [re.compile(p.replace('{arch}', _arch_re()), re.I) for p in pack['assets'].get(osname, [])]
    rels = [r for r in releases if not r.get('draft') and re.search(pack.get('tags', ''), r.get('tag_name', ''))]   # 'tags': numbered releases only, no nightlies
    for stable_only in (True, False):
        for rel in rels:
            if stable_only and rel.get('prerelease'):
                continue
            names = [a for a in rel.get('assets', []) if not a['name'].lower().endswith(('.sha256', '.sig', '.asc', '.txt'))]
            sums = {a['name'][:-7]: a['browser_download_url'] for a in rel.get('assets', []) if a['name'].lower().endswith('.sha256')}
            arm = platform.machine().lower() in ('arm64', 'aarch64')
            names = [a for a in names if arm or not re.search(r'arm|aarch', a['name'], re.I)]   # never an ARM build on x64
            for pat in pats:
                for a in names:
                    if pat.search(a['name']):
                        dg = a.get('digest') or ''
                        return dict(url=a['browser_download_url'], name=a['name'], size=a.get('size', 0),
                                    version=rel.get('tag_name', ''), sha256=dg[7:].lower() if dg.startswith('sha256:') else None,
                                    sha256_url=sums.get(a['name']))
    return None


def resolve(pack_id, osname=None):
    pack = BY_ID[pack_id]
    rels = _get_json(f"https://api.github.com/repos/{pack['repo']}/releases?per_page=10")
    return pick_asset(pack, rels, osname)


# ----------------------------------------------------------------------------- download
def _host_ok(url):
    u = urllib.parse.urlparse(url)
    return u.scheme == 'https' and (u.hostname or '') in ALLOWED_HOSTS


def expected_sha256(asset):
    """The checksum GitHub publishes for the file, or the project's own .sha256 file next to it."""
    if asset.get('sha256'):
        return asset['sha256']
    if asset.get('sha256_url') and _host_ok(asset['sha256_url']):
        try:
            req = urllib.request.Request(asset['sha256_url'], headers={'User-Agent': 'StudioLab'})
            with urllib.request.urlopen(req, timeout=20) as r:
                m = re.search(r'\b[0-9a-fA-F]{64}\b', r.read(4096).decode('utf-8', 'replace'))
                return m.group(0).lower() if m else None
        except Exception:
            return None
    return None


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def download(url, dst, progress=None, expected=0, limit=None):
    if not _host_ok(url):
        raise RuntimeError('refusing to download from ' + url)
    req = urllib.request.Request(url, headers={'User-Agent': 'StudioLab'})
    with urllib.request.urlopen(req, timeout=60) as r, open(dst, 'wb') as f:
        if not _host_ok(r.geturl()):
            raise RuntimeError('download was redirected to an unexpected site')
        total = int(r.headers.get('Content-Length') or expected or 0)
        got = 0
        while True:
            b = r.read(1 << 16)
            if not b:
                break
            got += len(b)
            if got > (limit or MAX_BYTES):
                raise RuntimeError('download is unexpectedly large - stopped')
            f.write(b)
            if progress and total:
                progress(min(0.99, got / total))
    return dst


# ----------------------------------------------------------------------------- safe extraction
def _inside(base, target):
    base, target = os.path.realpath(base), os.path.realpath(target)
    return os.path.commonpath([base, target]) == base


ARCHIVES = ('.zip', '.tar.gz', '.tgz', '.tar.xz', '.tar.bz2', '.tar', '.deb', '.dmg', '.pkg')


def keeper(pack):
    """Archive-member filter: only the pack's own plugin bundles (and archives that may contain them) are written to
    disk - other plugins shipped in the same download are never unpacked."""
    exts = ('.vst3', '.component')

    def keep(name):
        parts = [x for x in name.replace('\\', '/').split('/') if x and x != '.']
        for seg in parts:
            if seg.lower().endswith(exts):
                return wanted(pack, seg)
        return bool(parts) and parts[-1].lower().endswith(ARCHIVES)
    return keep


def extract_zip(path, out, keep=None):
    with zipfile.ZipFile(path) as z:
        for m in z.infolist():
            name = m.filename.replace('\\', '/')
            if name.startswith('/') or '..' in name.split('/'):
                continue
            if keep and not name.endswith('/') and not keep(name):
                continue
            mode = (m.external_attr >> 16) & 0o170000
            dst = os.path.join(out, *name.split('/'))
            if not _inside(out, dst):
                continue
            if mode == 0o120000:                               # symlink inside a mac bundle
                link = z.read(m).decode('utf-8', 'replace')
                if link.startswith('/') or not _inside(out, os.path.join(os.path.dirname(dst), link)):
                    continue
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                try:
                    os.symlink(link, dst)
                except OSError:
                    pass
                continue
            if name.endswith('/'):
                os.makedirs(dst, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with z.open(m) as src, open(dst, 'wb') as f:
                shutil.copyfileobj(src, f)
            perm = (m.external_attr >> 16) & 0o777
            if perm and not sys.platform.startswith('win'):
                os.chmod(dst, perm | 0o600)


def extract_tar(path, out, keep=None):
    with tarfile.open(path) as t:
        safe = []
        for m in t.getmembers():
            if m.name.startswith('/') or '..' in m.name.split('/') or m.isdev():
                continue
            if keep and not m.isdir() and not keep(m.name):
                continue
            if (m.issym() or m.islnk()) and (m.linkname.startswith('/') or
                                             not _inside(out, os.path.join(out, os.path.dirname(m.name), m.linkname))):
                continue
            if not _inside(out, os.path.join(out, m.name)):
                continue
            safe.append(m)
        if hasattr(tarfile, 'data_filter'):
            t.extractall(out, members=safe, filter='data')
        else:
            t.extractall(out, members=safe)


def extract_deb(path, out, keep=None):
    """.deb = ar archive holding data.tar.*; parsed here so no dpkg is needed."""
    with open(path, 'rb') as f:
        if f.read(8) != b'!<arch>\n':
            raise RuntimeError('not a .deb file')
        while True:
            hdr = f.read(60)
            if len(hdr) < 60:
                break
            name = hdr[:16].decode().strip().rstrip('/')
            size = int(hdr[48:58].decode().strip())
            data = f.read(size)
            if size % 2:
                f.read(1)
            if name.startswith('data.tar'):
                tmp = os.path.join(out, '_' + name)
                with open(tmp, 'wb') as g:
                    g.write(data)
                extract_tar(tmp, out, keep)
                os.remove(tmp)
                return
    raise RuntimeError('no data in .deb')


def _extract_dmg(path, out, log):
    mnt = tempfile.mkdtemp(prefix='sl_dmg_')
    subprocess.run(['hdiutil', 'attach', '-nobrowse', '-readonly', '-noautoopen', '-mountpoint', mnt, path],
                   check=True, capture_output=True, input=b'Y\n')
    try:
        for name in os.listdir(mnt):
            src = os.path.join(mnt, name)
            if name.lower().endswith(('.vst3', '.component')):
                shutil.copytree(src, os.path.join(out, name), symlinks=True)
            elif name.lower().endswith('.pkg'):
                _expand_pkg(src, os.path.join(out, name + '_x'), log)
            elif os.path.isdir(src) and not os.path.islink(src) and name.lower() not in ('applications',):
                shutil.copytree(src, os.path.join(out, name), symlinks=True, ignore_dangling_symlinks=True)
    finally:
        subprocess.run(['hdiutil', 'detach', mnt, '-quiet'], capture_output=True)


def _expand_pkg(path, out, log):
    """Unpack a macOS installer package without installing it (no admin password needed)."""
    subprocess.run(['pkgutil', '--expand-full', path, out], check=True, capture_output=True)


def unpack(path, out, log=print, depth=0, keep=None):
    low = path.lower()
    os.makedirs(out, exist_ok=True)
    if low.endswith('.zip'):
        extract_zip(path, out, keep)
    elif low.endswith(('.tar.gz', '.tgz', '.tar.xz', '.tar.bz2', '.tar')):
        extract_tar(path, out, keep)
    elif low.endswith('.deb'):
        extract_deb(path, out, keep)
    elif low.endswith('.dmg') and sys.platform == 'darwin':
        _extract_dmg(path, out, log)
    elif low.endswith('.pkg') and sys.platform == 'darwin':
        _expand_pkg(path, os.path.join(out, 'pkg'), log)
    else:
        raise RuntimeError(f'cannot unpack {os.path.basename(path)} on this computer')
    if depth < 2 and not find_bundles(out):                    # archive inside the archive (e.g. zip -> dmg)
        for root, dirs, files in os.walk(out):
            for fn in files:
                if fn.lower().endswith(('.zip', '.tar.gz', '.tar.xz', '.deb', '.dmg', '.pkg')):
                    try:
                        unpack(os.path.join(root, fn), os.path.join(root, fn + '_x'), log, depth + 1, keep)
                    except Exception as e:
                        log(f'   (skipped {fn}: {e})')


def find_bundles(folder):
    """Plugin bundles (.vst3 folder/file, .component on Mac) anywhere under folder; nested bundles are not descended."""
    out = []
    exts = ('.vst3', '.component') if sys.platform == 'darwin' else ('.vst3',)
    for root, dirs, files in os.walk(folder):
        for name in list(dirs) + files:
            if name.lower().endswith(exts):
                out.append(os.path.join(root, name))
        dirs[:] = [d for d in dirs if not d.lower().endswith(exts)]
    return out


def complete(bundle):
    """A plugin bundle must actually contain its program file (antivirus software may have removed it)."""
    if os.path.isfile(bundle):
        return os.path.getsize(bundle) > 10_000
    for root, dirs, files in os.walk(bundle):
        if any(os.path.getsize(os.path.join(root, f)) > 10_000 for f in files if not os.path.islink(os.path.join(root, f))):
            return True
    return False


def _norm(name):
    base = os.path.splitext(os.path.basename(name))[0].lower()
    base = re.sub(r'[\s_\-]*\(?(64|32)[\s_\-]*bit\)?', '', base)
    return re.sub(r'[\s_\-]+', ' ', base).strip()


def wanted(pack, path):
    return any(re.search(p, _norm(path)) for p in pack['bundles'])


# ----------------------------------------------------------------------------- status / install
def _record():
    try:
        with open(RECORD) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_record(d):
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    with open(RECORD, 'w') as f:
        json.dump(d, f, indent=2)


def installed_paths(pack, plugins=None):
    """Where this pack's plugins are on this computer (our folder or any system plugin folder)."""
    if plugins is None:
        from .vsthost import find_plugins
        plugins = find_plugins()
    return [p['path'] for p in plugins if wanted(pack, p['path'])]


def status():
    from .vsthost import find_plugins
    plugins = find_plugins()
    rec = _record()
    out = []
    for p in PACKS:
        paths = installed_paths(p, plugins)
        need = len(p['bundles'])
        found = {b for b in p['bundles'] for x in paths if re.search(b, _norm(x))}
        out.append(dict(id=p['id'], name=p['name'], maker=p['maker'], license=p['license'], plays=p['plays'], page=p['page'],
                        size=p['size'], installed=len(found) >= need, partial=0 < len(found) < need,
                        version=rec.get(p['id'], {}).get('version'), paths=paths, checks=rec.get(p['id'], {}).get('checks')))
    for pid, r in rec.items():
        if pid not in BY_ID and not r.get('app') and any(os.path.exists(f) for f in r.get('files', [])):
            out.append(dict(id=pid, name=', '.join(os.path.splitext(os.path.basename(f))[0] for f in r.get('files', [])),
                            maker='', license='', size='', page='', installed=True, partial=False, version=r.get('version'),
                            retired=True, paths=r.get('files', []),
                            plays='no longer offered for download - still used while installed; remove it if you prefer'))
    known = []
    for k in KNOWN:
        from .vstrigs import PLAYERS
        hit = [x['path'] for x in plugins if PLAYERS[k['id']]['match'](x['path'])]
        known.append(dict(k, installed=bool(hit), paths=hit, auto=installer_available(k['id'])))
    from .vsthost import broken
    bad = [dict(name=os.path.splitext(os.path.basename(p))[0], path=p, why=w) for p, w in broken().items()]
    return dict(packs=out, known=known, broken=bad, os=host_os(), folder=PLUGIN_DIR)


def install(pack_id, log=print, progress=None, vt_key=None, require_vt=False):
    if pack_id not in BY_ID:
        raise RuntimeError('unknown pack ' + pack_id)
    pack = BY_ID[pack_id]
    log(f"Looking up the latest {pack['name']} release ...")
    try:
        asset = resolve(pack_id)
    except Exception as e:
        hint = ' (GitHub limits how often it can be asked - try again in an hour)' if '403' in str(e) or '429' in str(e) else ''
        raise RuntimeError(f"couldn't reach GitHub: {e}{hint}. You can also download it from {pack['page']}")
    if not asset:
        raise RuntimeError(f"no {host_os()} download found for {pack['name']} - get it from {pack['page']}")
    if asset['name'].lower().endswith(('.exe', '.msi')):
        raise RuntimeError(f"{pack['name']} is only offered with an installer for this computer - "
                           f"install it yourself from {pack['page']} and Studio Lab will find it")
    log(f"Downloading {asset['name']} ({asset['version']}, {asset['size'] / 1e6:.0f} MB) ...")
    work = tempfile.mkdtemp(prefix='sl_pack_')
    try:
        fn = os.path.join(work, re.sub(r'[^A-Za-z0-9._-]', '_', asset['name']))
        download(asset['url'], fn, progress, asset.get('size', 0))
        from . import safety
        want = expected_sha256(asset)
        digest = sha256_of(fn)
        checks = dict(source=f"official release of {pack['repo']} on GitHub", open_source=pack['license'])
        if want:
            if digest != want:
                raise RuntimeError(f"{asset['name']} failed its checksum check (it isn't the file the project published) - not installed")
            log('   checksum verified (SHA-256)')
            checks['checksum'] = 'matches the published SHA-256'
        else:
            log('   (the project publishes no checksum for this file)')
            checks['checksum'] = 'none published'
        d = safety.defender_scan(fn)                         # Windows: Microsoft Defender scan of the download
        log('   ' + d['detail'])
        if d['ran'] and not d['clean']:
            raise RuntimeError(d['detail'] + ' - not installed')
        checks['defender'] = d['detail']
        v = safety.vt_check(fn, digest, vt_key, log)        # VirusTotal: ~70 engines, installs only at 0 detections
        log('   ' + v['detail'])
        if v.get('ran') and not v.get('clean'):
            who = (' (' + ', '.join(v.get('flagged_by') or []) + ')') if v.get('flagged_by') else ''
            raise RuntimeError(f"VirusTotal: {v['flagged']} of {v['engines']} antivirus engines flagged this download{who} - not installed. "
                               f"Details: {v['link']}")
        if require_vt and not v.get('ran'):
            raise RuntimeError('no VirusTotal result (' + v['detail'] + ') and you asked for one - not installed')
        checks['virustotal'] = v['detail'] + (f" · {v['link']}" if v.get('link') else '')
        os.makedirs(PLUGIN_DIR, exist_ok=True)
        copied = []
        log('Unpacking ...')
        ex = os.path.join(work, 'x')
        unpack(fn, ex, log, keep=keeper(pack))
        found = [b for b in find_bundles(ex) if wanted(pack, b)]
        gone = [b for b in found if not complete(b)]
        if gone:
            raise RuntimeError(', '.join(os.path.basename(b) for b in gone) + ' is incomplete after unpacking '
                               '(your antivirus may have removed part of it) - not installed')
        if not found:
            raise RuntimeError(f"{pack['name']} is only offered with an installer for this computer - "
                               f"install it yourself from {pack['page']} and Studio Lab will find it")
        for b in found:                                      # the unpacked plugin files themselves
            d = safety.defender_scan(b)
            if d['ran'] and not d['clean']:
                raise RuntimeError(f"{os.path.basename(b)}: {d['detail']} - not installed")
            for r in safety.scan_binaries(b, vt_key):
                if not r['clean'] and r['engines']:
                    raise RuntimeError(f"VirusTotal: {r['flagged']}/{r['engines']} engines flag {r['file']} - not installed ({r['link']})")
        for b in found:
            dst = os.path.join(PLUGIN_DIR, os.path.basename(b))
            if os.path.isdir(dst) and not os.path.islink(dst):
                shutil.rmtree(dst)
            elif os.path.exists(dst):
                os.remove(dst)
            if os.path.isdir(b):
                shutil.copytree(b, dst, symlinks=True)
            else:
                shutil.copy2(b, dst)
            copied.append(dst)
            log('   installed ' + os.path.basename(dst))
        rec = _record()
        rec[pack_id] = dict(version=asset['version'], asset=asset['name'], files=copied, installed=int(time.time()),
                            sha256=digest, checks=checks)
        _save_record(rec)
        log(f"{pack['name']} is ready.")
        return dict(ok=True, id=pack_id, version=asset['version'], files=copied)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def recorded():
    """Ids of packs this app installed (including retired ones, so they can still be removed)."""
    return list(_record())


def remove(pack_id):
    rec = _record()
    for f in rec.get(pack_id, {}).get('files', []):
        if _inside(PLUGIN_DIR, f) and os.path.exists(f):
            shutil.rmtree(f) if os.path.isdir(f) and not os.path.islink(f) else os.remove(f)
    rec.pop(pack_id, None)
    _save_record(rec)
    return dict(ok=True)


def install_many(ids, log=print, progress=None, vt_key=None, require_vt=False):
    res, failed = [], []
    ids = [i for i in ids if i in BY_ID or i in INST_BY_ID]
    for n, i in enumerate(ids):
        try:
            fn = install if i in BY_ID else install_app
            res.append(fn(i, log, (lambda p, n=n: progress((n + p) / len(ids))) if progress else None,
                          vt_key=vt_key, require_vt=require_vt))
        except Exception as e:
            log(f"!! {(BY_ID.get(i) or INST_BY_ID[i])['name']}: {e}")
            failed.append(dict(id=i, error=str(e)))
    return dict(ok=not failed, installed=[r['id'] for r in res], failed=failed)


# ----------------------------------------------------------------------------- (2.13.3) official installers
# Free, open-source plugins that are only published as an installer app (or a download too big to unpack here): the
# official installer is downloaded from the project's GitHub release, checked exactly like the packs (published
# SHA-256, Microsoft Defender, VirusTotal when you have a key) and then run - silently when it is a standard Inno Setup
# or NSIS installer, otherwise its own setup window opens. Windows asks for permission (UAC) first; on a Mac the
# system asks for your password. Plugins that need an account (Vital, LABS, BBC SO ...) can't be installed this way.
INSTALLER_MAX = 1600 * 1024 * 1024
INSTALLERS = [
    dict(id='cardinal', name='Cardinal (modular)', repo='DISTRHO/Cardinal', license='GPL-3.0', page='https://cardinal.kx.studio/',
         assets={'windows': [r'^cardinal-win64-.*-installer\.exe$'], 'mac': [r'^cardinal-macos-universal-.*\.pkg$']}),
    dict(id='geonkick', name='Geonkick', repo='Geonkick-Synthesizer/geonkick', license='GPL-3.0', page='https://geonkick.org/',
         assets={'windows': [r'^geonkickwindowsinstaller-.*x86_64.*\.exe$']}),
    dict(id='vaporizer2', name='Vaporizer2', repo='VASTDynamics/Vaporizer2', license='GPL-3.0',
         page='https://www.vast-dynamics.com/?q=products',
         assets={'windows': [r'^vaporizer2_installer_win_.*\.zip$'], 'mac': [r'^vaporizer2_installer_osx64_.*\.zip$']}),
    dict(id='chowtape', name='CHOW Tape Model', repo='jatinchowdhury18/AnalogTapeModel', license='GPL-3.0',
         page='https://chowdsp.com/products.html',
         assets={'windows': [r'win.*64.*\.exe$', r'win.*\.exe$'], 'mac': [r'mac.*\.pkg$', r'mac.*\.dmg$']}),
    dict(id='byod', name='BYOD (Build Your Own Distortion)', repo='Chowdhury-DSP/BYOD', license='GPL-3.0',
         page='https://chowdsp.com/products.html',
         assets={'windows': [r'win.*64.*\.exe$', r'win.*\.exe$'], 'mac': [r'mac.*\.pkg$', r'mac.*\.dmg$']}),
]
INST_BY_ID = {p['id']: p for p in INSTALLERS}


def installer_kind(path):
    """'inno', 'nsis' or None, read from the installer itself (to run it silently with the right switches)."""
    try:
        with open(path, 'rb') as f:
            head = f.read(4 * 1024 * 1024)
    except OSError:
        return None
    if b'Inno Setup' in head:
        return 'inno'
    if b'Nullsoft' in head or b'NSIS' in head:
        return 'nsis'
    return None


def run_installer(path, log=print):
    """Run an installer and wait for it. Windows: elevated (UAC prompt), silent for Inno Setup / NSIS. Mac: the
    system's own package installer, with its password prompt. Returns the exit code."""
    low = path.lower()
    if host_os() == 'windows' and low.endswith(('.exe', '.msi')):
        kind = installer_kind(path)
        args = {'inno': '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-', 'nsis': '/S'}.get(kind, '')
        if low.endswith('.msi'):
            args, exe = f'/i "{path}" /qn /norestart', 'msiexec.exe'
        else:
            exe = path
        log('   running the installer' + (' silently' if args else ' - follow its setup window') + ' (Windows will ask for permission) ...')
        ps = (f"$p = Start-Process -FilePath '{exe}' " + (f"-ArgumentList '{args}' " if args else '') +
              "-Verb RunAs -Wait -PassThru; exit $p.ExitCode")
        from .proc import NOWIN
        r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps], timeout=3600, **NOWIN)
        return r.returncode
    if host_os() == 'mac' and low.endswith('.pkg'):
        log('   running the macOS installer (it will ask for your password) ...')
        cmd = f'installer -pkg {json.dumps(path)} -target /'
        from .proc import NOWIN
        r = subprocess.run(['osascript', '-e', f'do shell script {json.dumps(cmd)} with administrator privileges'], timeout=3600, **NOWIN)
        return r.returncode
    if host_os() == 'mac' and low.endswith('.dmg'):
        from .proc import NOWIN
        subprocess.run(['open', path], **NOWIN)
        log('   the disk image is open - drag or run the installer inside it')
        return 0
    raise RuntimeError('this installer type cannot be run automatically on this computer')


def installer_available(pid):
    p = INST_BY_ID.get(pid)
    return bool(p and p['assets'].get(host_os()))


def install_app(pid, log=print, progress=None, vt_key=None, require_vt=False):
    """Download a plugin's official installer (checked like the packs) and run it."""
    pack = INST_BY_ID[pid]
    if not installer_available(pid):
        raise RuntimeError(f"{pack['name']} has no automatic installer for this computer - get it from {pack['page']}")
    log(f"Looking up the latest {pack['name']} release ...")
    try:
        rels = _get_json(f"https://api.github.com/repos/{pack['repo']}/releases?per_page=10")
    except Exception as e:
        raise RuntimeError(f"couldn't reach GitHub: {e}. You can also download it from {pack['page']}")
    asset = pick_asset(pack, rels)
    if not asset:
        raise RuntimeError(f"no {host_os()} installer found for {pack['name']} - get it from {pack['page']}")
    log(f"Downloading {asset['name']} ({asset['version']}, {asset['size'] / 1e6:.0f} MB) ...")
    work = tempfile.mkdtemp(prefix='sl_inst_')
    try:
        fn = os.path.join(work, re.sub(r'[^A-Za-z0-9._-]', '_', asset['name']))
        download(asset['url'], fn, progress, asset.get('size', 0), limit=INSTALLER_MAX)
        from . import safety
        want, digest = expected_sha256(asset), sha256_of(fn)
        if want and digest != want:
            raise RuntimeError(f"{asset['name']} failed its checksum check - not installed")
        log('   checksum verified (SHA-256)' if want else '   (the project publishes no checksum for this file)')
        d = safety.defender_scan(fn)
        log('   ' + d['detail'])
        if d['ran'] and not d['clean']:
            raise RuntimeError(d['detail'] + ' - not installed')
        v = safety.vt_check(fn, digest, vt_key, log)
        log('   ' + v['detail'])
        if v.get('ran') and not v.get('clean'):
            raise RuntimeError(f"VirusTotal: {v['flagged']} of {v['engines']} engines flagged this download - not installed ({v['link']})")
        if require_vt and not v.get('ran'):
            raise RuntimeError('no VirusTotal result (' + v['detail'] + ') and you asked for one - not installed')
        run = fn
        if fn.lower().endswith('.zip'):                       # an installer shipped inside a zip
            ex = os.path.join(work, 'x')
            extract_zip(fn, ex, keep=lambda n: n.lower().endswith(('.exe', '.msi', '.pkg', '.dmg')))
            cands = []
            for root, _, files in os.walk(ex):
                cands += [os.path.join(root, f) for f in files if f.lower().endswith(('.exe', '.msi', '.pkg', '.dmg'))]
            cands = [c for c in cands if not re.search(r'uninst', os.path.basename(c), re.I)]
            if not cands:
                raise RuntimeError(f"no installer inside {asset['name']} - get it from {pack['page']}")
            run = max(cands, key=os.path.getsize)
            d = safety.defender_scan(run)
            if d['ran'] and not d['clean']:
                raise RuntimeError(d['detail'] + ' - not installed')
        code = run_installer(run, log)
        if code not in (0, 3010):
            raise RuntimeError(f"the {pack['name']} installer stopped (code {code}) - it may have been cancelled")
        rec = _record()
        rec['app:' + pid] = dict(version=asset['version'], asset=asset['name'], installed=int(time.time()), sha256=digest, app=True)
        _save_record(rec)
        log(f"{pack['name']} is installed.")
        return dict(ok=True, id=pid, version=asset['version'])
    finally:
        shutil.rmtree(work, ignore_errors=True)
