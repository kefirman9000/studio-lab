"""Wider sound pools for the electronic genres.

Many electronic genres offered only one to four sounds per part, so the Sound panel's "Suggested for this genre" list
was short and songs kept picking the same few. Each scene below lists the sounds that are idiomatic for it; every
genre in that scene gets them added to its parts' pools (after its own sounds, so its signature sound stays first).
The part a genre's authenticity rules check (trap's 808, dubstep's mid-bass, trance's lead ...) is left exactly as
the genre wrote it."""
from .styles import POOLS, STYLES
from .genre_groups import GROUPS

TARGET = 8            # sounds per part (a genre that already has more keeps them all)

SCENES = {
    'House & Disco': dict(
        bass=['deepbass', 'junobass', 'organbass', 'techbass', 'moogbass', 'bhbass', 'sinebass', 'bouncebass'],
        chords=['m1piano', 'rhodes', 'samplerstab', 'junopoly', 'houseorgan', 'pianosaw', 'mhpluck', 'stab'],
        pad=['lushpad', 'junopad', 'strings', 'vocalpad', 'warmpad', 'jupiterpad', 'solina', 'glasspad'],
        arp=['mhpluck', 'pluck', 'houseorgan', 'samplerstab', 'marimba', 'superpluck', 'kalimba', 'technoseq'],
        lead=['vocalchop', 'breathlead', 'mhpluck', 'pluck_saw', 'm1piano', 'moog_lead', 'softlead', 'rhodes']),
    'Techno & Trance': dict(
        bass=['rollbass', 'psybass', 'rumble', 'sawbass', 'techbass', 'deepbass', 'moogbass'],
        chords=['techstab', 'dubstab', 'hypersaw', 'supersaw', 'stab', 'samplerstab', 'obstab', 'polysynth'],
        pad=['trancepad', 'darkpad', 'atmos', 'lushpad', 'vocalpad', 'strings', 'warmpad', 'glasspad'],
        arp=['technoseq', 'superpluck', 'acid', 'techstab', 'pluck_saw', 'psylead', 'mhpluck', 'pluck'],
        lead=['supersaw_lead', 'emolead', 'hypersaw', 'psylead', 'techstab', 'acid', 'synclead', 'hardlead']),
    'Dubstep, Garage & Bass': dict(
        bass=['wobble', 'vowelwob', 'multiwob', 'tablewob', 'chopwob', 'growl', 'reese', 'midbass'],
        chords=['fbchord', 'rhodes', 'samplerstab', 'supersaw', 'stab', 'lushpad', 'polysynth', 'pianosaw'],
        pad=['glasspad', 'vocalpad', 'lushpad', 'atmos', 'darkpad', 'warmpad', 'strings', 'junopad'],
        arp=['vocalchop', 'pluck', 'superpluck', 'glock', 'chip', 'bell', 'mhpluck', 'kalimba'],
        lead=['vocalchop', 'emolead', 'supersaw_lead', 'screech', 'leadsaw', 'softlead', 'breathlead', 'psylead']),
    'Drum & Bass, Breaks & Hard': dict(
        bass=['reese', 'neuro', 'dnbwob', 'bouncebass', 'moogbass', 'sinebass', 'fmbass', 'growl'],
        chords=['pianosaw', 'rhodes', 'piano', 'hypersaw', 'samplerstab', 'stab', 'junopoly', 'strings'],
        pad=['strings', 'lushpad', 'vocalpad', 'atmos', 'glasspad', 'trancepad', 'darkpad', 'warmpad'],
        arp=['chip', 'superpluck', 'pluck', 'vocalchop', 'technoseq', 'bell', 'glock', 'samplerstab'],
        lead=['emolead', 'vocalchop', 'supersaw_lead', 'breathlead', 'leadsaw', 'synclead', 'hardlead', 'hoover']),
    'Hip-Hop, Trap & Phonk': dict(
        chords=['piano', 'rhodes', 'strings', 'choir', 'lofikeys', 'bell', 'glasspad', 'fbchord'],
        pad=['strings', 'choir', 'glasspad', 'vocalpad', 'atmos', 'darkpad', 'warmpad', 'lushpad'],
        arp=['bell', 'glock', 'celesta', 'pluck', 'piano', 'kalimba', 'harp', 'flute'],
        lead=['bell', 'glock', 'flute', 'piano', 'vocalchop', 'celesta', 'softlead', 'churchbell']),
    'Pop, R&B & Hopecore': dict(
        bass=['sinebass', 'moogbass', 'junobass', 'deepbass', 'fmbass', 'bouncebass'],
        chords=['piano', 'rhodes', 'pianosaw', 'junopoly', 'guitar', 'nylon', 'fbchord', 'epiano'],
        pad=['lushpad', 'strings', 'warmpad', 'vocalpad', 'junopad', 'glasspad', 'jupiterpad', 'choir'],
        arp=['pluck', 'mhpluck', 'glock', 'marimba', 'kalimba', 'superpluck', 'chip', 'vocalchop'],
        lead=['vocalchop', 'softlead', 'breathlead', 'emolead', 'moog_lead', 'flute', 'supersaw_lead', 'synclead']),
    'Chill, Lo-fi & Ambient': dict(
        bass=['sinebass', 'deepbass', 'moogbass', 'junobass', 'upright', 'ebass'],
        chords=['lofikeys', 'rhodes', 'piano', 'nylon', 'epiano', 'junopoly', 'wurli', 'guitar'],
        pad=['atmos', 'lushpad', 'glasspad', 'junopad', 'vocalpad', 'strings', 'darkpad', 'warmpad'],
        arp=['kalimba', 'marimba', 'celesta', 'harp', 'mhpluck', 'glock', 'vibes', 'pluck'],
        lead=['breathlead', 'flute', 'lofikeys', 'rhodes', 'vocalchop', 'softlead', 'sax', 'nylon']),
    'Retro & Video Game': dict(
        bass=['moogbass', 'sawbass', 'junobass', 'dxbass', 'chipbass', 'acid'],
        chords=['obstab', 'jupiterpad', 'junopoly', 'polysynth', 'synthbrass', 'supersaw', 'hypersaw', 'samplerstab'],
        pad=['jupiterpad', 'junopad', 'warmpad', 'solina', 'mellotron', 'darkpad', 'glasspad', 'vocalpad'],
        arp=['chip', 'superpluck', 'techstab', 'moogpluck', 'pluck_saw', 'technoseq', 'dxbell', 'pluck'],
        lead=['moog_lead', 'synclead', 'leadsaw', 'chip', 'hypersaw', 'softlead', 'synthbrass', 'emolead']),
    'Footwork & Juke': dict(
        chords=['samplerstab', 'rhodes', 'stab', 'vocalpad', 'm1piano'],
        arp=['vocalchop', 'samplerstab', 'chip', 'pluck'],
        lead=['vocalchop', 'samplerstab', 'chip', 'pluck_saw']),
}


