"""Song names: every song gets a title (yours, or an invented one that fits its genre and mood).

The name goes at the front of every exported file, before the technical tag:
    Ashes-of-the-North_cinematic_journey_D-minor_88bpm_seed3.mp3
Invented names are deterministic (same song settings = same name), so re-rendering a song keeps its name.
"""
import random
import re

ADJ = {
    'Orchestral': ['Crimson', 'Fallen', 'Eternal', 'Silent', 'Iron', 'Last', 'Distant', 'Burning', 'Forgotten', 'Golden', 'Shattered',
                   'Rising', 'Hollow', 'Ancient', 'Endless', 'Darkened', 'Sacred', 'Winter', 'Broken', 'Unbroken', 'Northern'],
    'Electronic': ['Neon', 'Midnight', 'Electric', 'Velvet', 'Digital', 'Lunar', 'Infinite', 'Chrome', 'Static', 'Hyper', 'Liquid',
                   'Solar', 'Hidden', 'Faded', 'Glass', 'Violet', 'Afterglow', 'Strobe', 'Phantom', 'Polar'],
    'Classic': ['Blue', 'Golden', 'Sweet', 'Lonesome', 'Late', 'Easy', 'Wild', 'Southern', 'Old', 'Summer', 'Lazy', 'Smoky',
                'Honey', 'Restless', 'Runaway', 'Little', 'Lucky', 'Velvet', 'Paper', 'Highway'],
}
NOUN = {
    'Orchestral': ['Horizon', 'Kingdoms', 'Oath', 'Requiem', 'Crown', 'Empire', 'Dawn', 'Throne', 'Legacy', 'Valor', 'Ashes', 'Tides',
                   'Covenant', 'Citadel', 'Exodus', 'Memory', 'Light', 'Storm', 'Sky', 'Heart', 'Shadows', 'Glory'],
    'Electronic': ['Pulse', 'Signal', 'Skyline', 'Circuit', 'Drift', 'Horizon', 'Echoes', 'Frequency', 'Mirage', 'Orbit', 'Dreams',
                   'Lights', 'Wave', 'Motion', 'Paradise', 'Static', 'Voltage', 'Nights', 'Memory', 'Haze'],
    'Classic': ['Road', 'Rain', 'Heartache', 'Avenue', 'Sunday', 'River', 'Morning', 'Train', 'Letter', 'Porch', 'Fire', 'Groove',
                'Lullaby', 'Moon', 'Saturday', 'Town', 'Dance', 'Blues', 'Soul', 'Window'],
}
MOOD_ADJ = {'dark': ['Black', 'Shadow', 'Cold', 'Grim'], 'happy': ['Bright', 'Sunny', 'Golden', 'Happy'],
            'chill': ['Slow', 'Soft', 'Easy', 'Calm'], 'epic': ['Mighty', 'Eternal', 'Titan', 'Glorious'],
            'dreamy': ['Dreaming', 'Hazy', 'Floating', 'Starlit'], 'aggressive': ['Savage', 'Brutal', 'Raging', 'Feral'],
            'melancholic': ['Fading', 'Lonely', 'Grey', 'Lost'], 'energetic': ['Wired', 'Rapid', 'Blazing', 'Electric'],
            'mysterious': ['Hidden', 'Veiled', 'Secret', 'Strange'], 'romantic': ['Tender', 'Rose', 'Velvet', 'Sweet']}
PATTERNS = ['{a} {n}', '{a} {n}', 'The {a} {n}', '{n} of the {a2}', '{a} {n}', 'Beyond the {n}', '{n} in {a2}']
A2 = {'Orchestral': ['North', 'Fallen', 'Ages', 'Brave', 'Night', 'Lost', 'Dawn', 'Deep'],
      'Electronic': ['Night', 'Future', 'City', 'Void', 'Static', 'Neon', 'Stars', 'Machine'],
      'Classic': ['Morning', 'Road', 'Heart', 'South', 'Evening', 'Rain', 'Town', 'Summer']}


def invent(style, category, mood, seed):
    rng = random.Random(f'{style}|{seed}|{mood}|name')
    cat = category if category in ADJ else 'Electronic'
    adj = list(ADJ[cat]) + (MOOD_ADJ.get(mood or '', []) * 2)
    pat = rng.choice(PATTERNS)
    n = rng.choice(NOUN[cat])
    a = rng.choice([x for x in adj if x != n] or adj)
    return pat.format(a=a, n=n, a2=rng.choice(A2[cat]))


def clean(name):
    """A user-typed title, kept readable but safe for every file system."""
    name = re.sub(r'[\x00-\x1f<>:"/\\|?*]+', ' ', str(name or '')).strip().strip('.')
    return re.sub(r'\s+', ' ', name)[:60]


def slug(name):
    """'Ashes of the North' -> 'Ashes-of-the-North' (file-name part)."""
    s = re.sub(r'[^\w\-\']+', '-', clean(name), flags=re.UNICODE).strip('-')
    return re.sub(r'-{2,}', '-', s) or 'Untitled'


def song_name(song):
    opts = song.get('user_opts') or song['opts']
    given = clean(getattr(opts, 'title', None) or '')
    if given:
        return given
    st = song['st']
    return invent(song['style'], st.get('category'), getattr(opts, 'mood', None), song['seed'])
