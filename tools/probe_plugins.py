"""One-off probe (run in CI, Linux): install candidate plugin packs, dump their parameters, check they make sound."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from sgcore import vstpacks
import urllib.request
def _gj(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'StudioLab', 'Accept': 'application/vnd.github+json',
                                               'Authorization': 'Bearer ' + os.environ.get('GH_TOKEN', '')})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())
vstpacks._get_json = _gj
OUT = sys.argv[1]
ids = sys.argv[2:]
res = {}
for pid in ids:
    r = res[pid] = {}
    try:
        vstpacks.install(pid, log=lambda *a: print(pid, *a))
        paths = vstpacks.installed_paths(vstpacks.BY_ID[pid])
        r['paths'] = paths
        import pedalboard
        from pedalboard import load_plugin
        from mido import Message
        for p in [q for q in paths if q.endswith('.vst3')][:1] or paths[:1]:
            try:
                names = pedalboard.VST3Plugin.get_plugin_names_for_file(p) if p.endswith('.vst3') else [None]
            except Exception:
                names = [None]
            for nm in names[:3]:
                try:
                    pl = load_plugin(p, plugin_name=nm) if nm else load_plugin(p)
                    params = {k: (str(v.raw_value), v.string_value if hasattr(v, 'string_value') else '', list(getattr(v, 'valid_values', []) or [])[:40])
                              for k, v in pl.parameters.items()}
                    out = pl([Message('note_on', note=48, velocity=100, time=0), Message('note_off', note=48, time=1.0)],
                             duration=1.5, sample_rate=44100, num_channels=2)
                    progs = None
                    for key in ('program', 'Program', 'preset', 'Preset', 'patch', 'Patch'):
                        if key in pl.parameters:
                            progs = list(getattr(pl.parameters[key], 'valid_values', []) or [])[:400]
                    r[nm or os.path.basename(p)] = dict(programs=progs, is_instrument=getattr(pl, 'is_instrument', None), n_params=len(params),
                                                       peak=float(np.abs(out).max()), params=params)
                    print(pid, nm, 'params', len(params), 'peak', float(np.abs(out).max()))
                except Exception as e:
                    r[str(nm)] = 'load failed: %s' % e
                    print(pid, nm, 'load failed', e)
    except Exception as e:
        r['error'] = str(e)
        print(pid, 'ERROR', e)
json.dump(res, open(os.path.join(OUT, 'plugins.json'), 'w'), indent=1, default=str)
# apply every rig patch of the probed players and check it sounds
from sgcore import vstrigs, vst_worker
from pedalboard import load_plugin
from mido import Message
chk = {}
for pid in ids:
    paths = [q for q in vstpacks.installed_paths(vstpacks.BY_ID[pid]) if q.endswith('.vst3')]
    for name, pt in vstrigs.PATCHES.items():
        if pt['player'] != pid or not paths:
            continue
        try:
            pl = load_plugin(paths[0])
            applied, missing = vst_worker.apply_recipe(pl, vstrigs.recipe_for(name))
            ev = []
            for n_ in (48, 52, 55):
                ev += [Message('note_on', note=n_, velocity=100, time=0.0), Message('note_off', note=n_, time=1.0)]
            out = pl(ev, duration=2.0, sample_rate=44100, num_channels=2)
            pk = float(np.abs(out).max()); late = float(np.abs(out[:, int(1.6 * 44100):]).max())
            chk[name] = dict(missing=missing, peak=pk, tail=late)
            print(name, 'missing', missing, 'peak', round(pk, 3), 'tail', round(late, 4))
        except Exception as e:
            chk[name] = str(e); print(name, 'FAIL', e)
json.dump(chk, open(os.path.join(OUT, 'patches.json'), 'w'), indent=1)