def _locked(g, role):
    """The part a genre's authenticity rules check (trap's 808, dubstep's mid-bass ...) keeps its own list. (Genres
    whose defining part usually keeps its sound still mostly do - the wider list only adds the occasional variation.)"""
    from .fitness import SIGNATURE
    return g in SIGNATURE and SIGNATURE[g][0] == role


# 1.77 club synths, offered right after each genre's own signature sound (index 1-2), so the electronic scenes pick
# them often instead of only when the pool happens to have room: scene -> role -> sounds
CLUB = {
    'House & Disco': dict(chords=['housechord'], arp=['housechord', 'trancepluck', 'hollowpluck'], lead=['analoglead']),
    'Techno & Trance': dict(arp=['trancepluck'], lead=['analoglead', 'wavetable']),
    # 1.79 sounds
    'Chill, Lo-fi & Ambient': dict(arp=['handpan', 'hollowpluck'], pad=['granular', 'glassharmonica']),
    'Dubstep, Garage & Bass': dict(lead=['formantchop', 'wavetable'], arp=['formantchop', 'hollowpluck']),
    'Drum & Bass, Breaks & Hard': dict(lead=['wavetable']),
    'Pop, R&B & Hopecore': dict(lead=['formantchop']),
}
# individual genres (inserted the same way; the genre's own sound stays first)
WORLD = {'trip_hop': dict(lead=['theremin']), 'spooky_surf': dict(lead=['theremin']), 'monster_theme': dict(lead=['theremin']),
         'tension': dict(pad=['glassharmonica', 'waterphone'], lead=['glassharmonica']), 'ambient': dict(pad=['granular', 'glassharmonica']),
         'field_ambient': dict(pad=['granular'], arp=['handpan']), 'klezmer': dict(lead=['cimbalom'], arp=['cimbalom']),
         'gypsy_jazz': dict(arp=['cimbalom']), 'celtic_jig': dict(lead=['hurdygurdy']), 'folk_jam': dict(lead=['hurdygurdy']),
         'afro_house': dict(arp=['kora', 'balafon']), 'afrobeats': dict(arp=['balafon', 'kora']), 'afrobeat': dict(arp=['balafon']),
         'organic_house': dict(arp=['handpan', 'kora'], lead=['duduk']), 'chillstep': dict(lead=['formantchop'])}
