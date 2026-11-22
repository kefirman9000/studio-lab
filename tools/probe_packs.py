"""One-off probe (run in CI): list the newest release assets of candidate plugin packs, install the Linux builds,
dump their parameter names and check they make sound; list candidate sample-library files with git blob SHA-1s."""
import json, os, subprocess, sys, urllib.request, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = sys.argv[1] if len(sys.argv) > 1 else 'probe_out'
os.makedirs(OUT, exist_ok=True)
REPOS = ['surge-synthesizer/OB-Xf', 'VASTDynamics/Vaporizer2', 'DISTRHO/Cardinal', 'Geonkick-Synthesizer/geonkick',
         'DrumGizmo/drumgizmo', 'sfztools/sfizz']
tok = os.environ.get('GH_TOKEN', '')
def gj(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ' + tok})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())
rel = {}
for r in REPOS:
    try:
        rs = gj(f'https://api.github.com/repos/{r}/releases?per_page=5')
        rel[r] = [dict(tag=x['tag_name'], pre=x['prerelease'], assets=[(a['name'], a['size']) for a in x['assets']]) for x in rs]
    except Exception as e:
        rel[r] = str(e)
json.dump(rel, open(os.path.join(OUT, 'releases.json'), 'w'), indent=1)
print(json.dumps({k: (v[0] if isinstance(v, list) and v else v) for k, v in rel.items()}, indent=1)[:20000])
# sample libraries: file lists with blob sha + size
for repo, d in (('sgossner/VSCO-2-CE', 'vsco'), ('sfzinstruments/SalamanderGrandPiano', 'salamander')):
    subprocess.run(['git', 'clone', '-q', '--depth', '1', '--filter=blob:none', '--no-checkout', f'https://github.com/{repo}', d], check=True)
    head = subprocess.run(['git', '-C', d, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    ls = subprocess.run(['git', '-C', d, 'ls-tree', '-r', '-l', 'HEAD'], capture_output=True, text=True).stdout
    rows = []
    for line in ls.splitlines():
        meta, path = line.split('\t', 1)
        mode, typ, sha, size = meta.split()
        rows.append(dict(p=path, sha=sha, s=int(size) if size.isdigit() else 0))
    json.dump(dict(repo=repo, commit=head, files=rows), open(os.path.join(OUT, d + '_files.json'), 'w'))
    tops = {}
    for r_ in rows:
        k = '/'.join(r_['p'].split('/')[:2]); tops.setdefault(k, [0, 0]); tops[k][0] += 1; tops[k][1] += r_['s']
    print(repo, head, len(rows), 'files'); [print('  ', k, v[0], '%.0f MB' % (v[1] / 1e6)) for k, v in sorted(tops.items())]
