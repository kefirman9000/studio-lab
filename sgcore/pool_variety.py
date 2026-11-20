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
    'House & Disco': dict(chords=['housechord', 'frenchchord', 'organchord', 'detroitchord'],
                          arp=['housechord', 'housevox', 'organchord', 'trancepluck', 'hollowpluck'],
                          pad=['discostrings', 'detroitchord'], lead=['housevox', 'analoglead', 'discostrings']),
    'Techno & Trance': dict(arp=['trancepluck'], lead=['analoglead', 'wavetable']),
    # 1.79 sounds
    'Chill, Lo-fi & Ambient': dict(arp=['handpan', 'hollowpluck'], pad=['granular', 'glassharmonica']),
    'Drum & Bass, Breaks & Hard': dict(lead=['electrosaw', 'wavetable', 'peaklead'], chords=['dancestab', 'liquidkeys'],
                                       arp=['dancestab', 'liquidkeys'], pad=['liquidpad']),
    'Dubstep, Garage & Bass': dict(lead=['formantchop', 'mdsawlead', 'wavetable', 'fmscreech', 'yoi', 'dubhorn'],
                                   arp=['formantchop', 'hollowpluck'], pad=['liquidpad'], chords=['colorbass', 'dubhorn']),
    'Pop, R&B & Hopecore': dict(lead=['formantchop']),
}
# individual genres (inserted the same way; the genre's own sound stays first)
WORLD = {'trip_hop': dict(lead=['theremin']), 'spooky_surf': dict(lead=['theremin']), 'monster_theme': dict(lead=['theremin']),
         'tension': dict(pad=['glassharmonica', 'waterphone'], lead=['glassharmonica']), 'ambient': dict(pad=['granular', 'glassharmonica']),
         'field_ambient': dict(pad=['granular'], arp=['handpan']), 'klezmer': dict(lead=['cimbalom'], arp=['cimbalom']),
         'gypsy_jazz': dict(arp=['cimbalom']), 'celtic_jig': dict(lead=['hurdygurdy']), 'folk_jam': dict(lead=['hurdygurdy']),
         'afro_house': dict(arp=['kora', 'balafon']), 'afrobeats': dict(arp=['balafon', 'kora']), 'afrobeat': dict(arp=['balafon']),
         'organic_house': dict(arp=['handpan', 'kora'], lead=['duduk']), 'chillstep': dict(lead=['formantchop'])}