VARIANTS_808 = ('808dist', '808long', '808punch')
_TECHNO = dict(chords=['dubchord', 'housechord'], arp=['hypnoseq', 'bleep'], lead=['analoglead'])
CLUB_GENRE = {g: _TECHNO for g in ('techno', 'minimal', 'melodic_techno', 'hard_techno', 'uk_tribal_techno',
                                   'berlin_school', 'acid_techno', 'industrial_techno', 'detroit_techno', 'hypnotic_techno')}
CLUB_GENRE.update({'minimal': dict(_TECHNO, arp=['bleep', 'hypnoseq']), 'dub_techno': dict(chords=['dubchord'], lead=['dubchord']),
                   'tech_house': dict(chords=['housechord'], arp=['hypnoseq', 'housechord'], lead=['analoglead'])})
SPLIT_FROM = ('sawbass', 'techbass', 'organbass', 'rollbass', 'moogbass', 'deepbass', 'junobass')   # bass lines that
                                                                                                # suit a split bass


def _club(g, scene, pools, banned):
    adds = dict(CLUB.get(scene) or {})
    adds.update(CLUB_GENRE.get(g) or {})             # a genre's own list replaces the scene's for that part
    for role, extra in (WORLD.get(g) or {}).items():
        adds[role] = list(extra) + [x for x in adds.get(role, []) if x not in extra]
    for role, extra in adds.items():
        lst = pools.get(role)
        if lst is None or _locked(g, role):
            continue
        for k, inst in enumerate([x for x in extra if x not in banned][:3]):
            if inst not in lst:
                lst.insert(min(len(lst), 1 + k), inst)
    b = pools.get('bass')
    if b and b[0] == '808' and not _locked(g, 'bass'):   # 808 genres: the 808 variants (not where the 808 is the signature)
        for k, v in enumerate(VARIANTS_808):
            if v not in b and v not in banned:
                b.insert(min(len(b), 1 + k), v)
    b = pools.get('bass')
    if b and b[0] in SPLIT_FROM and 'splitbass' not in b and 'splitbass' not in banned and not _locked(g, 'bass'):
        b.insert(min(len(b), 2), 'splitbass')


def widen():
    from .instruments import INSTRUMENTS
    for tab in GROUPS.values():
        for scene, genres in tab:
            add = SCENES.get(scene)
            if not add:
                continue
            for g in genres:
                pools = POOLS.get(g)
                if not pools or g not in STYLES:
                    continue
                if scene in CLUB or g in CLUB_GENRE or g in WORLD or (pools.get('bass') or [''])[0] == '808':
                    _club(g, scene, pools, set(STYLES[g].get('no_sounds') or ()))
                main = {t.get('layer'): t.get('inst') for t in STYLES[g]['tracks']}
                for role, extra in add.items():
                    lst = pools.get(role)
                    if lst is None or _locked(g, role):
                        continue
                    if role == 'bass' and main.get('bass') not in extra:
                        continue                   # a bass line is written for its sound (a sub, an 808, a walking
                                                   # line, a 303): only genres already on one of the scene's basses widen
                    banned = set(STYLES[g].get('no_sounds') or ())
                    for inst in extra:
                        if len(lst) >= TARGET:
                            break
                        if inst in INSTRUMENTS and inst not in lst and inst not in banned:
                            lst.append(inst)
