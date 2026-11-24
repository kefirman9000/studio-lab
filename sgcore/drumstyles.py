"""Drum patterns you can pick on their own - separate from the drum kit (the sounds) and from the genre.

Each style is a set of step patterns (16 steps = one 4/4 bar; X accent, x normal, o soft, . rest) for the usual drum
parts. Choosing one swaps the genre's own patterns for these on every part the genre has; parts the style does not
mention keep the genre's patterns, and parts the genre does not have are mapped onto the nearest part it does have.
"""
FOUR = 'X...X...X...X...'
BACK = '....X.......X...'

DRUM_STYLES = {
    'four_floor': dict(label='Four on the floor (house, disco)', drums=dict(
        kick=[FOUR], snare=[BACK], clap=[BACK], ohat=['..x...x...x...x.'], chat=['o.o.o.o.o.o.o.o.', '.o.o.o.o.o.o.o.o'],
        shaker=['oxoxoxoxoxoxoxox'])),
    'disco': dict(label='Disco (open-hat offbeats, 16th hats)', swing=0.5, drums=dict(
        kick=[FOUR], snare=[BACK], ohat=['..X...X...X...X.'], chat=['xxxxxxxxxxxxxxxx', 'x.xxx.xxx.xxx.xx'], tamb=[BACK])),
    'two_step': dict(label='2-step garage (skippy)', swing=0.6, drums=dict(
        kick=['X.........X.....', 'X......X..X.....', 'X.....X.X.....X.'], snare=[BACK], clap=[BACK],
        chat=['.xox.xox.xox.xox'], shaker=['o.o.o.o.o.o.o.o.'], rim=['......o......o..'])),
    'breakbeat': dict(label='Breakbeat (funky break)', drums=dict(
        kick=['X.....x...X.....', 'X.x.......X..x..'], snare=['....X..o.o..X...', '....X.o.....X..o'],
        chat=['x.x.x.x.x.x.x.x.'], ohat=['..............x.'])),
    'boom_bap': dict(label='Boom bap (90s hip-hop)', swing=0.58, drums=dict(
        kick=['X......xX.....x.', 'X.....x.X.......'], snare=[BACK, '....X.......X..o'], chat=['x.x.x.x.x.x.x.x.'],
        ohat=['..............x.'])),
    'trap': dict(label='Trap (half-time snare, rolling hats)', drums=dict(
        kick=['X.....X...X.....', 'X......X..X...X.'], snare=['........X.......'], clap=['........X.......'],
        chat=['x.x.x.x.x.x.x.x.', 'x.x.x.xxx.x.x.x.'])),
    'half_time': dict(label='Half-time (big, slow backbeat)', drums=dict(
        kick=['X.........X.....', 'X.......X.x.....'], snare=['........X.......'], clap=['........X.......'],
        chat=['x...x...x...x...'], ride=['x...x...x...x...'])),
    'dnb': dict(label='Drum & bass two-step', drums=dict(
        kick=['X.........X.....', 'X.........X..x..'], snare=[BACK, '....X..o....X...'], chat=['x.x.x.x.x.x.x.x.'],
        ride=['x.x.x.x.x.x.x.x.'])),
    'jersey_club': dict(label='Jersey club (bouncing kicks)', drums=dict(
        kick=['X..X..X...X.X...', 'X..X..X.X.X.X...'], snare=['....X.......X.X.'], clap=['....X.......X.X.'],
        chat=['x.x.x.x.x.x.x.x.'])),
    'dembow': dict(label='Dembow / reggaeton', drums=dict(
        kick=[FOUR], snare=['...X..X....X..X.'], clap=['...X..X....X..X.'], rim=['...x..x....x..x.'],
        chat=['x.x.x.x.x.x.x.x.'])),
    'afrobeats': dict(label='Afrobeats (log-rolling shaker groove)', swing=0.55, drums=dict(
        kick=['X...X...X...X...', 'X.....X.X...X...'], snare=['...x..x....x..x.'], rim=['...x..x....x..x.'],
        shaker=['xoxoxoxoxoxoxoxo'], conga=['..o..x.....o.x..'], chat=['x.x.x.x.x.x.x.x.'])),
    'rock': dict(label='Rock (straight 8ths)', drums=dict(
        kick=['X.....X.X.......', 'X.......X.X.....'], snare=[BACK], chat=['x.x.x.x.x.x.x.x.'], ride=['x.x.x.x.x.x.x.x.'],
        crash=['X...............'])),
    'motown': dict(label='Motown / 60s pop (two-step + tambourine)', drums=dict(
        kick=['X.......X.X.....', 'X.....X.......X.'], snare=[BACK], tamb=['x.x.X.x.x.x.X.x.'], chat=['x.x.x.x.x.x.x.x.'])),
    'shuffle': dict(label='Shuffle (blues, boogie)', swing=0.66, drums=dict(
        kick=['X.....X.X.....X.'], snare=[BACK], chat=['x.xxx.xxx.xxx.xx'], ride=['x.xxx.xxx.xxx.xx'])),
    'train': dict(label='Train beat (country, rockabilly)', drums=dict(
        kick=['X.......X.......'], snare=['o.o.X.o.o.o.X.o.'], chat=['x.x.x.x.x.x.x.x.'])),
    'bossa': dict(label='Bossa nova (rim clave, soft kick)', swing=0.52, drums=dict(
        kick=['X..x....X..x....'], rim=['x..x..x...x..x..'], snare=['x..x..x...x..x..'], shaker=['xoxoxoxoxoxoxoxo'],
        chat=['xoxoxoxoxoxoxoxo'])),
    'swing': dict(label='Swing (ride, feathered kick)', swing=0.66, drums=dict(
        ride=['x...x.x.x...x.x.'], chat=['....x.......x...'], kick=['o...o...o...o...'], snare=['................', '.......o......o.'])),
    'soft_pulse': dict(label='Soft pulse (gentle, sparse)', drums=dict(
        kick=['X.....x.......x.', 'X.......X.......'], snare=['....o.......o...'], clap=['....o.......o...'],
        chat=['..o...o...o...o.'], shaker=['.o.o.o.o.o.o.o.o'])),
    'minimal': dict(label='Minimal (kick and hats only)', drums=dict(
        kick=[FOUR], snare=['................'], clap=['................'], chat=['..o...o...o...o.'])),
}

# a part the chosen style has, but the genre doesn't -> the genre's nearest part
ALIAS = {'clap': ['snare'], 'snare': ['clap', 'rim'], 'rim': ['snare', 'clap'], 'chat': ['shaker', 'ride', 'tamb'],
         'ohat': ['chat'], 'ride': ['chat'], 'shaker': ['chat', 'tamb'], 'tamb': ['shaker', 'chat'], 'conga': ['tom', 'perc']}


def apply(st, style_id):
    """Put a drum style's patterns into a (copied) genre dict. Returns the parts it changed."""
    ds = DRUM_STYLES.get(style_id)
    if not ds:
        return []
    drums = st.get('drums') or {}
    changed = []
    for part, pats in ds['drums'].items():
        tgt = part if part in drums else next((a for a in ALIAS.get(part, []) if a in drums and a not in ds['drums']), None)
        if tgt:
            drums[tgt] = list(pats)
            changed.append(tgt)
    # the genre's other drum parts that the style doesn't speak for: hand-claps etc. keep playing their own pattern
    if 'swing' in ds:
        st['swing'] = ds['swing']
    st['drums'] = drums
    return changed


def menu():
    return [dict(id=k, name=v['label']) for k, v in DRUM_STYLES.items()]