# (1.88) the new synth bank, filed with the genres it was made for
_NEW_188 = {
    'synthwave': dict(lead=['synthwavelead', 'cs80brass'], chords=['cs80brass', 'ppgwave'], pad=['ppgwave', 'cs80brass'], bass=['outrunbass']),
    'dark_synthwave': dict(lead=['synthwavelead'], pad=['ppgwave', 'bowedpad'], bass=['outrunbass']),
    'synthpop': dict(lead=['synthwavelead', 'vocalead'], chords=['ppgwave'], bass=['slapsynth', 'outrunbass']),
    'city_pop': dict(bass=['slapsynth'], chords=['ppgwave'], pad=['ppgwave']),
    'new_jack_swing': dict(bass=['slapsynth'], chords=['ppgwave']),
    'electro_funk': dict(bass=['slapsynth'], lead=['synthwavelead']),
    'future_bass': dict(chords=['futurechord', 'colorbass'], arp=['kawaiipluck'], lead=['kawaiipluck', 'mdsawlead', 'vocalead']),
    'melodic_dubstep': dict(chords=['futurechord', 'colorbass'], lead=['mdsawlead', 'vocalead'], bass=['colorbass']),
    'future_bass_dubstep': dict(lead=['mdsawlead'], bass=['colorbass']),
    'hyperpop': dict(arp=['kawaiipluck', 'bitpiano'], lead=['kawaiipluck'], chords=['futurechord', 'bitpiano']),
    'glitch_pop': dict(arp=['kawaiipluck', 'bitpiano'], chords=['bitpiano']),
    'kpop': dict(arp=['kawaiipluck'], chords=['futurechord'], lead=['vocalead']),
    'hopecore': dict(arp=['kawaiipluck', 'icebell'], chords=['futurechord'], pad=['shimmerpad']),
    'tropical_house': dict(arp=['tropicalpluck'], lead=['tropicalpluck']),
    'balearic_chill': dict(arp=['tropicalpluck'], pad=['windpad']),
    'lofi': dict(chords=['tapekeys', 'bitpiano'], arp=['tapekeys'], pad=['windpad']),
    'beat_tape_cinematic': dict(chords=['tapekeys']),
    'jazz_rap': dict(chords=['tapekeys']),
    'downtempo': dict(chords=['tapekeys'], pad=['windpad', 'reverseswell']),
    'hazy_downtempo': dict(chords=['tapekeys'], pad=['reverseswell', 'windpad']),
    'sunrise_chillwave': dict(lead=['synthwavelead'], pad=['ppgwave', 'reverseswell']),
    'alt_rnb': dict(pad=['rnbpad'], arp=['pluckbell'], lead=['sinelead']),
    'rnb': dict(pad=['rnbpad']),
    'slow_jam': dict(pad=['rnbpad']),
    'trap': dict(arp=['pluckbell'], lead=['pluckbell', 'sinelead']),
    'plugg': dict(arp=['pluckbell'], lead=['sinelead', 'pluckbell']),
    'cloud_rap': dict(pad=['rnbpad', 'reverseswell'], lead=['sinelead']),
    'g_funk': dict(lead=['sinelead']),
    'chiptune': dict(lead=['chiparp'], arp=['chiparp']),
    'ps1_game': dict(lead=['chiparp'], pad=['ppgwave']),
    'cybergrind': dict(lead=['chiparp'], arp=['chiparp']),
    'field_ambient': dict(pad=['shimmerpad', 'bowedpad', 'windpad'], arp=['icebell'], lead=['ebowguitar']),
    'fourth_world': dict(pad=['windpad', 'shimmerpad'], lead=['ebowguitar']),
    'cinematic': dict(pad=['shimmerpad', 'bowedpad'], chords=['cs80brass']),
    'tension': dict(pad=['bowedpad', 'windpad'], arp=['icebell']),
    'post_rock': dict(lead=['ebowguitar'], pad=['shimmerpad']),
    'shoegaze': dict(lead=['ebowguitar'], pad=['shimmerpad', 'reverseswell']),
    'christmas_magic': dict(arp=['icebell'], lead=['icebell']),
    'acid_house': dict(bass=['acidsquare']),
    'trance': dict(lead=['vocalead']),
    'uplifting_trance': dict(pad=['shimmerpad']),
}
VARIANTS_808 = ('808dist', '808long', '808punch')
_TECHNO = dict(chords=['dubchord', 'industrialstab', 'ravestab2', 'detroitchord'], arp=['hypnoseq', 'berlinseq', 'metalperc', 'bleep'],
               lead=['peaklead', 'analoglead', 'ravestab2'], pad=['hypnopad', 'detroitchord'])
CLUB_GENRE = {g: _TECHNO for g in ('techno', 'minimal', 'melodic_techno', 'hard_techno', 'uk_tribal_techno',
                                   'berlin_school', 'acid_techno', 'industrial_techno', 'detroit_techno', 'hypnotic_techno')}
_TRANCE = dict(arp=['sylpluck', 'tranceseq', 'dreampluck', 'trancepizz', 'trancebell', 'breakpiano', 'laserpluck'],
               lead=['screamlead', 'dreamlead', 'tranceflute', 'trancebell'],
               chords=['upstab', 'dreampad', 'vocoderchord', 'breakpiano'], pad=['trancestrings', 'gatedchoir', 'dreampad', 'dreamair'],
               bass=['fmroll', 'offbass', 'dreambass'])
for _g in ('trance', 'uplifting_trance', 'progressive_trance', 'club_trance_2000s', 'progressive_trance_2010s',
           'vocal_trance_remix', 'electro_prog_trance', 'trance_pop_90s', 'hard_trance'):
    CLUB_GENRE[_g] = _TRANCE
CLUB_GENRE['hard_trance'] = dict(_TRANCE, arp=['laserpluck', 'tranceseq', 'sylpluck'], lead=['rawlead', 'screamlead', 'trancebell'],
                                 bass=['fmroll', 'offbass'])
