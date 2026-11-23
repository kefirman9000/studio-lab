"""(2.18) Sounds & instruments, one place: what this computer has, what can be downloaded automatically, what needs
you (a sign-up or your own installer), and one job that gets - or checks and repairs - everything automatic.

check()   -> a single checklist of every sound source (fast: no network, no plugin loading)
get_all() -> downloads/installs every missing automatic item and repairs incomplete ones; keeps going past failures
"""
import os
import re

GM_MB = 31
ACCOUNT = {'bbcso', 'labs', 'vital'}          # free, but the maker wants a sign-up first


def _item(id, group, name, state, what='', mb=0, auto=True, detail='', url='', kind=''):
    # state: ok | missing | repair | manual | unsupported | broken
    return dict(id=id, group=group, name=name, state=state, what=what, mb=mb, auto=auto, detail=detail, url=url, kind=kind)


def check(deep=False):
    """Every sound source with its state. deep=True also looks for missing files inside installed libraries/plugins."""
    from . import soundfont, samplelibs, vstpacks, vsthost
    items = []
    # recorded instruments
    gm = soundfont.installed()
    items.append(_item('gm', 'Recorded instruments', 'General MIDI library (GeneralUser GS)', 'ok' if gm else 'missing',
                       'pianos, guitars, basses and everything else the libraries below don\'t cover', 0 if gm else GM_MB,
                       kind='gm'))
    for r in samplelibs.status():
        st, detail, mb = 'ok', '', 0
        if not r['installed']:
            st, mb = 'missing', r['mb']
        else:
            missing = 0
            if deep:
                L = samplelibs.manifest()['libs'][r['id']]
                missing = sum(1 for f in L['files'] if not os.path.isfile(samplelibs._local(r['id'], f)))
            if r['update_mb'] or missing > 3:
                st, mb = 'repair', r['update_mb'] or 1
                detail = f'{missing} recordings missing' if missing else 'an update is available'
        items.append(_item('lib:' + r['id'], 'Recorded instruments', r['title'], st, r['blurb'], mb, detail=detail,
                           kind='lib'))
    # plugins
    vst_ok = vsthost.available()
    items.append(_item('vst', 'Free synths & effects', 'VST support (pedalboard)', 'ok' if vst_ok else 'missing',
                       'lets Studio Lab play plugins - installed automatically with the first plugin', 0 if vst_ok else 30,
                       kind='vst'))
    S = vstpacks.status()
    osname = S['os']
    for p in S['packs']:
        if p.get('retired'):
            continue
        pack = vstpacks.BY_ID.get(p['id'], {})
        can = bool(pack.get('assets', {}).get(osname))
        mbm = re.search(r'(\d+)', p.get('size') or '')
        mb = int(mbm.group(1)) if mbm else 0
        if p['installed']:
            st = 'ok'
            if deep and p['paths'] and not all(vstpacks.complete(x) for x in p['paths']):
                st = 'repair'
        elif p['partial']:
            st = 'repair' if can else 'unsupported'
        else:
            st = 'missing' if can else 'unsupported'
        items.append(_item('pack:' + p['id'], 'Free synths & effects', p['name'], st, p['plays'], 0 if st == 'ok' else mb,
                           auto=can, detail='not made for this computer' if not can and st != 'ok' else '',
                           url=p.get('page', ''), kind='pack'))
    for k in S['known']:
        if k['installed']:
            st = 'ok'
        elif k.get('auto'):
            st = 'missing'
        else:
            st = 'manual'
        acct = k['id'] in ACCOUNT
        detail = ('runs the official installer (your computer asks for permission)' if k.get('auto') else
                  'free - needs an account on the maker\'s site' if acct else
                  'free - download it from its website (no automatic installer for this computer)')
        items.append(_item('app:' + k['id'], 'Free synths & effects' if k.get('auto') else 'Get these yourself',
                           k['name'], st, k['plays'], 0, auto=bool(k.get('auto')), url=k.get('url', ''),
                           kind='app' if k.get('auto') else 'manual', detail=detail if st != 'ok' else ''))
    for b in S.get('broken') or []:
        items.append(_item('broken:' + b['path'], 'Needs attention', b['name'], 'broken', b['why'], auto=False, kind='broken'))
    auto_todo = [i for i in items if i['auto'] and i['state'] in ('missing', 'repair')]
    total = [i for i in items if i['state'] != 'unsupported' and i['kind'] != 'broken' and (i['auto'] or i['state'] == 'ok')]
    return dict(items=items, os=osname,
                summary=dict(ok=sum(1 for i in total if i['state'] == 'ok'), total=len(total), todo=len(auto_todo),
                             todo_mb=sum(i['mb'] for i in auto_todo),
                             manual=sum(1 for i in items if i['state'] == 'manual'),
                             broken=sum(1 for i in items if i['state'] == 'broken'),
                             apps=sum(1 for i in auto_todo if i['kind'] == 'app')))


def get_all(log=print, progress=None, apps=True, only=None, vt_key=None, require_vt=False, deep=True):
    """Get every automatic item that is missing, and repair the incomplete ones. One failure never stops the rest."""
    from . import soundfont, samplelibs, vstpacks, vsthost
    c = check(deep=deep)
    todo = [i for i in c['items'] if i['auto'] and i['state'] in ('missing', 'repair')
            and (apps or i['kind'] != 'app') and (not only or i['id'] in only)]
    if any(i['kind'] in ('pack', 'app') for i in todo) and not any(i['kind'] == 'vst' for i in todo) and not vsthost.available():
        todo.insert(0, next(i for i in c['items'] if i['kind'] == 'vst'))
    # VST support first: every plugin needs it
    todo.sort(key=lambda i: {'vst': 0, 'gm': 1, 'lib': 2, 'pack': 3, 'app': 4}.get(i['kind'], 9))
    done, failed = [], []
    if not todo:
        log('Everything that can be downloaded automatically is already here and complete ✓')
    weights = [max(1.0, float(i['mb'] or 5)) for i in todo]
    tot = sum(weights) or 1.0
    for n, it in enumerate(todo):
        base = sum(weights[:n]) / tot

        def prog(p, base=base, w=weights[n]):
            if progress:
                progress(min(0.99, base + w / tot * max(0.0, min(1.0, p))))
        log(f"[{n + 1}/{len(todo)}] {it['name']}{' (repair)' if it['state'] == 'repair' else ''}")
        prog(0)
        try:
            if it['kind'] == 'vst':
                if not vsthost.install(log):
                    raise RuntimeError('could not install VST support')
            elif it['kind'] == 'gm':
                soundfont.download(log)
            elif it['kind'] == 'lib':
                samplelibs.install(it['id'][4:], log, prog)
            elif it['kind'] == 'pack':
                vstpacks.install(it['id'][5:], log, prog, vt_key=vt_key, require_vt=require_vt)
            elif it['kind'] == 'app':
                vstpacks.install_app(it['id'][4:], log, prog, vt_key=vt_key, require_vt=require_vt)
            done.append(it['id'])
        except Exception as e:                     # keep going: report it at the end
            log(f"   ✗ {it['name']}: {e}")
            failed.append(dict(id=it['id'], name=it['name'], error=str(e)))
    if any(i['kind'] in ('pack', 'app') for i in todo):
        try:
            vsthost.probe_all(log)
        except Exception as e:
            log(f'   (plugin check skipped: {e})')
    if progress:
        progress(1.0)
    if todo:
        log(f"Finished: {len(done)} done" + (f", {len(failed)} failed - press the button again to retry them" if failed else ' ✓'))
    return dict(ok=not failed, done=done, failed=failed)
