"""One-off probe (run in CI, Linux): install candidate plugin packs, dump their parameters, check they make sound."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from sgcore import vstpacks
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
        for p in paths[:2]:
            try:
                names = pedalboard.VST3Plugin.get_plugin_names_for_file(p) if p.endswith('.vst3') else [None]
            except Exception:
                names = [None]
            for nm in names[:3]:
                try:
                    pl = load_plugin(p, plugin_name=nm) if nm else load_plugin(p)
                    params = {k: (str(v.raw_value), v.string_value if hasattr(v, 'string_value') else '', list(getattr(v, 'valid_values', []) or [])[:12])
                              for k, v in pl.parameters.items()}
                    out = pl([Message('note_on', note=48, velocity=100, time=0), Message('note_off', note=48, time=1.0)],
                             duration=1.5, sample_rate=44100, num_channels=2)
                    r[nm or os.path.basename(p)] = dict(is_instrument=getattr(pl, 'is_instrument', None), n_params=len(params),
                                                       peak=float(np.abs(out).max()), params=params)
                    print(pid, nm, 'params', len(params), 'peak', float(np.abs(out).max()))
                except Exception as e:
                    r[str(nm)] = 'load failed: %s' % e
                    print(pid, nm, 'load failed', e)
    except Exception as e:
        r['error'] = str(e)
        print(pid, 'ERROR', e)
json.dump(res, open(os.path.join(OUT, 'plugins.json'), 'w'), indent=1, default=str)