_DREAMY_HOUSE = dict(chords=['housechord', 'organchord', 'dreampad', 'detroitchord'], arp=['dreampluck', 'housechord', 'hollowpluck'],
                     pad=['dreampad', 'dreamair', 'discostrings'], lead=['dreamlead', 'housevox', 'analoglead'], bass=['dreambass'])
for _g in ('melodic_house', 'deep_house', 'progressive_house', 'sunny_melodic_house', 'organic_house', 'balearic_chill'):
    CLUB_GENRE[_g] = dict(_DREAMY_HOUSE, **{k: v + [x for x in _DREAMY_HOUSE.get(k, []) if x not in v]
                                              for k, v in CLUB_GENRE.get(_g, {}).items()})
CLUB_GENRE.update({'minimal': dict(_TECHNO, arp=['bleep', 'metalperc', 'hypnoseq', 'berlinseq'], chords=['dubchord', 'detroitchord'],
                                   lead=['analoglead', 'metalperc']),
                   'dub_techno': dict(chords=['dubchord', 'detroitchord'], lead=['dubchord'], pad=['hypnopad']),
                   'berlin_school': dict(_TECHNO, arp=['berlinseq', 'hypnoseq', 'bleep']),
                   'tech_house': dict(chords=['housechord'], arp=['hypnoseq', 'housechord'], lead=['analoglead'])})
_FESTIVAL = dict(lead=['anthemlead', 'festpluck'], arp=['festpluck'], chords=['festpluck', 'anthemlead'], pad=['buildpad'],
                 bass=['hardbass', 'electrobass'])
for _g in ('bigroom', 'electro_prog_trance', 'electro_house', 'festival_house', 'big_room_techno'):
    CLUB_GENRE[_g] = dict(_FESTIVAL, **{k: v + [x for x in _FESTIVAL.get(k, []) if x not in v] for k, v in CLUB_GENRE.get(_g, {}).items()})
CLUB_GENRE['progressive_house'] = dict(CLUB_GENRE['progressive_house'], lead=['anthemlead', 'dreamlead', 'festpluck', 'housevox'],
                                       arp=['festpluck', 'dreampluck', 'housechord'], pad=['buildpad', 'dreampad', 'dreamair'],
                                       bass=['hardbass', 'dreambass'])
for _g in ('techno', 'hard_techno', 'melodic_techno'):                   # peak-time techno: the big leads and build pads too
    CLUB_GENRE[_g] = dict(CLUB_GENRE[_g], lead=CLUB_GENRE[_g]['lead'] + ['anthemlead'], pad=CLUB_GENRE[_g]['pad'] + ['buildpad'])
for _g in ('trance', 'uplifting_trance', 'progressive_trance', 'progressive_trance_2010s', 'club_trance_2000s'):
    CLUB_GENRE[_g] = dict(CLUB_GENRE[_g], lead=CLUB_GENRE[_g]['lead'] + ['anthemlead'], pad=CLUB_GENRE[_g]['pad'] + ['buildpad'])
SPLIT_FROM = ('sawbass', 'techbass', 'organbass', 'rollbass', 'moogbass', 'deepbass', 'junobass')   # bass lines that
                                                                                                # suit a split bass


_DNB_MID = ('reese', 'neuro', 'dnbwob', 'growl', 'fmbass', 'bouncebass', 'sawbass')
BASS_SWAPS = {   # scene -> [(the genre's own bass family, new basses that play the same kind of line)]
    'House & Disco': [(('organbass', 'techbass', 'deepbass', 'sawbass', 'moogbass', 'bhbass'), ['garagebass'])],
    'Techno & Trance': [(('sawbass', 'techbass', 'moogbass', 'acid'), ['berlinseq'])],
    'Drum & Bass, Breaks & Hard': [(_DNB_MID, ['dancereese', 'jumpup', 'neuroformant']),
                                   (('moogbass', 'sinebass', 'deepbass', 'bouncebass'), ['rollerbass'])],
    'Dubstep, Garage & Bass': [(('wobble', 'growl', 'reese', 'midbass', 'riddim', 'vowelwob', 'multiwob', 'fmbass'),
                                ['yoi', 'talkgrowl2', 'tearout', 'squareriddim', 'laserwob', 'robotbass', 'creakbass', 'stabwob',
                                 'divebass', 'dubhorn']),
                               (('sinebass', 'subwob', 'deepbass', '808'), ['dubsub'])],
}


def _club(g, scene, pools, banned):
    adds = dict(CLUB.get(scene) or {})
    if 'liquid' in g:                                # liquid DnB stays soft: none of the aggressive DnB synths
        adds = {r: [x for x in v if x not in ('electrosaw', 'dancestab', 'peaklead')] for r, v in adds.items()}
        banned = set(banned) | {'electrosaw', 'techneuro', 'peaklead', 'jumpup', 'neuroformant'}
    if g.startswith('deep_') or g in ('minimal', 'dub_techno', 'chillstep'):   # deep / minimal: no brutal sounds
        banned = set(banned) | {'tearout', 'yoi', 'squareriddim', 'talkgrowl2', 'fmscreech', 'industrialstab', 'ravestab2',
                                'peaklead', 'laserwob', 'robotbass', 'creakbass', 'stabwob', 'divebass', 'dubhorn', 'rawlead'}
    adds.update(CLUB_GENRE.get(g) or {})             # a genre's own list replaces the scene's for that part
    for role, extra in list((WORLD.get(g) or {}).items()) + list((_NEW_188.get(g) or {}).items()):
        adds[role] = list(extra) + [x for x in adds.get(role, []) if x not in extra]
    nb = [x for x in ((_NEW_188.get(g) or {}).get('bass') or []) if x not in banned]
    if nb and _locked(g, 'bass'):                    # a protected bass takes only what its own check accepts
        from .fitness import SIGNATURE
        nb = [x for x in nb if x in SIGNATURE[g][1]]
    b0 = pools.get('bass')
    if nb and b0 and b0[0] not in ('808', 'drill808'):
        for k, x in enumerate(nb):                       # a new bass that plays this genre's kind of line
            if x not in b0:
                b0.insert(min(len(b0), 1 + k), x)
    for role, extra in adds.items():
        lst = pools.get(role)
        if lst is None or role == 'bass':
            continue
        if _locked(g, role):                              # a protected part only takes sounds its own check accepts
            from .fitness import SIGNATURE
            extra = [x for x in extra if x in SIGNATURE[g][1]]
        for k, inst in enumerate([x for x in extra if x not in banned][:5]):
            if inst not in lst:
                lst.insert(min(len(lst), 1 + k), inst)
    b = pools.get('bass')
    if b and b[0] == '808' and not _locked(g, 'bass'):   # 808 genres: the 808 variants (not where the 808 is the signature)
        for k, v in enumerate(VARIANTS_808):
            if v not in b and v not in banned:
                b.insert(min(len(b), 1 + k), v)
    b = pools.get('bass')
    if scene == 'Drum & Bass, Breaks & Hard' and b and b[0] in ('reese', 'neuro', 'dnbwob', 'growl', 'fmbass', 'bouncebass') \
            and not _locked(g, 'bass'):
        for k, v in enumerate(('techneuro', 'electrosaw')):
            if v not in b and v not in banned:
                b.insert(min(len(b), 2 + k), v)
    if b and 'fmroll' in (adds.get('bass') or []) and b[0] in ('rollbass', 'sawbass', 'psyroll', 'moogbass') \
            and 'fmroll' not in b and not _locked(g, 'bass'):
        b.insert(min(len(b), 1), 'fmroll')
    for k, nb in enumerate(x for x in (adds.get('bass') or []) if x in ('dreambass', 'hardbass', 'electrobass', 'offbass')):
        if b and nb not in b and nb not in banned and not _locked(g, 'bass') and b[0] not in ('acid', '808', 'psyroll', 'psybass'):
            b.insert(min(len(b), 1 + k), nb)                  # dreamy / festival genres: their own kind of bass too
    for fam, news in BASS_SWAPS.get(scene, ()):
        if b and b[0] in fam and not ('liquid' in g and fam is _DNB_MID):
            if _locked(g, 'bass'):                       # a protected bass takes only what its own check accepts
                from .fitness import SIGNATURE
                news = [x for x in news if x in SIGNATURE[g][1]]
            for k, v in enumerate(news):
                if v not in b and v not in banned:
                    b.insert(min(len(b), 1 + k), v)
    if b and b[0] in SPLIT_FROM and 'splitbass' not in b and 'splitbass' not in banned and not _locked(g, 'bass'):
        b.insert(min(len(b), 2), 'splitbass')


# (1.90) era / character check: sounds the shared scene lists added to a genre are dropped when they clash with it
# (a genre's own chosen sounds are never touched). tools/pool_audit.py lists what was dropped.
BRUTAL = {'tearout', 'yoi', 'squareriddim', 'talkgrowl2', 'fmscreech', 'laserwob', 'robotbass', 'creakbass', 'stabwob',
          'divebass', 'dubhorn', 'rawlead', 'industrialstab', 'peaklead', 'screech', 'riddim', 'metalbass', 'techneuro',
          'electrosaw', 'neuroformant', 'jumpup', 'chopwob', 'multiwob', 'tablewob', 'fmgrowl', 'electrobass', 'hardlead'}
MODERN_EDM = {'futurechord', 'colorbass', 'mdsawlead', 'kawaiipluck', 'wavetable', 'formantchop', 'anthemlead', 'megastab',
              'festpluck', 'syncstab', 'hypersaw', 'laserpluck', 'superpluck', 'supersaw_lead', 'vocalchop', 'yoi',
              'buildpad', 'electrosaw', 'dancestab'}
GENTLE_WORDS = ('deep', 'chill', 'ambient', 'lofi', 'hauntology', 'jazz', 'soul', 'smooth', 'bossa', 'lounge', 'downtempo',
                'balearic', 'organic', 'minimal', 'dub_techno', 'liquid', 'lullaby', 'campfire', 'dream', 'sunrise', 'hazy',
                'field', 'new_age', 'chant', 'piano', 'acoustic', 'folk', 'trip_hop', 'beat_tape')
OLD_WORDS = ('70s', '80s', '90s', '00s', 'early_', 'classic', 'retro', 'disco', 'motown', 'hauntology', 'synthwave', 'city_pop',
             'new_jack', 'g_funk', 'boombap', 'jungle', 'old_school', 'chiptune', 'ps1', 'italo', 'hi_nrg', 'eurodance', 'krautrock')


def era_clash(g, inst):
    """Why `inst` doesn't belong in genre g (or None): brutal bass-music sounds in a gentle genre, modern EDM sounds
    in a pre-2005 / acoustic genre."""
    st = STYLES.get(g) or {}
    name = g.lower()
    if inst in BRUTAL and any(w in name for w in GENTLE_WORDS):
        return 'too brutal for a gentle genre'
    if inst in MODERN_EDM and (any(w in name for w in OLD_WORDS) or st.get('category') in ('Classic', 'Orchestral')):
        return 'a modern EDM sound in an older / acoustic genre'
    return None


ERA_DROPPED = {}


def _era_filter(original):
    for g, pools in POOLS.items():
        own = {t.get('inst') for t in (STYLES.get(g) or {}).get('tracks', [])}
        for role, lst in pools.items():
            keep = []
            for x in lst:
                why = era_clash(g, x) if (x not in (original.get(g, {}).get(role) or []) and x not in own) else None
                if why:
                    ERA_DROPPED.setdefault(g, []).append((role, x, why))
                else:
                    keep.append(x)
            lst[:] = keep


def widen():
    import copy as _copy
    original = _copy.deepcopy(POOLS)
    _widen(original)
    _era_filter(original)


def _widen(original):
    from .instruments import INSTRUMENTS
    for tab in GROUPS.values():
        for scene, genres in tab:
            add = SCENES.get(scene) or {}
            for g in genres:
                if not add and g not in CLUB_GENRE and g not in WORLD and g not in _NEW_188:
                    continue
                pools = POOLS.get(g)
                if not pools or g not in STYLES or STYLES[g].get('exact_pools'):
                    continue                           # (genres modelled on reference records keep their own lists)
                if scene in CLUB or g in CLUB_GENRE or g in WORLD or g in _NEW_188 or (pools.get('bass') or [''])[0] == '808':
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
