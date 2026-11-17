# Studio Lab - technical genre rules (208 genres)

Generated from the code (`sgcore/styles.py` and friends) - this is exactly what the generator follows. Every genre lists its tempo, scales, feel, song form, patterns, sounds and mix.

## How to read the patterns

- **Drum / rhythm patterns** are one bar of 16 steps (16th notes) - or 12 steps in 3/4, 6/8 and 12/8 genres. `X` = accent,
  `x` = normal hit, `o` = ghost note, `.` = rest, `-` = hold. Several patterns per part = the song varies between them.
- **Bass patterns**: `R` = root, `O` = octave, `F` = fifth, `A` = approach note, `b` / `m` = blue / minor notes; `-` holds.
  `bass_mode` `808` = sliding 808, `wobble` = LFO bass (rates are in beats per LFO cycle), `walk` = walking bass.
- **Chord rhythm (`chord_rh`) / lead rhythm (`lead_rh`)** use the same grid; `x` = a chord or melody note starts.
- **Progressions** are scale degrees (0 = I / i, 3 = IV, 4 = V, 5 = vi, 6 = VII ...), one per bar unless `chord_bars` says otherwise.
- **Swing** 0.5 = straight, 0.58 = MPC-style, 0.66 = triplet swing; `swing_unit` 16 = 16ths swing, 8 = 8ths swing.
- **Song form**: section name, bars, which parts play, options (`drop`, `build`, `alt` = alternate progression / sounds,
  `filter_in`, `fade`, `crash`). `form_scale` multiplies bar counts (e.g. 2 at drum & bass tempos).
- **Instruments**: part -> sound (level in dB). "Alternatives" are the sounds the genre may swap in (its own first).
  The part in brackets is its role. A part with the `kick` role that is not called `kick` (timpani, taiko, orchestral bass drum,
  bodhran, tabla ...) is that genre's lowest drum: it takes the kick's place in the beat, the build-ups and the sidechain.
- **Traits**: the twelve high-level rule categories (sgcore/traits.py) - arrangement, density, human feel, melody, bass, drop,
  variation, context, texture, rhythm, harmony, energy curve. Inferred from the rules above unless declared by hand; a song can
  override any of them ("Character" in the app, `--trait category=value` on the command line).
- **Mix**: `lufs` loudness target, `air` / `low` shelf boosts in dB, `width` stereo width, `sc_depth` sidechain pumping.

# Electronic

## House & Disco

### House (`house`)

Classic / NYC house: four-on-the-floor 909, the bouncy M1 organ bass, offbeat piano and organ stabs, warm pads, pumping sidechain

- **Tempo** 120-127 BPM · **scales** minor, dorian · swing 0.55 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 3, 4, 3], [0, 6, 5, 6], [5, 3, 0, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 4], [0, 6, 2, 3]]} · chord_bars 1 · chord size 4
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `.o.o.o.o.o.o.o.o` / `oooooooooooooooo`; **shaker** `o.o.o.o.o.o.o.o.`; **conga** `..o..x.....o.x..` / `......x..x....o.`
- **Drum kit** 909 · preset `909`
- **Bass** `..R...R...R...R.` / `..R..R..O.R...R.` / `..R...R-..R...O.` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x...x.x...x..x` / `...x..x....x..x.` / `x..x..x...x..x..`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x.x.x-..x-x.x-..` / `x-..x.x-..x.x-..` / `..x.x..x..x.x...` / `x--.x--.x-x-x---`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.18
  - ohat (top): `ohat`  dB · pan=0.15
  - chat (top): `chat` -29 dB · pan=-0.2
  - shaker (top): `shaker` -31 dB · pan=0.35
  - bass (bass): `organbass` -13 dB · sc=1.0 · alternatives ['sawbass', 'fmbass', 'moogbass']
  - chords (chords): `m1piano` -18 dB · rev=0.25 · dly=0.15 · sc=0.9 · alternatives ['organ', 'stab', 'epiano']
  - pad (pad): `warmpad` -21 dB · rev=0.35 · sc=1.0 · alternatives ['strings', 'solina', 'glasspad']
  - arp (arp): `organ` -27 dB · pan=-0.25 · rev=0.25 · dly=0.3 · sc=0.8 · alternatives ['stab', 'piano']
  - lead (lead): `m1piano`  dB · pan=0.1 · rev=0.3 · dly=0.3 · sc=0.5 · alternatives ['organ', 'stab', 'epiano']
  - conga (top): `conga` -29 dB · pan=-0.3
- **Mix** {'lufs': -9.0, 'air': 2.0, 'low': 1.0} · reverb 1.8 · sc_depth 0.55
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Deep House (`deep_house`)

Deep house: warm organ & Rhodes 7th chords, round sub, shuffled shakers

- **Tempo** 118-123 BPM · **scales** dorian, minor · swing 0.57 (unit 16) · humanise 0.004
- **Progressions** {'dorian': [[0, 3, 0, 3], [0, 3, 6, 4], [0, 6, 3, 0]], 'minor': [[0, 3, 6, 5], [0, 5, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **rim** `......o.....o..o` / `...o......o.....`; **ohat** `..x...x...x...x.`; **shaker** `oxoxoxoxoxoxoxox`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R.....R...R..O..` / `..R.....R.R...R.` / `R-....R-..R-..A.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x--.......x--...` / `...x--......x-..` / `x-.x--....x-....`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-.x-.x---......` / `..x-x-..x-x-....` / `x-------x-.x----` / `....x-x-x-------`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `groove_locked` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `sub_only` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `modal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap` -21 dB · rev=0.25
  - rim (top): `rim` -30 dB · pan=0.3
  - ohat (top): `ohat` -28 dB · pan=-0.15
  - shaker (top): `shaker` -30 dB · pan=0.25
  - bass (bass): `sinebass`  dB · sc=0.8 · alternatives ['fmbass', 'sf:fingerbass', 'organbass']
  - chords (chords): `epiano`  dB · rev=0.3 · dly=0.15 · sc=0.7 · alternatives ['organ', 'wurli', 'stab', 'piano']
  - pad (pad): `warmpad`  dB · rev=0.4 · sc=0.8 · alternatives ['strings', 'choir', 'glasspad']
  - arp (arp): `epiano` -27 dB · pan=0.2 · rev=0.3 · dly=0.3 · sc=0.5 · alternatives ['piano', 'pluck']
  - lead (lead): `epiano`  dB · rev=0.35 · dly=0.3 · sc=0.4 · alternatives ['sax', 'flute', 'trumpet']
- **Mix** {'lufs': -10.0, 'air': 1.0, 'low': 1.5} · reverb 2.2 · sc_depth 0.35
- **Other rules** {'sc_release': 0.5, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Tech House (`tech_house`)

Tech house: rolling, rubbery filtered bassline, 909 groove with congas, rims and shakers, percussive organ and synth stabs - minimal melody, all groove

- **Tempo** 124-128 BPM · **scales** minor, dorian · swing 0.56 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 0, 0], [0, 0, 5, 6], [0, 3, 0, 3]] · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **shaker** `oxoxoxoxoxoxoxox` / `oxxoxxoxoxxoxxox`; **conga** `..o..x.o...o.x..` / `x..o.x...o.ox...` / `..o.x..o.o..x.o.`; **rim** `...o.......o..o.` / `.o....o..o....o.` / `...o..o....o.o..`; **bongo** `.x.x..x..x.x..xx` / `...x.x.x...x.xx.` / `x.x..x.x.x..x.x.`; **tamb** `..x...x...x...x.` / `..x...x...x.x.x.`
- **Drum kit** 909 · preset `punchy`
- **Bass** `..RR..R...RO..R.` / `..R.R..R..R..RO.` / `.RR..R.R.RR..R..` · mode `pattern` · lowest note 31
- **Chord rhythm** `......x.........` / `...x......x.....`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x.x.....x.x.....` / `..x.x.....x.x...` / `x...x.x.........` / `x.x.x...........`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `groove_locked` · density `dense` · feel `loose_human` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.2
  - ohat (top): `ohat` -27 dB
  - shaker (top): `shaker` -29 dB · pan=0.3
  - conga (top): `conga` -27 dB · pan=-0.3
  - rim (top): `rim` -30 dB · pan=0.2
  - bass (bass): `sawbass`  dB · sc=1.0 · alternatives ['fmbass', 'organbass', 'sinebass']
  - chords (chords): `organ` -24 dB · rev=0.3 · dly=0.3 · sc=0.8 · alternatives ['stab', 'epiano', 'piano']
  - arp (arp): `pluck_saw` -29 dB · pan=0.25 · dly=0.35 · sc=0.6 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `stab`  dB · rev=0.3 · dly=0.35 · sc=0.5 · alternatives ['organ', 'pluck_saw', 'acid']
  - bongo (top): `conga` -29 dB · pan=0.4
  - tamb (top): `tamb` -31 dB · pan=-0.35
- **Mix** {'lufs': -8.5, 'air': 1.5, 'low': 1.5} · reverb 1.6 · sc_depth 0.65
- **Other rules** {'sc_release': 0.4, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.55, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'drum_voice': {'bongo': {'pitch': 380}}}

### Progressive House (`progressive_house`)

Progressive house: emotive plucks, wide supersaws, long builds and big drops

- **Tempo** 122-130 BPM · **scales** minor · swing 0.52 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [5, 3, 0, 4], [0, 6, 5, 3]] · chord_bars 1 · chord size 3
- **Song form** `trance`: intro 16 [bass, kick, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> break 24 [arp, chords, fx, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, pad, top] (build) -> drop 32 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> break 8 [fx, lead, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 16 [bass, kick, top] · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `..o...o...o...o.`
- **Drum kit** 909 · preset `punchy`
- **Bass** `..R...R...R...R.` / `..RO..RO..RO..RO` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x.x.x...` / `x-x-x-..x-x-x-x-` / `x.x.x...x.x.x...` / `x---x---x-------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `melodic_bass` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.3
  - ohat (top): `ohat` -27 dB
  - chat (top): `chat` -30 dB · pan=-0.2
  - ride (top): `ride` -32 dB · pan=0.3
  - bass (bass): `sawbass`  dB · sc=1.0 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `supersaw`  dB · rev=0.35 · sc=1.0 · alternatives ['pluck_saw', 'piano', 'stab', 'polysynth']
  - pad (pad): `warmpad`  dB · rev=0.45 · sc=1.0 · alternatives ['strings', 'supersaw', 'choir', 'glasspad']
  - arp (arp): `pluck_saw` -25 dB · pan=-0.2 · rev=0.3 · dly=0.35 · sc=0.9 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `supersaw_lead`  dB · rev=0.35 · dly=0.25 · sc=0.7 · alternatives ['pluck', 'leadsaw']
- **Mix** {'lufs': -8.5, 'air': 2.0, 'low': 1.0} · reverb 2.6 · sc_depth 0.8
- **Other rules** {'sc_release': 0.5, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slow_chords': 0.35}

### Acid House (`acid_house`)

Acid house: squelching 303 lines, raw 909 drums, rave stabs

- **Tempo** 122-128 BPM · **scales** minor, phrygian · swing 0.53 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 0, 0], [0, 0, 5, 6]] · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `xxxxxxxxxxxxxxxx` / `x.x.x.x.x.x.x.x.`
- **Drum kit** 606 · preset `909`
- **Bass** `R.......R.......` · mode `acid` · lowest note 31
- **Chord rhythm** `x.....x.........` / `...x......x.....`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x.x.x.x.........` / `x...x...x.x.x...` / `..x...x...x...x.` / `x-------........`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.2
  - ohat (top): `ohat` -26 dB
  - chat (top): `chat` -29 dB · pan=0.2
  - bass (bass): `acid` -15 dB · dly=0.2 · sc=0.6 · alternatives ['sawbass', 'moogbass', 'fmbass']
  - chords (chords): `stab` -25 dB · rev=0.3 · dly=0.3 · alternatives ['organ', 'piano', 'polysynth']
  - pad (pad): `warmpad` -28 dB · rev=0.4 · alternatives ['strings', 'glasspad', 'choir']
  - arp (arp): `pluck_saw` -28 dB · pan=-0.25 · dly=0.4 · alternatives ['acid', 'pluck', 'stab']
  - lead (lead): `acid` -22 dB · rev=0.3 · alternatives ['stab', 'hoover', 'leadsaw']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 1.0} · reverb 1.2 · sc_depth 0.4
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Big Room (`bigroom`)

Big room / festival EDM: huge kicks, massive drops, stabby supersaw leads

- **Tempo** 126-130 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 0, 5, 6], [5, 6, 0, 0]] · chord_bars 1 · chord size 3
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** (synth preset) · preset `hard`
- **Bass** `..R...R...R...R.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x...x.x.x...x.` / `x..x..x.x.......` / `x.x.x.x.x.x.x.x.` / `x...x...x-------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `festival_mainstage` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.35
  - ohat (top): `ohat` -26 dB
  - chat (top): `chat` -29 dB
  - bass (bass): `fmbass`  dB · sc=1.0 · alternatives ['sawbass', 'reese', 'moogbass']
  - chords (chords): `supersaw`  dB · rev=0.4 · sc=1.0 · alternatives ['stab', 'pluck_saw', 'polysynth']
  - pad (pad): `warmpad`  dB · rev=0.5 · sc=1.0 · alternatives ['supersaw', 'choir', 'strings']
  - arp (arp): `pluck_saw` -27 dB · pan=0.25 · dly=0.35 · sc=0.8 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `hoover` -17 dB · rev=0.4 · sc=0.6 · alternatives ['supersaw_lead', 'leadsaw', 'pluck_saw']
- **Mix** {'lufs': -7.5, 'air': 2.0, 'low': 1.5} · reverb 2.8 · sc_depth 0.9
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 4.0, 'decay': 5}}, 'snare_tracks': ['clap'], 'bass_gate': 0.5, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Eurodance (`eurodance`)

90s eurodance: driving four-on-the-floor, offbeat bass, piano stabs, big anthemic leads

- **Tempo** 134-142 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 5, 3, 4], [5, 3, 0, 4]] · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `....x.......x...`
- **Drum kit** 909 · preset `909`
- **Bass** `..R...R...R...R.` / `.RR..RR..RR..RR.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x..x..x...x..x..` / `x.x...x.x.x...x.`
- **Arp** {'rate': 1, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x-x-x---x-x-` / `x--x--x-x-------` / `x-x-x---x-x-x---` / `x-------x-------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `groove_locked` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.2
  - ohat (top): `ohat` -26 dB
  - chat (top): `chat` -29 dB
  - tamb (top): `tamb` -29 dB
  - bass (bass): `sawbass`  dB · sc=0.6 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `piano`  dB · rev=0.25 · sc=0.4 · alternatives ['stab', 'supersaw', 'organ', 'polysynth', 'm1piano']
  - pad (pad): `strings` -26 dB · rev=0.4 · sc=0.6 · alternatives ['warmpad', 'choir', 'solina']
  - arp (arp): `pluck_saw` -27 dB · dly=0.3 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `supersaw_lead`  dB · rev=0.35 · sc=0.4 · alternatives ['leadsaw', 'pluck_saw']
- **Mix** {'lufs': -9.0, 'air': 2.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.4
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Afro House (`afro_house`)

Afro house: four-on-the-floor with rolling congas and shakers, deep bass, kalimba & marimba hooks, chants

- **Tempo** 118-124 BPM · **scales** minor, dorian · swing 0.54 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 6, 5, 6], [0, 3, 0, 3], [0, 5, 6, 0]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **shaker** `xxxxxxxxxxxxxxxx`; **conga** `..o.x..o..o.x.o.` / `x..o..x.o..x..o.`; **woodblock** `..x.....x.x.....`; **ohat** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R..R....R..R....` / `..R...R...R..R..` / `R-..R-..R-..R-..` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------x-----` / `..x.....x.......` / `x--.....x--.....`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x.x..x.x..x.....` / `..x.x..x..x.x...` / `x--x--x-x-------` / `x---x---x-x-----`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `sub_only` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - clap (snare): `clap` -21 dB · rev=0.3
  - shaker (top): `shaker` -27 dB · pan=0.3
  - conga (top): `conga` -23 dB · pan=-0.25
  - woodblock (top): `woodblock` -29 dB · pan=0.2
  - ohat (top): `ohat` -28 dB
  - bass (bass): `sinebass` -13 dB · sc=0.5 · alternatives ['fmbass', 'sawbass', '808']
  - chords (chords): `warmpad` -24 dB · rev=0.4 · sc=0.5 · alternatives ['epiano', 'piano', 'organ', 'stab']
  - pad (pad): `choir` -28 dB · rev=0.5 · alternatives ['warmpad', 'strings']
  - arp (arp): `kalimba` -24 dB · rev=0.3 · dly=0.3 · alternatives ['marimba', 'pluck', 'steeldrum']
  - lead (lead): `marimba` -19 dB · rev=0.3 · dly=0.25 · alternatives ['kalimba', 'flute', 'pluck', 'sax']
- **Mix** {'lufs': -9.5, 'air': 1.4, 'low': 1.6} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.7, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Kalimba / marimba (hooks); Congas, shakers; Deep bass; Pads; Vocal chants

### Melodic Deep House (`melodic_house`)

Melodic deep house: warm rolling bassline, organic shakers and congas, emotive piano and plucked melodies over lush pads, gentle and euphoric

- **Tempo** 118-124 BPM · **scales** minor, major, dorian · swing 0.53 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 6, 5, 3], [5, 3, 0, 4]], 'major': [[0, 4, 5, 3], [3, 0, 4, 5], [5, 3, 0, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `melodic_house`: intro 16 [chords, fx, pad] (filter_in) -> intro 16 [arp, chords, fx, pad] -> verse 12 [arp, bass, chords, kick, pad] -> drop 28 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 24 [chords, fx, lead, pad, top] (alt) -> build 8 [arp, chords, fx, pad] (build) -> verse 16 [arp, bass, chords, kick, lead, pad] (alt) -> drop 24 [arp, bass, chords, kick, lead, pad, snare, top] (drop, alt) -> outro 8 [bass, kick, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **shaker** `x.xxx.xxx.xxx.xx`; **conga** `......o.......o.` / `..o.....o.o.....`; **ohat** `..x...x...x...x.`; **rim** `...x......x.....`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R..R..R.R..R..R.` / `..R...R...R..R..` / `R-..R-..R-..R-..` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `..x-x-x-x---x---` / `x--x--x-x-------`
- **Build-ups** default `filter` · choices ['drumless', 'filter', 'none']
- **Traits** arrangement `groove_locked` · density `dense` · feel `tight_swing` · melody `long_lyrical` · bass `melodic_bass` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - clap (snare): `clap` -21 dB · rev=0.35
  - shaker (top): `shaker` -27 dB · pan=0.3
  - conga (top): `conga` -26 dB · pan=-0.25
  - ohat (top): `ohat` -28 dB
  - rim (top): `rim` -29 dB · pan=0.2
  - bass (bass): `moogbass` -15 dB · sc=0.6 · alternatives ['sinebass', 'sawbass', 'sf:fingerbass']
  - chords (chords): `warmpad` -24 dB · rev=0.5 · sc=0.5 · alternatives ['piano', 'polysynth', 'epiano', 'strings']
  - pad (pad): `glasspad` -27 dB · rev=0.5 · sc=0.5 · alternatives ['strings', 'warmpad', 'choir', 'solina']
  - arp (arp): `harp` -25 dB · pan=0.25 · rev=0.4 · dly=0.3 · alternatives ['pluck', 'guitar', 'pizz']
  - lead (lead): `piano` -18 dB · rev=0.4 · dly=0.2 · alternatives ['pluck', 'guitar', 'sf:nylon', 'violin', 'flute']
  - texture (fx): `texture` -38 dB · rev=0.5
- **Mix** {'lufs': -9.5, 'air': 1.6, 'low': 1.3} · reverb 2.0 · sc_depth 0.35
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.65, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Felt / grand piano; Plucked guitar or harp; Lush pads; Rolling bass; Shakers, congas; field-recording textures

### Organic Melodic House (`organic_house`)

Organic melodic deep house: warm four-on-the-floor with shakers and congas, piano, flute and soft strings, nature-like atmosphere - spacious, hypnotic and simple, no big drops

- **Tempo** 120-124 BPM · **scales** minor, dorian, major · swing 0.53 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]], 'major': [[0, 4, 5, 3], [3, 0, 4, 0]]} · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **shaker** `x.xxx.xxx.xxx.xx` / `x.x.x.x.x.x.x.x.`; **conga** `......o.......o.` / `..o.....o.o.....` / `...o..o....o..o.`; **ohat** `..x...x...x...x.`; **rim** `...x......x.....`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R..R..R.R..R..R.` / `R-..R-..R-..R-..` / `..R...R...R..R..` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x-x-x-------` / `x-------x---x---` / `x---x---x-x-x---` / `..x-x-x-x-------`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `groove_locked` · density `dense` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - clap (snare): `clap` -22 dB · rev=0.35
  - shaker (top): `shaker` -28 dB · pan=0.3
  - conga (top): `conga` -26 dB · pan=-0.25
  - ohat (top): `ohat` -29 dB
  - rim (top): `rim` -30 dB · pan=0.2
  - bass (bass): `sinebass` -14 dB · sc=0.5 · alternatives ['moogbass', 'upright', '808']
  - chords (chords): `piano` -23 dB · rev=0.5 · alternatives ['epiano', 'warmpad', 'guitar', 'strings']
  - pad (pad): `strings` -28 dB · rev=0.6 · sc=0.4 · alternatives ['glasspad', 'warmpad', 'choir', 'solina']
  - arp (arp): `harp` -26 dB · pan=0.25 · rev=0.45 · dly=0.3 · alternatives ['pluck', 'guitar', 'marimba', 'kalimba']
  - lead (lead): `flute` -20 dB · rev=0.45 · dly=0.25 · alternatives ['violin', 'pluck', 'sf:nylon', 'cello']
  - texture (fx): `texture` -36 dB · rev=0.5
- **Mix** {'lufs': -10.0, 'air': 1.6, 'low': 1.2} · reverb 2.6 · sc_depth 0.3
- **Other rules** {'sc_release': 0.5, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.7, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.8, 'simplicity': 0.35}
- **Sound brief** Grand / felt piano; flute; soft strings; harp or plucked guitar; shakers and congas; nature field recordings

### Italo Disco (`italo_disco`)

Italo disco / Eurodisco (early-mid 80s): four-on-the-floor with a gated-reverb snare on 2 and 4, a melodic octave synth bassline, bright Juno / Jupiter / DX7 arps and anthemic leads - cleaner and more synthetic than disco

- **Tempo** 116-126 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 3, 6, 5], [0, 5, 3, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **ohat** `..x...x...x...x.`; **tamb** `....x.......x...`
- **Drum kit** linn · preset `linn`
- **Bass** `R.O.R.O.R.O.R.O.` / `R.O.R.R.O.R.O.R.` / `RRO.RRO.RRO.RRO.` · mode `pattern` · lowest note 33
- **Chord rhythm** `x-------x-------` / `x---x---x---x---`
- **Arp** {'rate': 1, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x---x-x-x-x-` / `x-x-x-x-x-------` / `x-------x---x-x-`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `groove_locked` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -28 dB
  - tamb (top): `tamb` -30 dB · pan=-0.3
  - bass (bass): `sawbass` -14 dB · sc=0.3 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `polysynth` -24 dB · rev=0.35 · alternatives ['synthbrass', 'epiano', 'm1piano']
  - pad (pad): `solina` -28 dB · rev=0.5 · alternatives ['strings', 'choir', 'warmpad']
  - arp (arp): `pluck_saw` -27 dB · pan=0.25 · dly=0.3 · alternatives ['chip', 'pluck', 'stab']
  - lead (lead): `leadsaw` -19 dB · rev=0.4 · dly=0.3 · alternatives ['synthbrass', 'polysynth', 'supersaw_lead']
- **Mix** {'lufs': -10.0, 'air': 2.0, 'low': 0.8} · reverb 2.0 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.55, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.75}
- **Sound brief** Juno / Jupiter octave bass; DX7 / PPG brass and bells; bright saw lead; vocoder; LinnDrum with gated snare

### Future Funk (`future_funk`)

Future funk: pitched-up, chopped 70s/80s disco and city-pop flavour over a swung four-on-the-floor with heavy sidechain pumping - funky bass, filter sweeps, vocal chops; bright and nostalgic

- **Tempo** 115-126 BPM · **scales** major, dorian · swing 0.57 (unit 16) · humanise 0.0
- **Progressions** {'major': [[3, 2, 1, 4], [1, 4, 0, 5], [3, 4, 2, 5]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]]} · chord_bars 1 · chord size 4
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.xxx.xxx.xxx.xx`; **tamb** `....x.......x...`
- **Drum kit** 909 · preset `909`
- **Bass** `R..O.R...RR.O..A` / `R.R..O.R..R.O.R.` / `R..O..R.R.O..R.A` · mode `pattern` · lowest note 31
- **Chord rhythm** `x..x..x.x..x..x.` / `.x.x..x..x.x..x.`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x...x.x.x...` / `..x.x.x...x.x...` / `x.xx.x..x.xx.x..`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `tension_release` · density `medium` · feel `loose_human` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -18 dB · rev=0.25
  - ohat (top): `ohat` -27 dB
  - chat (top): `chat` -29 dB · pan=0.2
  - tamb (top): `tamb` -30 dB · pan=-0.3
  - bass (bass): `ebass` -14 dB · sc=0.7 · alternatives ['sf:slapbass', 'moogbass', 'sf:fingerbass']
  - chords (chords): `epiano` -22 dB · rev=0.3 · sc=0.9 · alternatives ['polysynth', 'sf:cleanguitar', 'synthbrass']
  - pad (pad): `strings` -27 dB · rev=0.4 · sc=0.8 · alternatives ['solina', 'warmpad', 'sf:slowstrings']
  - arp (arp): `vox` -23 dB · dly=0.25 · sc=0.6 · alternatives ['mutedgtr', 'epiano', 'phonkbell']
  - lead (lead): `vox` -19 dB · rev=0.3 · sc=0.5 · alternatives ['synthbrass', 'sax', 'leadsaw']
- **Mix** {'lufs': -8.5, 'air': 2.4, 'low': 1.0} · reverb 2.0 · sc_depth 0.85
- **Other rules** {'sc_release': 0.3, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.5, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Melodic deep house (sunny, piano & strings) (`sunny_melodic_house`)

Sunny melodic deep house: warm 122-124 four-on-the-floor with shakers, congas and offbeat hats, a melodic rolling bass, bright piano chords and plucks, lush strings and a singing lead, long filtered breakdowns that open into big emotional returns

- **Tempo** 121-124 BPM · **scales** minor, dorian, major · swing 0.52 (unit 16) · humanise 0.003
- **Progressions** {'minor': [[0, 5, 2, 6], [5, 3, 0, 6], [0, 3, 5, 4], [3, 6, 0, 5]], 'dorian': [[0, 3, 0, 6], [0, 6, 3, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4], [3, 4, 0, 5]]} · chord_bars 1 · chord size 4
- **Song form** `melodic_house_radio`: intro 8 [arp, chords, fx, pad] (filter_in) -> intro 8 [arp, chords, fx, pad, top] -> verse 4 [bass, chords, kick, pad] -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> verse 8 [arp, bass, chords, kick, snare, top] -> break 12 [chords, fx, lead, pad, top] (alt) -> build 4 [bass, chords, kick, pad] (build) -> drop 24 [arp, bass, chords, kick, lead, pad, snare, top] (drop, alt) -> outro 4 [arp, chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `.o.o.o.o.o.o.o.o` / `oxoxoxoxoxoxoxox`; **shaker** `oxxoxxoxoxxoxxox` / `x.xxx.xxx.xxx.xx`; **conga** `..o..x.o...o.x..` / `x..o..x...o..x..`; **rim** `...o.......o....` / `......o.......o.`
- **Drum kit** 909 · preset `909`
- **Bass** `..R..R.O..R..R.O` / `.RR..R.R.RR..R.O` / `..R.R..R..R.R.RO` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x...x...x...x.` / `x--...x-..x-..x.` / `..x.x...x.x...x.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x-x-x---` / `..x-x-x-x-------` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['drumless', 'filter', 'pickup']
- **Traits** arrangement `groove_locked` · density `dense` · feel `tight_swing` · melody `long_lyrical` · bass `melodic_bass` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - clap (snare): `clap` -20 dB · rev=0.3
  - ohat (top): `ohat` -26 dB · pan=0.15
  - chat (top): `chat` -30 dB · pan=-0.2
  - shaker (top): `shaker` -30 dB · pan=0.35
  - conga (top): `conga` -29 dB · pan=-0.35
  - rim (top): `rim` -31 dB · pan=0.25
  - bass (bass): `moogbass` -14 dB · sc=0.9 · alternatives ['sinebass', 'sawbass', 'sf:fingerbass']
  - chords (chords): `piano` -21 dB · rev=0.3 · dly=0.15 · sc=0.7 · alternatives ['m1piano', 'epiano', 'pluck_saw']
  - pad (pad): `strings` -24 dB · rev=0.5 · sc=0.6 · alternatives ['warmpad', 'glasspad', 'solina']
  - arp (arp): `pluck_saw` -27 dB · pan=-0.25 · rev=0.35 · dly=0.4 · sc=0.6 · alternatives ['pluck', 'marimba', 'bell']
  - lead (lead): `pluck` -20 dB · pan=0.1 · rev=0.45 · dly=0.35 · sc=0.4 · alternatives ['flute', 'pluck_saw', 'marimba']
  - texture (fx): `texture` -38 dB
- **Mix** {'lufs': -9.0, 'air': 1.4, 'low': 1.4} · reverb 2.6 · sc_depth 0.5
- **Other rules** {'sc_release': 0.42, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 50, 'punch': 120, 'decay': 8, 'drive': 1.6, 'click': 0.3}}, 'snare_tracks': ['clap'], 'bass_gate': 0.7, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.75}
- **Sound brief** Warm 909 kick, shakers, congas; rolling melodic bass (Moog / sine); bright piano; lush string pad; delayed pluck arp; singing lead (piano, pluck, flute)

### 90s club house (New York) (`nineties_club_house`)

90s club house (mid-90s New York): a punchy, swung 909 / sampled-drum groove with shuffled hats and tambourine, a deep driving bass, short filtered minor chord stabs bouncing on the offbeats, a touch of organ - minimal, hypnotic and made for the floor

- **Tempo** 122-126 BPM · **scales** minor, dorian · swing 0.58 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 0, 5, 5], [0, 5, 3, 4], [0, 0, 6, 6]], 'dorian': [[0, 3, 0, 3], [0, 0, 6, 3]]} · chord_bars 1 · chord size 4
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X.......X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `xxxxxxxxxxxxxxxx` / `x.xxx.xxx.xxx.xx`; **tamb** `..x...x...x...x.` / `xxxxxxxxxxxxxxxx`; **rim** `...x.....x....x.` / `......x..x......`
- **Drum kit** 909 · preset `909`
- **Bass** `..R...R...R...R.` / `R.R...R.R.R...R.` / `..R..R..R.R..R..` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x..x....x..x..` / `...x..x....x..x.` / `..x...x.x.x...x.`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-------........` / `x---....x---....` / `........x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `groove_locked` · density `dense` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -19 dB · rev=0.15
  - clap (snare): `clap` -20 dB · rev=0.2
  - ohat (top): `ohat` -25 dB · pan=0.15
  - chat (top): `chat` -29 dB · pan=-0.2
  - tamb (top): `tamb` -28 dB · pan=0.3
  - rim (top): `rim` -30 dB · pan=-0.3
  - bass (bass): `sinebass` -12 dB · sc=0.8 · alternatives ['moogbass', 'organbass', '808']
  - chords (chords): `stab` -21 dB · rev=0.3 · dly=0.25 · sc=0.6 · alternatives ['warmpad', 'organ', 'm1piano']
  - pad (pad): `warmpad` -29 dB · rev=0.4 · sc=0.8 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `organ` -28 dB · pan=0.25 · rev=0.25 · dly=0.3 · sc=0.6 · alternatives ['stab', 'm1piano', 'twang']
  - lead (lead): `organ` -24 dB · rev=0.3 · dly=0.3 · sc=0.4 · alternatives ['stab', 'epiano']
- **Mix** {'lufs': -10.0, 'air': 1.4, 'low': 1.3} · reverb 1.6 · sc_depth 0.45
- **Other rules** {'sc_release': 0.4, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 52, 'punch': 150, 'decay': 8, 'drive': 2.4, 'click': 0.5}, 'snare': {'tone': 200, 'snap': 1.4, 'decay': 14}}, 'snare_tracks': ['clap'], 'bass_gate': 0.55, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** 909 / sampled kick, snare + clap; swung 16th hats; tambourine; deep sub / Moog bass; short filtered pad stabs (minor 7ths); organ hits

### Bass house / UK bass (`bass_house`)

Bass house / UK bass: a punchy four-on-the-floor around 126 with shuffled hats, a fat, distorted, talking bassline that wobbles and bends in the gaps between kicks, stabby organ / rave chords and vocal-chop style hooks; tops-only intro, short stop-start drops and a long drums-out breakdown before the last drop

- **Tempo** 124-128 BPM · **scales** minor, phrygian · swing 0.54 (unit 16) · humanise 0.003
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 6], [0, 6, 0, 5]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 0]]} · chord_bars 1 · chord size 3
- **Song form** `bass_house`: intro 16 [chords, fx, top] (filter_in) -> build 4 [fx, top] (build) -> drop 8 [bass, fx, kick, snare, top] (drop) -> break 4 [chords, top] -> drop 24 [bass, chords, fx, kick, lead, snare, top] (crash) -> break 16 [chords, fx, pad, top] (alt) -> build 8 [chords, fx, top] (build) -> drop 32 [bass, chords, fx, kick, lead, snare, top] (drop, alt) -> outro 8 [fx, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.xxx.xxx.xxx.xx` / `x.x.x.xxx.x.x.xx`; **snare** `................` / `..............x.`
- **Drum kit** (synth preset) · preset `909`
- **Bass** `..R-.R..R.R-.R..` / `.R-.R-..R-..R-.O` / `..R..R-...R-.R-.` · mode `wobble` · lowest note 31
- **Chord rhythm** `..x...x...x...x.` / `x..x..x...x.....` / `...x..x....x..x.`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.35}
- **Lead rhythm** `x.x..x.x..x.....` / `..x.x..x.x......` / `x..x..x.x.x.....`
- **Build-ups** default `(category default)` · choices ['pause', 'filter', 'none'] · transitions ['gap', 'none', 'crash']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `rhythmic_stabs` · bass `wobble_modulated` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - clap (snare): `clap` -16 dB · rev=0.2
  - snare (snare): `snare` -20 dB
  - chat (top): `chat` -27 dB · pan=0.15
  - ohat (top): `ohat` -28 dB · pan=-0.15
  - bass (bass): `wobble` -11 dB · sc=0.8 · alternatives ['fmbass', 'growl', 'reese']
  - chords (chords): `organ` -22 dB · rev=0.25 · sc=0.6 · alternatives ['stab', 'm1piano', 'epiano']
  - pad (pad): `warmpad` -30 dB · rev=0.4 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `stab` -28 dB · dly=0.25 · alternatives ['pluck', 'pluck_saw', 'organ']
  - lead (lead): `stab` -20 dB · rev=0.25 · dly=0.25 · alternatives ['pluck', 'pluck_saw', 'organ']
- **Mix** {'lufs': -8.5, 'air': 1.2, 'low': 2.2, 'width': 0.6} · reverb 1.6 · sc_depth 0.6
- **Other rules** {'sc_release': 0.22, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 50, 'punch': 140, 'decay': 9, 'drive': 2.2, 'click': 0.6}}, 'snare_tracks': ['clap', 'snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'wobble_rates': [0.5, 0.5, 0.25, 1], 'wobble_rates_alt': [0.25, 0.5, 0.3333333333333333], 'wobble_lens': [2, 2, 4, 4, 8]}
- **Sound brief** Punchy 909 kick + clap, shuffled hats; distorted FM / wobble bass in the gaps (sidechained); organ / rave stabs; vocal-chop style lead; build-ups by taking everything out but the hats

### Nu-disco / disco lounge (`nu_disco`)

Nu-disco / disco lounge: a warm four-on-the-floor around 112-120 with open hats and claps, a bouncy octave / syncopated disco bassline, filtered funky guitar and Rhodes chords, lush strings and a sweet synth or sax hook - groovy, sunny and a little hazy

- **Tempo** 110-122 BPM · **scales** minor, dorian, major · swing 0.53 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 3, 0, 3], [0, 5, 3, 4], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 1, 0, 3]], 'major': [[1, 4, 0, 5], [3, 4, 2, 5]]} · chord_bars 1 · chord size 4
- **Song form** `nu_disco`: intro 8 [bass, chords, kick] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 32 [bass, chords, kick, lead, pad, snare, top] (crash) -> break 8 [bass, chords, kick] (alt) -> build 8 [bass, chords, kick, pad, top] (build) -> chorus 32 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.` / `xxx.xxx.xxx.xxx.`; **shaker** `.x.x.x.x.x.x.x.x`; **tamb** `....x.......x...`
- **Drum kit** 909 · preset `909`
- **Bass** `R.O.R.O.R.O.R.O.` / `R..O..R.R..O..R.` / `R.R.O.R..R.RO.R.` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x...x...x...x.` / `x.x..x.x..x.x...` / `.x.x.x.x.x.x.x.x`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-x-x-------` / `..x-x-x-x---x---` / `x-x-....x-x-x---`
- **Build-ups** default `(category default)` · choices ['filter', 'pause', 'pickup']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -17 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -27 dB · pan=-0.2
  - shaker (top): `shaker` -32 dB · pan=0.3
  - tamb (top): `tamb` -31 dB · pan=-0.3
  - bass (bass): `moogpluck` -13 dB · sc=0.4 · alternatives ['sf:fingerbass', 'fmbass', 'sawbass']
  - chords (chords): `mutedgtr` -23 dB · pan=0.25 · sc=0.4 · alternatives ['epiano', 'clav', 'polysynth']
  - pad (pad): `strings` -27 dB · rev=0.4 · alternatives ['solina', 'warmpad', 'sf:slowstrings']
  - arp (arp): `epiano` -27 dB · pan=-0.25 · dly=0.2 · alternatives ['pluck', 'vibes', 'piano']
  - lead (lead): `polysynth` -19 dB · rev=0.3 · dly=0.25 · alternatives ['sax', 'synthbrass', 'softlead']
- **Mix** {'lufs': -9.5, 'air': 1.2, 'low': 1.6, 'width': 1.0} · reverb 2.0 · sc_depth 0.4
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.006, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** 909 four-on-the-floor + claps + open hats; octave disco bass (slap / synth); muted funk guitar + Rhodes; string section; synth or sax hook

### Garage-house pop (`garage_house`)

Garage-house pop (2010s UK): a 2-step garage beat at house tempo (~122) with shuffled hats and skippy kicks, a wonky, syncopated sub-and-organ bassline, warm stabby chords and a soulful hook - poppy, groovy and deep at once

- **Tempo** 120-124 BPM · **scales** minor, dorian, major · swing 0.58 (unit 16) · humanise 0.003
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 3, 5, 4]], 'dorian': [[0, 3, 0, 3]], 'major': [[0, 4, 5, 3], [3, 4, 0, 5]]} · chord_bars 1 · chord size 4
- **Song form** `garage_house`: verse 24 [bass, chords, kick, snare, top] -> break 4 [chords, fx, top] -> break 8 [bass, chords, fx, top] (build) -> chorus 32 [bass, chords, kick, lead, pad, snare, top] (drop) -> bridge 8 [chords, fx, pad, top] (alt) -> chorus 20 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 24 [bass, chords, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X......X..X.....` / `X...X...X...X...`; **snare** `....X.......X...` / `....X......X.X..`; **chat** `.xox.xox.xox.xox` / `x.xxx.xxx.xxx.xx`; **shaker** `o.o.o.o.o.o.o.o.`; **rim** `...x......x.....`
- **Drum kit** punchy · preset `punchy`
- **Bass** `R-..R..R.-R..O..` / `..R-..R-..R-.R..` / `R-....R-..R..O..` · mode `pattern` · lowest note 29
- **Chord rhythm** `..x..x....x..x..` / `x..x..x...x.....`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x.x..x.x..x.....` / `..x.x..x.x......` / `x---x-x-x-------`
- **Build-ups** default `(category default)` · choices ['pause', 'filter', 'stops'] · transitions ['gap', 'none', 'crash']
- **Traits** arrangement `groove_locked` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - shaker (top): `shaker` -31 dB · pan=-0.3
  - rim (top): `rim` -29 dB
  - bass (bass): `organbass` -12 dB · sc=0.6 · alternatives ['sinebass', 'fmbass', 'moogbass']
  - chords (chords): `stab` -22 dB · rev=0.3 · sc=0.5 · alternatives ['organ', 'epiano', 'piano']
  - pad (pad): `warmpad` -28 dB · rev=0.45 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `epiano` -28 dB · dly=0.3 · alternatives ['pluck', 'piano', 'vibes']
  - lead (lead): `softlead` -19 dB · rev=0.3 · dly=0.3 · alternatives ['epiano', 'flute']
- **Mix** {'lufs': -9.0, 'air': 1.4, 'low': 1.8, 'width': 0.9} · reverb 2.0 · sc_depth 0.45
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.75, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** 2-step garage kit at 122, shuffled hats; wonky sub / organ bass; warm chord stabs; soulful vocal-style lead

### 90s Italo piano house (`piano_house_90s`)

Late-80s / early-90s Italo piano house: a clunky drum-machine four-on-the-floor around 120 with a busy, sampled-sounding hip-house break on top, big bright stabbing piano chords, a bouncy octave synth bass, and a soulful diva-style hook - raw, joyful and very Euro-club

- **Tempo** 118-124 BPM · **scales** major, minor · swing 0.52 (unit 16) · humanise 0.003
- **Progressions** {'major': [[0, 5, 3, 4], [0, 4, 5, 3], [1, 4, 0, 0]], 'minor': [[0, 6, 5, 6], [0, 5, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `piano_house_90s`: intro 8 [bass, chords, kick] -> verse 32 [bass, chords, kick, lead, snare, top] -> break 8 [bass, chords, kick] (alt) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> break 8 [bass, chords, kick, pad] (build) -> chorus 32 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 16 [bass, chords, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X..X....X.......` / `X..XX...X.......` / `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.xxx.xxx.xxx.xx`; **tamb** `....x.......x...`
- **Drum kit** 909 · preset `909`
- **Bass** `R.O.R.O.R.O.R.O.` / `R..R..O.R..R..O.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x..x..x...x..x..` / `x.x..x.x..x..x..` / `..x...x...x...x.`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x-x-....`
- **Build-ups** default `(category default)` · choices ['pickup', 'filter', 'stops'] · transitions ['crash', 'none', 'none']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -15 dB · rev=0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - ohat (top): `ohat` -27 dB · pan=-0.2
  - tamb (top): `tamb` -30 dB · pan=0.3
  - bass (bass): `sawbass` -13 dB · sc=0.3 · alternatives ['moogbass', 'organbass', 'fmbass']
  - chords (chords): `m1piano` -18 dB · rev=0.25 · alternatives ['piano', 'organ', 'epiano']
  - pad (pad): `strings` -27 dB · rev=0.4 · alternatives ['solina', 'warmpad', 'sf:slowstrings']
  - arp (arp): `stab` -28 dB · dly=0.2 · alternatives ['pluck', 'pluck_saw', 'organ']
  - lead (lead): `piano` -19 dB · rev=0.3 · dly=0.2 · alternatives ['softlead', 'epiano', 'vibes']
- **Mix** {'lufs': -9.5, 'air': 1.6, 'low': 1.4, 'width': 0.9} · reverb 2.0 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.55, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** 909 / Linn kick + claps, a sampled funk break on top; M1-style house piano stabs; octave synth bass; diva hook

### Tokyo deep house (`tokyo_deep_house`)

Tokyo deep house / city house: a clean four-on-the-floor around 122 with brushed shakers and offbeat hats, a melodic, walking deep-house bass, jazzy Rhodes and piano chords with 9ths and 11ths, airy strings and a breathy melody - elegant, nocturnal and urban

- **Tempo** 120-125 BPM · **scales** minor, dorian, major · swing 0.53 (unit 16) · humanise 0.003
- **Progressions** {'minor': [[0, 5, 3, 4], [5, 3, 0, 6], [0, 3, 6, 2]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 4]], 'major': [[3, 4, 2, 5], [1, 4, 0, 5]]} · chord_bars 1 · chord size 4
- **Song form** `tokyo_deep_house`: intro 12 [chords, fx, pad] (filter_in) -> intro 8 [bass, chords, kick, pad] -> verse 12 [bass, chords, kick, snare, top] -> break 4 [chords, pad, top] -> chorus 36 [bass, chords, kick, lead, pad, snare, top] (crash) -> break 12 [chords, fx, pad, top] (alt) -> verse 12 [arp, bass, chords, kick, snare, top] -> break 4 [chords, top] -> chorus 32 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.xxx.xxx.xxx.xx`; **shaker** `.x.x.x.x.x.x.x.x`; **rim** `...x......x.....`
- **Drum kit** 909 · preset `909`
- **Bass** `R..R.O..R..F.O..` / `R.R..O.R..R..O.R` / `R...O..RF...O...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x--x--x-..x-....` / `..x-..x-..x-..x-` / `x-------..x-x-..`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.45}
- **Lead rhythm** `x---x-x-x-------` / `..x-x---x-x-....` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['pause', 'filter', 'none'] · transitions ['none', 'gap', 'none']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -18 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -28 dB · pan=-0.2
  - shaker (top): `shaker` -31 dB · pan=0.3
  - rim (top): `rim` -30 dB · pan=-0.3
  - bass (bass): `moogbass` -13 dB · sc=0.4 · alternatives ['sinebass', 'sf:fingerbass', 'fmbass']
  - chords (chords): `epiano` -21 dB · rev=0.35 · alternatives ['piano', 'polysynth', 'wurli']
  - pad (pad): `strings` -27 dB · rev=0.45 · alternatives ['warmpad', 'solina', 'sf:slowstrings']
  - arp (arp): `piano` -27 dB · dly=0.25 · alternatives ['vibes', 'pluck', 'epiano']
  - lead (lead): `softlead` -20 dB · rev=0.4 · dly=0.3 · alternatives ['sax', 'flute']
- **Mix** {'lufs': -9.5, 'air': 1.4, 'low': 1.6, 'width': 1.0} · reverb 2.6 · sc_depth 0.35
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Clean 909 / acoustic-ish house kit, shakers; melodic deep bass; Rhodes / piano with 9ths + 11ths; strings; a soft breathy lead

### Mallet melodic house (`mallet_house`)

Mallet-led melodic house / IDM-house: interlocking marimba, vibraphone and kalimba patterns in odd groupings over a deep, rolling four-on-the-floor around 120, a round sub bass, soft pads and a slowly unfolding melody - intricate, organic and hypnotic, with long beatless openings where the mallets build up one layer at a time

- **Tempo** 116-124 BPM · **scales** minor, dorian, major, lydian · swing 0.53 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 6, 3, 4]], 'dorian': [[0, 3, 0, 6], [0, 1, 0, 3]], 'major': [[0, 4, 5, 3]], 'lydian': [[0, 1, 0, 1]]} · chord_bars 1 · chord size 4
- **Song form** `mallet_house`: intro 16 [arp, fx, pad] (filter_in) -> build 8 [arp, bass, chords, fx, pad] (build) -> drop 8 [arp, bass, chords, kick, snare, top] (drop) -> break 12 [arp, chords, pad, top] -> verse 32 [arp, bass, chords, kick, lead, snare, top] (crash) -> break 8 [arp, bass, fx, pad] (alt) -> build 8 [arp, chords, fx, pad, top] (build) -> drop 48 [arp, bass, chords, kick, lead, pad, snare, top] (drop, alt) -> outro 16 [arp, fx, pad] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...` / `X...X...X...X..x`; **clap** `........X.......` / `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.xxx.xxx.xxx.xx`; **shaker** `.x.x.x.x.x.x.x.x`; **conga** `..o..x.o...o.x..`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R-------..R-....` / `R---..R-R-------` · mode `pattern` · lowest note 29
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.95}
- **Lead rhythm** `x---x-x-x-------` / `..x-x---x-x-....` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['filter', 'drumless', 'none', 'pickup']
- **Traits** arrangement `groove_locked` · density `dense` · feel `tight_swing` · melody `long_lyrical` · bass `sub_only` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -18 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - shaker (top): `shaker` -32 dB · pan=0.3
  - conga (top): `conga` -28 dB · pan=-0.3
  - bass (bass): `sinebass` -12 dB · sc=0.4 · alternatives ['moogbass', '808', 'reese']
  - chords (chords): `warmpad` -26 dB · rev=0.5 · alternatives ['epiano', 'strings', 'solina']
  - pad (pad): `glasspad` -29 dB · rev=0.6 · alternatives ['warmpad', 'solina']
  - arp (arp): `marimba` -20 dB · pan=0.25 · rev=0.3 · dly=0.25 · alternatives ['vibes', 'kalimba', 'pluck']
  - arp2 (arp): `vibes` -25 dB · pan=-0.3 · rev=0.35 · dly=0.3
  - lead (lead): `kalimba` -21 dB · rev=0.4 · dly=0.3 · alternatives ['vibes', 'marimba', 'softlead']
- **Mix** {'lufs': -10.0, 'air': 1.0, 'low': 1.6, 'width': 1.2} · reverb 2.6 · sc_depth 0.35
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.8}
- **Sound brief** Marimba / vibes / kalimba arpeggios in interlocking patterns; deep rolling house kick, shakers, congas; sub bass; soft pads; a slowly unfolding lead

### 90s pop house / dance-pop (`pop_house_90s`)

Late-90s pop house / dance-pop: a radio song at house tempo (122-134) - a punchy four-on-the-floor with a clap backbeat, shuffled 16th hats and open hats on the off-beats, a bouncing octave synth bass, sidechained string pads, syncopated chord stabs and plucked guitar-like arps, a catchy synth hook for the chorus; no EDM build-ups, one breakdown where the bass drops out, a hard stop

- **Tempo** 122-134 BPM · **scales** minor, major, dorian · swing 0.53 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 6, 5, 6], [0, 5, 6, 0], [5, 6, 0, 0], [0, 3, 6, 5]], 'major': [[0, 4, 5, 3], [3, 4, 0, 5], [5, 3, 0, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `pop_house_90s`: intro 8 [bass, kick, pad, top] -> verse 16 [arp, bass, chords, kick, snare, top] (level=0.86) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> break 12 [arp, chords, kick, pad] (alt, level=0.66) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> chorus 8 [bass, chords, kick, lead, pad, snare, top] -> outro 4 [bass, chords, kick, top] · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X.......X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.xxx.xxx.xxx.xx` / `xxxxxxxxxxxxxxxx`; **tamb** `....x.......x...` / `..x...x...x...x.`
- **Drum kit** 909 · preset `909`
- **Bass** `R.O.R.O.R.O.R.O.` / `..R...R...R...R.` / `R..R..R.R..R..R.` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x..x....x..x..` / `x..x..x...x..x..` / `x---....x---....`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.75}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `..x-x-x-x---x---` / `x-x-x-x-x-------`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'pickup', 'drumless'] · drops land plainly
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -20 dB · rev=0.15
  - clap (snare): `clap` -18 dB · rev=0.25
  - ohat (top): `ohat` -26 dB · pan=0.15
  - chat (top): `chat` -28 dB · pan=-0.2
  - tamb (top): `tamb` -27 dB · pan=0.3
  - bass (bass): `moogbass` -10 dB · sc=0.7 · alternatives ['sawbass', 'organbass', 'fmbass']
  - chords (chords): `stab` -20 dB · rev=0.3 · dly=0.2 · sc=0.6 · alternatives ['m1piano', 'piano', 'organ', 'polysynth']
  - pad (pad): `strings` -24 dB · rev=0.45 · sc=0.8 · alternatives ['warmpad', 'solina', 'glasspad']
  - arp (arp): `pluck` -25 dB · pan=0.25 · rev=0.3 · dly=0.3 · sc=0.5 · alternatives ['guitar', 'pluck_saw', 'mutedgtr']
  - lead (lead): `pluck_saw` -20 dB · rev=0.35 · dly=0.25 · sc=0.4 · alternatives ['softlead', 'polysynth', 'supersaw_lead']
- **Mix** {'lufs': -9.0, 'air': 1.6, 'low': 1.3} · reverb 1.8 · sc_depth 0.45
- **Other rules** {'sc_release': 0.4, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 54, 'punch': 140, 'decay': 9, 'drive': 2.0, 'click': 0.5}}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.8}
- **Sound brief** 909 / sampled kick + clap; shuffled 16th hats, off-beat open hat, tambourine; octave synth bass; sidechained string pad; syncopated piano / synth chord stabs; plucked guitar or synth arp; synth hook lead

## Techno & Trance

### Trance (`trance`)

Uplifting trance: gated supersaw chords, rolling offbeat bass, euphoric leads

- **Tempo** 132-140 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [5, 6, 0, 0], [0, 6, 5, 6], [5, 3, 0, 4]] · chord_bars 1 · chord size 3
- **Song form** `trance`: intro 16 [bass, kick, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> break 24 [arp, chords, fx, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, pad, top] (build) -> drop 32 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> break 8 [fx, lead, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 16 [bass, kick, top] · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `oxoxoxoxoxoxoxox`; **ride** `..x...x...x...x.`
- **Drum kit** trance · preset `909`
- **Bass** `..RR..RR..RR..RR` / `.RRR.RRR.RRR.RRR` · mode `pattern` · lowest note 31
- **Chord rhythm** `xx.xx.xx.x.xx.x.` / `x.xx.xx.x.xx.xx.` / `x-x-x-x-x-x-x-x-`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-x-x-x-x-x-x---` / `x--x--x-x--x--x-` / `x---x---x-x-x---` / `x-------x-------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.3
  - ohat (top): `ohat` -26 dB
  - chat (top): `chat` -30 dB · pan=-0.2
  - ride (top): `ride` -31 dB · pan=0.25
  - bass (bass): `sawbass`  dB · sc=1.0 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `supersaw`  dB · rev=0.35 · dly=0.15 · sc=0.9 · alternatives ['stab', 'pluck_saw', 'polysynth']
  - pad (pad): `warmpad`  dB · rev=0.6 · sc=0.8 · alternatives ['strings', 'choir', 'supersaw', 'glasspad']
  - arp (arp): `pluck_saw` -26 dB · pan=0.25 · rev=0.35 · dly=0.4 · sc=0.8 · alternatives ['pluck', 'acid', 'stab']
  - lead (lead): `supersaw_lead`  dB · rev=0.55 · dly=0.35 · sc=0.5 · alternatives ['leadsaw', 'pluck_saw', 'polysynth']
- **Mix** {'lufs': -8.5, 'air': 2.5, 'low': 1.0} · reverb 3.0 · sc_depth 0.7
- **Other rules** {'sc_release': 0.4, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.55, 'chord_center': 66, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Psytrance (`psytrance`)

Psytrance: relentless kick-bass rolls, acid squelches, hypnotic phrygian riffs

- **Tempo** 140-148 BPM · **scales** phrygian, minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 0, 0], [0, 0, 1, 0]] · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....x.......x...`; **ohat** `..x...x...x...x.`; **chat** `xxxxxxxxxxxxxxxx`
- **Drum kit** trance · preset `punchy`
- **Bass** `.RRR.RRR.RRR.RRR` · mode `pattern` · lowest note 33
- **Chord rhythm** `......x.........`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 4}
- **Lead rhythm** `x.x.xx.x.x.xx.x.` / `xxx.xxx.xxx.x.x.` / `x.xxx.x.x.xxx.x.` / `xxxxxxxxxxxx....`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap` -22 dB · rev=0.35
  - ohat (top): `ohat` -27 dB
  - chat (top): `chat` -30 dB · pan=0.2
  - bass (bass): `sawbass`  dB · alternatives ['fmbass', 'acid', 'moogbass']
  - chords (chords): `stab` -26 dB · rev=0.4 · dly=0.5 · alternatives ['warmpad', 'organ', 'polysynth']
  - pad (pad): `warmpad` -27 dB · rev=0.6 · alternatives ['choir', 'supersaw', 'glasspad']
  - arp (arp): `acid` -25 dB · pan=-0.2 · rev=0.35 · dly=0.4 · alternatives ['pluck_saw', 'pluck', 'stab']
  - lead (lead): `acid`  dB · rev=0.55 · dly=0.4 · alternatives ['leadsaw', 'hoover', 'pluck_saw']
- **Mix** {'lufs': -8.0, 'air': 2.0, 'low': 1.0} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.25, 'delay_beats': 0.75, 'kit_override': {'kick': {'len': 0.28, 'decay': 14}}, 'snare_tracks': ['clap'], 'bass_gate': 0.45, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'tune_kick': True, 'kick_shape': {'pitch': 50, 'punch': 220, 'sweep': 36, 'decay': 15, 'drive': 2.6, 'len': 0.26, 'click': 0.6}}

### Techno (`techno`)

Peak-time techno: distorted kick, rolling 16th bass, dub stabs drowned in delay

- **Tempo** 128-134 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 0, 0], [0, 0, 5, 5], [0, 6, 0, 5]] · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....x.......x...`; **ohat** `..X...X...X...X.`; **chat** `oxoxoxoxoxoxoxox`; **ride** `..o...o...o...o.`
- **Drum kit** techno · preset `punchy`
- **Bass** `.RRR.RRR.RRR.RRR` / `..RR.RRR..RR.RRO` · mode `pattern` · lowest note 31
- **Chord rhythm** `......x.......x.` / `..x.......x.....` / `...x.......x....`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5}
- **Lead rhythm** `x...x...x.......` / `..x...x...x...x.` / `x.......x-------` / `x...x...x...x...`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `hypnotic_minimal` · density `medium` · feel `robotic` · melody `minimal_motivic` · bass `rolling_groove` · drop `groove_drop` · variation `low` · culture `underground_club` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap` -20 dB · rev=0.3
  - ohat (top): `ohat`  dB · pan=0.1
  - chat (top): `chat` -29 dB · pan=-0.25
  - ride (top): `ride` -30 dB · pan=0.3
  - bass (bass): `sawbass`  dB · sc=1.0 · alternatives ['fmbass', 'reese', 'moogbass']
  - chords (chords): `stab`  dB · rev=0.35 · dly=0.55 · sc=0.8 · alternatives ['organ', 'warmpad', 'polysynth']
  - pad (pad): `warmpad`  dB · rev=0.4 · sc=1.0 · alternatives ['strings', 'choir', 'glasspad']
  - arp (arp): `pluck_saw` -28 dB · pan=0.2 · rev=0.2 · dly=0.4 · sc=0.9 · alternatives ['acid', 'pluck', 'stab']
  - lead (lead): `stab` -22 dB · pan=-0.15 · rev=0.4 · dly=0.4 · sc=0.6 · alternatives ['acid', 'leadsaw', 'pluck_saw']
- **Mix** {'lufs': -8.5, 'air': 1.5, 'low': 1.5} · reverb 2.6 · sc_depth 0.85
- **Other rules** {'sc_release': 0.4, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 3.2}}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'rumble': 0.8}

### Minimal (`minimal`)

Minimal techno: sparse clicks and blips, deep sub, lots of space and delay

- **Tempo** 124-128 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 0, 0], [0, 0, 6, 6]] · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **rim** `..o..o.....o..o.` / `...o..o...o..o..`; **clap** `....o.......o...`; **chat** `..x...x...x...x.`; **shaker** `o.o.o.o.o.o.o.o.`
- **Drum kit** techno · preset `soft`
- **Bass** `R.....R...R.....` / `..R.....R..R....` · mode `pattern` · lowest note 31
- **Chord rhythm** `......x.........` / `...........x....`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.35}
- **Lead rhythm** `x.......x.......` / `..x.......x.....` / `x...x...........` / `....x.......x...`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `hypnotic_minimal` · density `medium` · feel `robotic` · melody `minimal_motivic` · bass `sub_only` · drop `groove_drop` · variation `low` · culture `underground_club` · texture `dry_and_upfront` · rhythm `on_the_grid` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - rim (top): `rim` -28 dB · pan=0.3 · dly=0.3
  - clap (snare): `clap` -24 dB · rev=0.4
  - chat (top): `chat` -28 dB
  - shaker (top): `shaker` -31 dB · pan=-0.3
  - bass (bass): `sinebass`  dB · sc=0.7 · alternatives ['fmbass', 'sawbass', '808']
  - chords (chords): `stab` -26 dB · rev=0.3 · dly=0.6 · alternatives ['organ', 'polysynth', 'm1piano']
  - arp (arp): `pluck_saw` -28 dB · pan=-0.3 · dly=0.5 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `stab` -24 dB · rev=0.4 · dly=0.5 · alternatives ['pluck_saw', 'organ', 'acid']
- **Mix** {'lufs': -9.5, 'air': 1.0, 'low': 1.5} · reverb 2.5 · sc_depth 0.5
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.5, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Melodic Techno (`melodic_techno`)

Melodic techno: rolling 16th basslines, hypnotic arpeggios, big emotional pads and plucks

- **Tempo** 120-128 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 6, 5, 6], [0, 0, 5, 5]], 'phrygian': [[0, 1, 0, 6]], 'harmonic_minor': [[0, 5, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **chat** `..x...x...x...x.`; **ohat** `..x...x...x...x.`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** techno · preset `909`
- **Bass** `.RRR.RRR.RRR.RRR` / `RRRRRRRRRRRRRRRR` / `.R.R.R.R.R.R.R.R` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x.x.x.x.` / `x..x..x.x..x..x.` / `x---x---x---x---` / `x-------x-------`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `hypnotic_minimal` · density `medium` · feel `robotic` · melody `minimal_motivic` · bass `melodic_bass` · drop `groove_drop` · variation `low` · culture `underground_club` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -21 dB · rev=0.35
  - chat (top): `chat` -28 dB
  - ohat (top): `ohat` -27 dB
  - ride (top): `ride` -32 dB
  - bass (bass): `sawbass` -15 dB · sc=0.7 · alternatives ['fmbass', 'reese', 'acid', 'moogbass']
  - chords (chords): `warmpad` -23 dB · rev=0.5 · sc=0.6 · alternatives ['supersaw', 'strings', 'stab']
  - pad (pad): `strings` -27 dB · rev=0.5 · sc=0.6 · alternatives ['warmpad', 'choir', 'tremolo', 'glasspad']
  - arp (arp): `pluck_saw` -24 dB · dly=0.4 · sc=0.4 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `leadsaw` -20 dB · rev=0.4 · dly=0.3 · sc=0.3 · alternatives ['supersaw_lead', 'pluck_saw', 'cello']
- **Mix** {'lufs': -9.0, 'air': 1.4, 'low': 1.3} · reverb 2.0 · sc_depth 0.5
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.55, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Rolling mono bass (Diva / Repro style); Arpeggiated pluck; Wide pads; Emotional lead

### Uplifting Trance (`uplifting_trance`)

Uplifting trance: emotional minor-key anthems, rolling off-beat bass, supersaw leads and plucky arps, a long piano / pad breakdown that explodes into the drop

- **Tempo** 134-140 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[5, 3, 0, 4], [0, 5, 2, 6], [0, 5, 3, 4], [5, 6, 0, 0], [0, 3, 5, 4]] · chord_bars 1 · chord size 4
- **Song form** `trance`: intro 16 [bass, kick, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> break 24 [arp, chords, fx, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, pad, top] (build) -> drop 32 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> break 8 [fx, lead, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 16 [bass, kick, top] · form_scale 1.25
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** trance · preset `909`
- **Bass** `.RRR.RRR.RRR.RRR` / `..R...R...R...R.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `..x...x...x...x.`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-x-x-x-x---x---` / `x--x--x-x-------` / `x-x-x---x-x-x---` / `x-------x---x---`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -19 dB · rev=0.3
  - ohat (top): `ohat` -26 dB
  - chat (top): `chat` -29 dB
  - ride (top): `ride` -32 dB
  - bass (bass): `sawbass` -15 dB · sc=0.7 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `supersaw` -22 dB · rev=0.4 · sc=0.8 · alternatives ['stab', 'pluck_saw', 'piano', 'polysynth']
  - pad (pad): `warmpad` -26 dB · rev=0.6 · sc=0.6 · alternatives ['strings', 'choir', 'glasspad', 'supersaw']
  - arp (arp): `pluck_saw` -24 dB · rev=0.35 · dly=0.4 · sc=0.5 · alternatives ['pluck', 'piano', 'stab']
  - lead (lead): `supersaw_lead` -18 dB · rev=0.55 · dly=0.35 · sc=0.4 · alternatives ['leadsaw', 'pluck_saw']
- **Mix** {'lufs': -8.5, 'air': 2.0, 'low': 1.0} · reverb 3.0 · sc_depth 0.55
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Supersaw lead; Plucky arp (gated); Rolling off-beat bass; Piano (breakdown); Wide pads; Vocal

### Progressive Trance (emotional) (`progressive_trance`)

Emotional progressive trance / melodic progressive house: simple emotive chords, a big singable lead, long builds, a piano breakdown and a clean, wide drop - melody over complexity

- **Tempo** 128-136 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [5, 6, 0, 0], [0, 3, 5, 6], [0, 5, 3, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4], [3, 4, 5, 5]]} · chord_bars 1 · chord size 3
- **Song form** `trance`: intro 16 [bass, kick, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> break 24 [arp, chords, fx, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, pad, top] (build) -> drop 32 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> break 8 [fx, lead, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 16 [bass, kick, top] · form_scale 1.0
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `....x.......x...` / ``
- **Drum kit** trance · preset `909`
- **Bass** `.RRR.RRR.RRR.RRR` / `..R...R...R...R.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x---x-x-x---` / `x-------x---x---` / `x---x-x-x-------` / `x-x-x---x-------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `melodic_bass` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.25
  - ohat (top): `ohat` -28 dB · pan=0.15
  - chat (top): `chat` -31 dB · pan=-0.2
  - ride (top): `ride` -31 dB · pan=0.3
  - bass (bass): `sawbass`  dB · sc=1.0 · alternatives ['moogbass', 'fmbass', 'reese']
  - chords (chords): `supersaw` -25 dB · rev=0.4 · sc=0.9 · alternatives ['piano', 'pluck_saw', 'polysynth', 'stab']
  - pad (pad): `warmpad` -27 dB · rev=0.6 · sc=0.6 · alternatives ['strings', 'glasspad', 'choir', 'supersaw']
  - arp (arp): `pluck_saw` -27 dB · pan=-0.2 · rev=0.35 · dly=0.4 · sc=0.7 · alternatives ['pluck', 'piano', 'stab']
  - lead (lead): `supersaw_lead` -19 dB · rev=0.55 · dly=0.35 · sc=0.4 · alternatives ['pluck_saw', 'leadsaw']
- **Mix** {'lufs': -8.5, 'air': 2.0, 'low': 1.0} · reverb 3.0 · sc_depth 0.45
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slow_chords': 0.35, 'repetition': 0.8, 'simplicity': 0.35}
- **Sound brief** Supersaw or clean pluck lead; grand piano (breakdown); wide strings / pads; rolling off-beat bass

### New Beat (`new_beat`)

New beat (late-80s Belgium): slow, heavy, stomping four-on-the-floor at ~100-115 BPM, industrial EBM drums, dark acid-tinged bass and sampled stabs - hypnotic and menacing

- **Tempo** 100-116 BPM · **scales** minor, phrygian · swing 0.52 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 6]], 'phrygian': [[0, 1, 0, 1], [0, 0, 1, 0]]} · chord_bars 1 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X.......X...`; **clap** `....X.......X..x`; **chat** `..x...x...x...x.`; **rim** `...x..x....x..x.`
- **Drum kit** techno · preset `techno`
- **Bass** `R.RR.RR.R.RR.RR.` / `R.R.R.RRR.R.R.RR` · mode `acid` · lowest note 31
- **Chord rhythm** `x...............` / `....x.......x...`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 4, 'prob': 0.5}
- **Lead rhythm** `x-------........` / `x---....x---....`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `minimal_motivic` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `on_the_grid` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -16 dB · rev=0.35
  - clap (snare): `clap` -20 dB · rev=0.3
  - chat (top): `chat` -28 dB
  - rim (top): `rim` -29 dB · pan=0.3
  - bass (bass): `acid` -14 dB · alternatives ['sawbass', 'fmbass', 'moogbass']
  - chords (chords): `stab` -25 dB · rev=0.45 · dly=0.3 · alternatives ['organ', 'polysynth', 'm1piano']
  - pad (pad): `choir` -30 dB · rev=0.6 · alternatives ['warmpad', 'strings']
  - arp (arp): `pluck_saw` -29 dB · dly=0.4 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `stab` -22 dB · rev=0.4 · dly=0.3 · alternatives ['pluck_saw', 'organ', 'acid']
- **Mix** {'lufs': -9.5, 'air': 0.6, 'low': 1.6, 'drive': 0.3} · reverb 2.0 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.85, 'simplicity': 0.4}

### UK bass / 130 (`uk_bass_130`)

UK bass / 130 (techno-dubstep crossover): a rolling, broken techno kick pattern with swung metallic hats and rimshots around 130, a heavy mono sub pinned to the root, dark stabs and sparse dubby chords, long DJ-friendly sections - hypnotic, physical and minimal

- **Tempo** 128-136 BPM · **scales** minor, phrygian · swing 0.56 (unit 16) · humanise 0.003
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 0], [0, 0, 6, 0]], 'phrygian': [[0, 0, 1, 0], [0, 1, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `uk_bass_130`: intro 8 [bass, fx, kick] -> A 40 [bass, fx, kick, snare, top] -> B 48 [bass, chords, fx, kick, lead, snare, top] (crash) -> break 4 [bass, fx, kick] -> break 12 [chords, fx, pad] (alt) -> build 4 [fx, pad, top] (build) -> B 48 [arp, bass, chords, fx, kick, lead, snare, top] (drop, alt) -> outro 8 [bass, fx, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X..X..X...X.....` / `X.....X...X..X..` / `X...X...X...X...` / `X..X......X.....`; **snare** `....X.......X...` / `........X.......`; **rim** `..x...x.x.....x.` / `...x..x....x..x.`; **chat** `xxxx.xxxxxxx.xxx` / `..x...x...x...x.`; **ohat** `..x...x...x...x.`
- **Drum kit** techno · preset `techno`
- **Bass** `R-------........` / `R-----..R-------` / `R-R-....R-------` · mode `pattern` · lowest note 28
- **Chord rhythm** `....x.......x...` / `..x.....x.......`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 4, 'prob': 0.25}
- **Lead rhythm** `x---....x-......` / `....x-......x---`
- **Build-ups** default `(category default)` · choices ['pause', 'none', 'drumless'] · transitions ['gap', 'none', 'none'] · drops land plainly
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `minimal_motivic` · bass `sub_only` · drop `groove_drop` · variation `low` · culture `underground_club` · texture `club_punchy` · rhythm `swung_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -17 dB · rev=0.35
  - rim (top): `rim` -27 dB · pan=0.3
  - chat (top): `chat` -28 dB · pan=-0.2
  - ohat (top): `ohat` -30 dB · pan=0.2
  - bass (bass): `sinebass` -10 dB · sc=0.5 · alternatives ['reese', 'wobble', '808']
  - chords (chords): `stab` -26 dB · rev=0.4 · dly=0.4 · alternatives ['organ', 'polysynth', 'm1piano']
  - pad (pad): `warmpad` -32 dB · rev=0.6 · alternatives ['choir', 'strings', 'glasspad']
  - arp (arp): `acid` -30 dB · pan=0.2 · dly=0.3 · alternatives ['pluck', 'pluck_saw', 'stab']
  - lead (lead): `stab` -25 dB · rev=0.4 · dly=0.4 · alternatives ['organ', 'acid', 'pluck_saw']
- **Mix** {'lufs': -8.5, 'air': 0.5, 'low': 2.4, 'width': 0.5} · reverb 2.4 · sc_depth 0.35
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 56, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'dub': 0.4, 'dub_beats': 0.75, 'pedal_sub': True, 'repetition': 0.9}
- **Sound brief** Broken techno kick, swung metallic hats, rimshots into delay; mono sine sub on the root; dark stabs

### Late-90s trance-pop (`trance_pop_90s`)

Late-90s vocal trance-pop / UK dance: a pumping four-on-the-floor around 134 with an offbeat octave bass, big warm string-synth and supersaw chords, a sweet vocal-style hook and plucked arps - euphoric and radio-sized, built of clear verses and choruses

- **Tempo** 130-138 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 5, 2, 6], [5, 3, 0, 4], [0, 3, 5, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `trance_pop_90s`: intro 8 [chords, fx, top] (filter_in) -> verse 8 [bass, chords, kick, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> break 8 [chords, fx, pad] (build) -> chorus 32 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [bass, kick, pad] (alt) -> verse 12 [arp, bass, chords, kick, snare, top] -> chorus 24 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 4 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** (synth preset) · preset `909`
- **Bass** `..O...O...O...O.` / `.RO..RO..RO..RO.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x-x-x-x-x-x-x-x-` / `x---x---x---x---` / `..x...x...x...x.`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.8}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x-x-....` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['roll', 'filter', 'pause']
- **Traits** arrangement `tension_release` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -16 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -27 dB · pan=-0.2
  - bass (bass): `sawbass` -14 dB · sc=0.6 · alternatives ['moogbass', 'fmbass', 'reese']
  - chords (chords): `supersaw` -21 dB · rev=0.3 · sc=0.6 · alternatives ['polysynth', 'piano', 'stab']
  - pad (pad): `solina` -26 dB · rev=0.45 · alternatives ['strings', 'warmpad', 'glasspad']
  - arp (arp): `pluck_saw` -27 dB · dly=0.3 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `supersaw_lead` -18 dB · rev=0.35 · dly=0.3 · alternatives ['softlead', 'leadsaw', 'polysynth']
- **Mix** {'lufs': -9.0, 'air': 1.6, 'low': 1.4, 'width': 1.1} · reverb 2.6 · sc_depth 0.5
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.5, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** 909 kick / clap / open hats; offbeat octave bass; string machine + supersaw chords; vocal-style lead; plucked arp

### Hard trance / hands-up (`hard_trance`)

Hard trance / hands-up (2000s): a pounding 909 kick around 140 with offbeat open hats, a driving 16th-note rolling bass pinned to the root, hard supersaw and hoover-style riffs, acid squelches and a catchy synth hook - short, punchy breakdowns with a classic snare roll and long, relentless main sections

- **Tempo** 136-144 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 5, 6, 4], [5, 6, 0, 0]], 'phrygian': [[0, 1, 0, 0]], 'harmonic_minor': [[0, 5, 4, 4]]} · chord_bars 1 · chord size 3
- **Song form** `hard_trance`: intro 16 [bass, fx, kick, top] -> intro 8 [bass, fx, top] -> verse 12 [arp, bass, kick, snare, top] (crash) -> build 8 [arp, bass, chords, fx, top] (build) -> drop 48 [arp, bass, chords, fx, kick, lead, snare, top] (drop) -> verse 16 [arp, bass, kick, snare, top] -> break 8 [chords, fx, lead, pad] (alt) -> build 4 [chords, lead, snare, top] (build) -> drop 40 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, alt) -> outro 8 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `xxxxxxxxxxxxxxxx` / `x.xxx.xxx.xxx.xx`; **snare** `................`
- **Drum kit** trance · preset `trance`
- **Bass** `.RRR.RRR.RRR.RRR` / `RRRRRRRRRRRRRRRR` / `..RR..RR..RR..RR` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.x..x.x..x.x...` / `x-x-x-x-x-x-x-x-` / `x..x..x...x..x..`
- **Arp** {'rate': 4, 'mode': 'up', 'oct': 5, 'prob': 0.9}
- **Lead rhythm** `x.x..x.x..x.x.x.` / `x-x-x-x-x---x---` / `x..x..x.x.x.x...`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'pause', 'filter']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `warehouse` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - clap (snare): `clap` -16 dB · rev=0.25
  - snare (snare): `snare` -17 dB
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -26 dB · pan=-0.2
  - bass (bass): `sawbass` -12 dB · sc=0.8 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `supersaw` -19 dB · rev=0.3 · sc=0.7 · alternatives ['stab', 'polysynth', 'synthbrass']
  - pad (pad): `warmpad` -27 dB · rev=0.5 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `acid` -25 dB · pan=0.2 · dly=0.2 · alternatives ['pluck_saw', 'pluck', 'stab']
  - lead (lead): `hoover` -18 dB · rev=0.3 · dly=0.2 · alternatives ['supersaw_lead', 'leadsaw', 'acid']
- **Mix** {'lufs': -8.0, 'air': 1.6, 'low': 1.6, 'width': 0.9} · reverb 2.4 · sc_depth 0.6
- **Other rules** {'sc_release': 0.2, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 52, 'punch': 160, 'decay': 10, 'drive': 2.4, 'click': 0.7}}, 'snare_tracks': ['clap', 'snare'], 'bass_gate': 0.5, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'pedal_sub': True}
- **Sound brief** Hard 909 kick + clap, open hats on the offbeat, 16th hats; rolling 16th bass on the root; hard supersaw / hoover riff; 303 acid line; catchy synth lead; snare-roll builds

## Dubstep, Garage & Bass

### Future Bass (`future_bass`)

Future bass: lush pitch-chopped supersaw chords, vocal chops, half-time trap drums

- **Tempo** 140-160 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'major': [[3, 4, 5, 0], [0, 4, 5, 3], [3, 4, 2, 5]], 'minor': [[5, 6, 0, 0], [0, 5, 6, 4]]} · chord_bars 1 · chord size 4
- **Song form** `future_bass`: intro 4 [chords, pad] (filter_in) -> verse 8 [chords, kick, lead, pad, top] -> build 4 [chords, snare, top] (build) -> drop 16 [arp, bass, chords, kick, lead, snare, top] (drop) -> verse 8 [chords, kick, pad, top] -> drop 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> break 12 [chords, lead, pad, top] (alt) -> build 4 [chords, snare, top] (build) -> drop 16 [arp, bass, chords, kick, lead, snare, top] (drop, alt) -> outro 8 [chords, pad] (fade) · form_scale 1.5
- **Drums** **kick** `X.....X...X.....` / `X......X..X..X..`; **snare** `........X.......`; **clap** `........X.......`
- **Drum kit** (synth preset) · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 31
- **Chord rhythm** `x.xx.x.xx.x.xx.x` / `x--x--x-x--x--x-` / `x-x-x-x-x-x-x-x-`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 6}
- **Lead rhythm** `x.x.xx.x..x.x...` / `xx.x.x..x.x.xx..` / `x.x.x.x.x-x-....` / `x-x-x-x-x-------`
- **Build-ups** default `triplet` · choices ['triplet', 'roll', 'hats', 'drumless', 'wash', 'pulse', 'stops']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare`  dB · rev=0.3
  - clap (snare): `clap` -20 dB · rev=0.3
  - chat (top): `chat` -26 dB · pan=0.15
  - bass (bass): `808` -14 dB · sc=0.6 · alternatives ['sawbass', 'reese', 'fmbass']
  - chords (chords): `supersaw`  dB · rev=0.35 · sc=1.0 · alternatives ['pluck_saw', 'stab', 'epiano', 'polysynth']
  - pad (pad): `warmpad` -27 dB · rev=0.5 · sc=1.0 · alternatives ['vox', 'choir', 'glasspad']
  - arp (arp): `pluck_saw` -27 dB · rev=0.3 · dly=0.3 · sc=0.6 · alternatives ['chip', 'pluck', 'stab']
  - lead (lead): `vox`  dB · rev=0.35 · dly=0.3 · sc=0.6 · alternatives ['supersaw_lead', 'pluck', 'chip']
- **Mix** {'lufs': -8.5, 'air': 2.5, 'low': 1.0} · reverb 2.4 · sc_depth 0.85
- **Other rules** {'sc_release': 0.35, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 65, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}

### Dubstep (classic UK) (`dubstep`)

Dark / UK dubstep: half-time at 140, deep clean sub with a slow wobbling mid-bass, sparse syncopated drums, lots of space, dark atmospheres

- **Tempo** 138-142 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 5, 0, 6], [0, 0, 0, 6]], 'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6], [0, 0, 0, 1]]} · chord_bars 1 · chord size 3
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1.75
- **Drums** **kick** `X.........X.....` / `X.....X...X.....` / `X.......X.X.....`; **snare** `........X.......`; **chat** `x...x...x...x.x.` / `..x...x...x...x.`; **ohat** `..............x.`; **rim** `.....x.......x..`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R.......R.......` · mode `wobble` · lowest note 26
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.35}
- **Lead rhythm** `x-------x-------` / `x---x---x-------` / `x---------------` / `........x-------`
- **Build-ups** default `stutter` · choices ['stutter', 'halftime', 'drumless', 'tapestop', 'hats', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `wobble_modulated` · drop `sudden` · variation `sectional` · culture `uk_soundsystem` · texture `wet_and_spacious` · rhythm `half_time` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -14 dB · rev=0.35
  - chat (top): `chat` -29 dB · pan=0.2
  - ohat (top): `ohat` -30 dB
  - rim (top): `rim` -30 dB · pan=-0.25
  - bass (bass): `wobble` -14 dB · sc=0.7 · alternatives ['reese', 'growl', 'fmbass']
  - chords (chords): `warmpad` -27 dB · rev=0.6 · sc=0.5 · alternatives ['supersaw', 'strings', 'epiano']
  - pad (pad): `choir` -28 dB · rev=0.6 · sc=0.5 · alternatives ['warmpad', 'strings']
  - arp (arp): `bell` -27 dB · rev=0.4 · dly=0.35 · alternatives ['celesta', 'pluck_saw', 'vibes']
  - lead (lead): `stab` -22 dB · rev=0.5 · dly=0.4 · sc=0.4 · alternatives ['organ', 'bell', 'softlead']
  - texture (fx): `texture` -36 dB · rev=0.5
- **Mix** {'lufs': -8.0, 'air': 1.2, 'low': 1.8} · reverb 3.0 · sc_depth 0.5
- **Other rules** {'sc_release': 0.3, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 2.0, 'punch': 200, 'decay': 6}, 'snare': {'snap': 1.5, 'decay': 10}}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True}
- **Sound brief** Clean mono sine sub + LFO-wobbled mid-bass; sparse punchy drums; dark pads and drones

### UK Garage (`ukgarage`)

UK garage / 2-step: skippy shuffled drums, organ stabs, vocal chops, sub bass

- **Tempo** 130-134 BPM · **scales** minor, dorian · swing 0.6 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 3, 6, 5]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 4]]} · chord_bars 1 · chord size 4
- **Song form** `garage`: intro 8 [chords, pad, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> break 4 [chords, top] (build) -> hook 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X......X..X.....` / `X.........X..x..`; **snare** `....X.......X...`; **chat** `.xox.xox.xox.xox` / `x.xxx.xxx.xxx.xx`; **shaker** `o.o.o.o.o.o.o.o.`; **rim** `......o......o..`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R-......R..R....` / `R-....R-..R..O..` / `..R-.....R-..R..` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x..x....x..x..` / `x..x..x...x.....` / `...x..x...x..x..`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x.x..x.x..x.....` / `..x.x..x.x......` / `x..x..x.x.x.....` / `x.xx.x..x.......`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `groove_locked` · density `medium` · feel `loose_human` · melody `rhythmic_stabs` · bass `sub_only` · drop `sudden` · variation `progressive` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - shaker (top): `shaker` -30 dB · pan=-0.3
  - rim (top): `rim` -29 dB
  - bass (bass): `sinebass`  dB · sc=0.7 · alternatives ['reese', 'fmbass', '808']
  - chords (chords): `organ`  dB · rev=0.3 · dly=0.2 · sc=0.5 · alternatives ['epiano', 'stab', 'piano']
  - pad (pad): `warmpad` -27 dB · rev=0.4 · alternatives ['strings', 'glasspad', 'solina', 'vox', 'organ']
  - arp (arp): `epiano` -28 dB · dly=0.3 · alternatives ['piano', 'pluck']
  - lead (lead): `vox`  dB · rev=0.3 · dly=0.3 · alternatives ['pluck', 'epiano', 'softlead']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 1.5} · reverb 2.0 · sc_depth 0.5
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.8, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Brostep (`brostep`)

Brostep: festival dubstep - snarling growls, wobbles and FM stabs trading bars in the drop over a clean sub, aggressive half-time drums, pitch dives, risers and hard stops

- **Tempo** 140-150 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 6, 5, 6]], 'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6]], 'harmonic_minor': [[0, 0, 5, 4], [0, 5, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1.75
- **Drums** **kick** `X.........X.....` / `X.....X...X..X..` / `X..X......X.....`; **snare** `........X.......`; **chat** `x.x.x.x.x.x.x.x.` / `xxxxxxxxxxxxxxxx`; **crash** `X...............`; **clap** `........X.......`
- **Drum kit** (synth preset) · preset `hard`
- **Bass** `R.......R.......` · mode `wobble` · lowest note 26
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.3}
- **Lead rhythm** `x-------x-------` / `x.x.x...x.......` / `x---x---x-------` / `x---------------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `switchup_heavy` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `wobble_modulated` · drop `long_build` · variation `switchup` · culture `festival_mainstage` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `sudden_contrasts`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -13 dB · rev=0.25
  - clap (snare): `clap` -19 dB
  - chat (top): `chat` -27 dB · pan=0.2
  - crash (top): `crash` -27 dB
  - bass (bass): `growl` -13 dB · sc=0.7 · alternatives ['wobble', 'screech', 'reese']
  - chords (chords): `warmpad` -27 dB · rev=0.5 · sc=0.6 · alternatives ['supersaw', 'strings', 'epiano']
  - pad (pad): `choir` -28 dB · rev=0.5 · sc=0.6 · alternatives ['warmpad', 'glasspad', 'strings']
  - arp (arp): `pluck_saw` -28 dB · rev=0.3 · dly=0.4 · alternatives ['bell', 'pluck', 'stab']
  - lead (lead): `supersaw_lead` -19 dB · rev=0.3 · sc=0.4 · alternatives ['leadsaw', 'polysynth', 'hoover']
- **Mix** {'lufs': -6.5, 'air': 1.6, 'low': 2.0, 'drive': 0.25} · reverb 2.2 · sc_depth 0.65
- **Other rules** {'sc_release': 0.25, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 3.5, 'punch': 220, 'decay': 6}, 'snare': {'snap': 2.0, 'decay': 9, 'drive': 1.5}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True, 'bass_switch': ['wobble', 'screech'], 'switch_bars': 1}
- **Sound brief** Growl / FM / wobble mid-basses (Serum / Vital style) over a mono sine sub; hard half-time drums; risers, impacts

### Melodic Dubstep (`melodic_dubstep`)

Melodic dubstep: emotional chords and a big supersaw theme over half-time drums - the drop carries the melody, with piano, strings and vocal chops and a heavy but musical bass

- **Tempo** 140-150 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[5, 3, 0, 4], [0, 5, 2, 6], [0, 5, 3, 4]], 'major': [[3, 4, 5, 0], [0, 4, 5, 3], [5, 3, 0, 4]]} · chord_bars 1 · chord size 4
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1.75
- **Drums** **kick** `X.........X.....` / `X.....X...X.....`; **snare** `........X.......`; **clap** `........X.......`; **chat** `x.x.x.x.x.x.x.x.`; **crash** `X...............`
- **Drum kit** (synth preset) · preset `hard`
- **Bass** `R-------R-------` / `R---R---R-R-R---` / `R-------R---R---` · mode `pattern` · lowest note 26
- **Chord rhythm** `x---------------` / `x.xx.x.xx.x.xx.x` / `x--x--x-x--x--x-`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x-x-x---x-x-x---` / `x--x--x-x-------` / `x-x-x-x-x---x---` / `x-------x---x---`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `melodic_bass` · drop `long_build` · variation `sectional` · culture `uk_soundsystem` · texture `wet_and_spacious` · rhythm `half_time` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -14 dB · rev=0.3
  - clap (snare): `clap` -20 dB
  - chat (top): `chat` -28 dB
  - crash (top): `crash` -28 dB
  - bass (bass): `reese` -15 dB · sc=0.8 · alternatives ['growl', 'wobble', 'sawbass']
  - chords (chords): `supersaw` -22 dB · rev=0.4 · sc=0.9 · alternatives ['piano', 'polysynth', 'stab']
  - pad (pad): `strings` -25 dB · rev=0.5 · sc=0.6 · alternatives ['choir', 'glasspad', 'warmpad']
  - arp (arp): `vox` -25 dB · rev=0.3 · dly=0.3 · alternatives ['pluck_saw', 'piano', 'phonkbell']
  - lead (lead): `supersaw_lead` -18 dB · rev=0.4 · dly=0.25 · sc=0.5 · alternatives ['pluck_saw', 'leadsaw']
- **Mix** {'lufs': -7.5, 'air': 2.0, 'low': 1.5} · reverb 2.6 · sc_depth 0.6
- **Other rules** {'sc_release': 0.3, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.9, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True}
- **Sound brief** Supersaw chords + lead; Piano; Strings; Vocal chops; Reese / growl mid-bass over a sine sub

### Deep Dubstep (soundsystem) (`deep_dubstep`)

Deep dubstep (soundsystem): half-time 140, kick on 1 and snare on 3, a mono sub pinned to one note for minutes (the root, now and then the flat 2nd), a growling mid-bass that wobbles in strict 8ths and 16ths or swells slowly, skippy rims and shakers thrown into dub echoes, one dark motif, a long drums-only intro - and no snare-roll build-ups: the drop just lands, or everything stops for a beat first

- **Tempo** 138-142 BPM · **scales** phrygian, minor · swing 0.56 (unit 16) · humanise 0.005
- **Progressions** {'phrygian': [[0, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0]], 'minor': [[0, 0, 0, 0], [0, 0, 5, 0], [0, 0, 0, 6]]} · chord_bars 2 · chord size 3
- **Song form** `deep_dubstep`: intro 12 [fx, pad, top] (filter_in) -> intro 4 [chords, fx, pad, top] -> drop 32 [bass, chords, fx, kick, lead, snare, top] (drop) -> drop 32 [arp, bass, chords, fx, kick, lead, snare, top] -> break 8 [chords, fx, pad, top] (alt) -> break 8 [bass, fx, kick, pad] (alt) -> build 4 [pad, top] (build) -> drop 32 [arp, bass, chords, fx, kick, lead, snare, top] (drop, alt) -> drop 24 [bass, chords, fx, kick, lead, snare, top] (alt) -> outro 8 [fx, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.........x.....` / `X.....x...X.....` / `X..........X....`; **snare** `........X.......` / `........X......o`; **rim** `...x......x...x.` / `......x.....x...` / `...x..x....x....` / `.....x.....x..x.`; **shaker** `..x...x.x.x...x.` / `..x.x...x...x.x.`; **chat** `..x...x...x...x.` / `....x.......x...` / `..x.....x.....x.`; **ohat** `..............x.` / `................` / `......x.........`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R---------------` / `R---------------` / `R-------R-------` / `R-----------R---` · mode `wobble` · lowest note 28
- **Chord rhythm** `....x...........` / `........x.......` / `x-------........` / `....x.......x...`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 4, 'prob': 0.2}
- **Lead rhythm** `x-------........` / `........x---....` / `x---....x-......` / `....x-------....`
- **Build-ups** default `pause` · choices ['pause', 'none', 'pause', 'drumless'] · transitions ['gap', 'none', 'none', 'crash'] · drops land plainly
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `tight_swing` · melody `minimal_motivic` · bass `sub_only` · drop `sudden` · variation `sectional` · culture `uk_soundsystem` · texture `wet_and_spacious` · rhythm `half_time` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.4
  - rim (top): `rim` -27 dB · pan=0.25 · rev=0.3
  - shaker (top): `shaker` -32 dB · pan=-0.3
  - chat (top): `chat` -30 dB · pan=-0.2
  - ohat (top): `ohat` -31 dB · pan=0.3 · rev=0.3
  - bass (bass): `wobble` -10 dB · sc=0.3 · alternatives ['sinebass', 'growl', 'reese']
  - chords (chords): `stab` -27 dB · rev=0.5 · dly=0.5 · alternatives ['organ', 'warmpad', 'epiano']
  - pad (pad): `warmpad` -33 dB · rev=0.6 · alternatives ['strings', 'choir', 'glasspad']
  - arp (arp): `bell` -32 dB · pan=0.3 · rev=0.6 · dly=0.55 · alternatives ['pluck', 'organ', 'celesta']
  - lead (lead): `stab` -25 dB · pan=-0.15 · rev=0.5 · dly=0.5 · alternatives ['organ', 'bell', 'softlead']
  - texture (fx): `texture` -37 dB · rev=0.6
- **Mix** {'lufs': -10.0, 'air': 0.5, 'low': 2.2, 'width': 0.35} · reverb 2.8 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 1.5, 'decay': 8, 'pitch': 47, 'punch': 110}, 'snare': {'snap': 1.4, 'decay': 9, 'tone': 190}}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 56, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'dub': 0.5, 'dub_beats': 0.75, 'own_progs': True, 'wobble_rates': [2, 4, 8, 2, 1], 'wobble_rates_alt': [1, 0.5, 0.5, 1, 0.3333333333333333], 'wobble_lens': [16, 16, 8, 8, 4], 'pedal_sub': True, 'repetition': 0.9, 'simplicity': 0.5}
- **Sound brief** Mono sine sub on the tonic (flat 2nd now and then) + a growling mid-bass on an LFO in 8ths / 16ths; punchy kick on 1, snare on 3 with a plate; rims, shakers and hats into a tape delay; one dark stab / bell motif; long drums-only intro; no snare rolls. Classic UK half-time: kick on beat 1, snare on beat 3. Balance: the sub carries the weight (felt more than heard, kept mono and clean below ~100 Hz), the mid-bass carries the movement - when the mid-bass talks the sub stays plain

### Deep Dubstep - sparse & eerie (`deep_dubstep_minimal`)

Deep / minimal dubstep: half-time 140 with the kick on 1 and the snare on 3, sparse shuffled 2-step percussion thrown into dub delays, a heavy clean sub carrying the track, one eerie motif, dub chord stabs and lots of dark negative space - soundsystem pressure, not festival brostep

- **Tempo** 138-142 BPM · **scales** minor, phrygian · swing 0.57 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 5], [0, 0, 0, 6], [0, 5, 0, 6]], 'phrygian': [[0, 0, 1, 0], [0, 0, 0, 1]]} · chord_bars 1 · chord size 3
- **Song form** `deep_dubstep_minimal`: intro 16 [fx, kick, pad, top] (filter_in) -> intro 8 [chords, fx, kick, pad, snare, top] -> drop 32 [bass, chords, fx, kick, lead, snare, top] (drop) -> break 16 [arp, chords, fx, pad, top] (alt) -> build 4 [kick, pad, snare, top] (build) -> drop 32 [arp, bass, chords, fx, kick, lead, snare, top] (drop, alt) -> outro 16 [fx, kick, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.........x.....` / `X.....x...X.....` / `X..........X....`; **snare** `........X.......` / `........X......o`; **clap** `........x.......`; **rim** `...x......x...x.` / `......x.....x...` / `...x..x....x....` / `.....x.....x..x.`; **shaker** `..x...x.x.x...x.` / `..x.x...x...x.x.`; **chat** `....x.......x...` / `..x.....x.....x.` / `......x.......x.`; **ohat** `..............x.` / `................` / `......x.........`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R-------........` / `R-------....R---` / `R-----..R-------` / `R---------..R-R-` · mode `pattern` · lowest note 26
- **Chord rhythm** `....x...........` / `........x.......` / `............x...` / `....x.......x...`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 4, 'prob': 0.2}
- **Lead rhythm** `x-------........` / `........x---....` / `x---....x-......` / `....x-------....`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `loose_human` · melody `minimal_motivic` · bass `sub_only` · drop `sudden` · variation `low` · culture `uk_soundsystem` · texture `wet_and_spacious` · rhythm `half_time` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -16 dB · rev=0.45 · dly=0.15
  - clap (snare): `clap` -22 dB · rev=0.5
  - rim (top): `rim` -26 dB · pan=0.25 · rev=0.35 · dly=0.45
  - shaker (top): `shaker` -31 dB · pan=-0.3
  - chat (top): `chat` -30 dB · pan=-0.2 · dly=0.2
  - ohat (top): `ohat` -31 dB · pan=0.3 · rev=0.3
  - bass (bass): `sinebass` -11 dB · alternatives ['wobble', '808', 'moogbass']
  - chords (chords): `stab` -26 dB · rev=0.55 · dly=0.65 · alternatives ['organ', 'warmpad', 'epiano']
  - pad (pad): `warmpad` -32 dB · rev=0.6 · alternatives ['strings', 'glasspad', 'choir']
  - arp (arp): `bell` -32 dB · pan=0.3 · rev=0.6 · dly=0.55 · alternatives ['celesta', 'pluck', 'vibes']
  - lead (lead): `stab` -25 dB · pan=-0.15 · rev=0.55 · dly=0.55 · alternatives ['organ', 'bell', 'softlead']
  - texture (fx): `texture` -35 dB · rev=0.6
- **Mix** {'lufs': -10.5, 'air': 0.6, 'low': 2.2} · reverb 3.2 · sc_depth 0.1
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 1.4, 'decay': 7, 'pitch': 46}, 'snare': {'snap': 1.4, 'decay': 8, 'tone': 190}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.95, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.9, 'simplicity': 0.5}
- **Sound brief** Clean sine sub (the lead instrument); dub chord stabs into long delays; eerie melodica / bell motif; dark drones; shuffled rims and shakers with delay throws. Classic UK half-time (kick on 1, snare on 3); almost all sub, very little mid-bass - the sub is the melody

### Deep dubstep - rollers (sub-weight) (`deep_dubstep_rollers`)

Deep dubstep - rollers: 140 half-time and steppers, a huge rolling sub that moves under everything, sparse skippy percussion thrown into dub echoes, a dark motif or a squelchy acid line, mono and heavy - built for a soundsystem

- **Tempo** 138-142 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 0], [0, 6, 0, 5], [0, 0, 3, 0]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 6]]} · chord_bars 2 · chord size 3
- **Song form** `deep_dubstep`: intro 12 [fx, pad, top] (filter_in) -> intro 4 [chords, fx, pad, top] -> drop 32 [bass, chords, fx, kick, lead, snare, top] (drop) -> drop 32 [arp, bass, chords, fx, kick, lead, snare, top] -> break 8 [chords, fx, pad, top] (alt) -> break 8 [bass, fx, kick, pad] (alt) -> build 4 [pad, top] (build) -> drop 32 [arp, bass, chords, fx, kick, lead, snare, top] (drop, alt) -> drop 24 [bass, chords, fx, kick, lead, snare, top] (alt) -> outro 8 [fx, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.....x...X.....` / `X...X...X...X...` / `X.........x..x..` / `X.X.......X.....`; **snare** `........X.......` / `........X......o`; **rim** `...x......x...x.` / `......x.....x...` / `..x..x.....x....` / `.....x..x.....x.`; **chat** `..x...x...x...x.` / `x.x...x.x.x...x.` / `....x.......x..x`; **shaker** `..x.x...x.x...x.` / `...x..x....x..x.`; **woodblock** `.......x........` / `..........x.....`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R---------------` / `R-------R-------` / `R-----------R---` / `R-------....R---` · mode `wobble` · lowest note 26
- **Chord rhythm** `x-------........` / `........x-------`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 4, 'prob': 0.55}
- **Lead rhythm** `x-------........` / `x---....x---....` / `........x-------` / `x.......x.x.....`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `dense` · feel `robotic` · melody `minimal_motivic` · bass `wobble_modulated` · drop `long_build` · variation `low` · culture `uk_soundsystem` · texture `wet_and_spacious` · rhythm `half_time` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.35
  - rim (top): `rim` -28 dB · pan=0.3
  - chat (top): `chat` -30 dB · pan=-0.2
  - shaker (top): `shaker` -33 dB · pan=0.35
  - woodblock (top): `woodblock` -30 dB · pan=-0.3
  - bass (bass): `wobble` -10 dB · sc=0.4 · alternatives ['sinebass', 'reese', 'growl']
  - chords (chords): `stab` -26 dB · rev=0.4 · dly=0.3 · alternatives ['organ', 'epiano', 'polysynth']
  - pad (pad): `warmpad` -33 dB · rev=0.5 · alternatives ['choir', 'strings', 'glasspad']
  - arp (arp): `acid` -27 dB · pan=0.2 · rev=0.2 · dly=0.3 · alternatives ['pluck_saw', 'bell', 'pluck']
  - lead (lead): `bell` -27 dB · pan=-0.2 · rev=0.5 · dly=0.4 · alternatives ['stab', 'acid', 'softlead']
  - texture (fx): `texture` -38 dB
- **Mix** {'lufs': -10.0, 'air': -1.0, 'low': 2.6, 'width': 0.6} · reverb 2.6 · sc_depth 0.3
- **Other rules** {'sc_release': 0.3, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 48, 'punch': 110, 'sweep': 45, 'decay': 10, 'drive': 1.8, 'len': 0.35, 'click': 0.4}, 'snare': {'tone': 200, 'snap': 1.3, 'body': 0.9, 'decay': 13, 'crack': 0.4}}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 56, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'dub': 0.6, 'dub_beats': 0.75, 'spring': False, 'wobble_rates': [2, 4, 1, 2, 8], 'repetition': 0.9}
- **Sound brief** Sine / triangle sub with a slow LFO (one note rolling for bars); dry punchy kick, snare on 3 with a plate; rims and woodblocks into a tape delay; one dark stab or a 303; reverb on the snare only. Half-time: kick on 1, snare on 3; pure rolling sub with only a thin mid layer

### Future garage (`future_garage`)

Future garage / atmospheric 2-step: a swung, skippy garage beat around 130 with sparse ghostly kicks, rimshots and crackle, a warm round sub on the root, washed-out pads and pitched, breathy vocal-chop textures, soft Rhodes and piano under heavy reverb - late-night, melancholic and hazy

- **Tempo** 128-136 BPM · **scales** minor, dorian · swing 0.6 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 0, 5, 3], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `future_garage`: intro 12 [fx, kick, pad, top] (filter_in) -> build 4 [chords, fx, kick, pad, top] (build) -> verse 32 [bass, chords, fx, kick, pad, snare, top] -> hook 40 [bass, chords, fx, kick, lead, pad, snare, top] (crash) -> break 8 [chords, fx, pad] -> break 8 [chords, fx, pad, top] (alt) -> hook 40 [arp, bass, chords, fx, kick, lead, pad, snare, top] (alt) -> outro 8 [chords, fx, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `..............X.` / `X.......X....X..`; **snare** `....X.......X...` / `....X......o.X..`; **rim** `......x.......x.` / `...x......x.....`; **chat** `.xox.xox.xox.xox` / `x.xo.xx.x.xo.x.x`; **shaker** `o.o.o.o.o.o.o.o.`
- **Drum kit** vintage · preset `soft`
- **Bass** `R-------R-......` / `R---....R---..R-` · mode `pattern` · lowest note 29
- **Chord rhythm** `x---------------` / `x-------..x-....`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x---x-....x-....` / `..x-x---x-......` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['pause', 'drumless', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `long_lyrical` · bass `sub_only` · drop `long_build` · variation `sectional` · culture `uk_soundsystem` · texture `wet_and_spacious` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -17 dB · rev=0.45
  - rim (top): `rim` -28 dB · pan=0.25 · dly=0.35
  - chat (top): `chat` -29 dB · pan=-0.2
  - shaker (top): `shaker` -33 dB · pan=0.3
  - bass (bass): `sinebass` -12 dB · sc=0.4 · alternatives ['reese', '808', 'moogbass']
  - chords (chords): `epiano` -24 dB · rev=0.5 · dly=0.2 · alternatives ['piano', 'warmpad', 'wurli']
  - pad (pad): `warmpad` -26 dB · rev=0.6 · alternatives ['glasspad', 'choir', 'strings']
  - arp (arp): `piano` -29 dB · rev=0.5 · dly=0.35 · alternatives ['epiano', 'pluck', 'vibes']
  - lead (lead): `softlead` -22 dB · rev=0.55 · dly=0.4 · alternatives ['epiano', 'flute']
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -10.0, 'air': -0.5, 'low': 2.0, 'width': 1.2} · reverb 3.4 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.8}
- **Sound brief** Swung 2-step kit (sparse kick, snare / rim, shuffled hats, crackle); sine sub; big pads; pitched vocal-chop pad; Rhodes / piano; long reverbs

### Early dubstep (stepper era) (`early_dubstep`)

Early dubstep (2005-07 "stepper" era): half-time 140 with a kick on 1, snare on 3 and busy, swung 2-step hats and shakers, a rolling sub with a mid-range bass that steps between a few notes, eerie synth stabs and sirens - darker than garage, cleaner than brostep, long DJ sections and a 16-bar breakdown

- **Tempo** 138-142 BPM · **scales** minor, phrygian · swing 0.56 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 0, 5, 0], [0, 0, 0, 6], [0, 6, 5, 6]], 'phrygian': [[0, 1, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `early_dubstep`: intro 12 [fx, pad, top] (filter_in) -> intro 4 [fx, kick, pad, top] -> drop 32 [bass, fx, kick, lead, pad, snare, top] (drop) -> drop 32 [bass, chords, fx, kick, lead, snare, top] -> break 16 [fx, pad, top] (alt) -> build 4 [fx, kick, pad, top] (build) -> drop 32 [bass, chords, fx, kick, lead, snare, top] (drop, alt) -> drop 32 [arp, bass, fx, kick, lead, pad, snare, top] -> outro 8 [fx, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.....X...X.....`; **snare** `........X.......`; **chat** `x.xxx.xxx.xxx.xx` / `..x.x.x...x.x.x.`; **shaker** `.x.x.x.x.x.x.x.x`; **rim** `......x.......x.`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R-.R-...R-..O-..` / `R---R-..F---R-..` / `R-------R-.R-...` · mode `wobble` · lowest note 28
- **Chord rhythm** `....x.......x...` / `x.......x.......`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 4, 'prob': 0.3}
- **Lead rhythm** `x-------........` / `x---....x---....`
- **Build-ups** default `(category default)` · choices ['pause', 'none'] · transitions ['gap', 'none'] · drops land plainly
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `minimal_motivic` · bass `wobble_modulated` · drop `groove_drop` · variation `low` · culture `uk_soundsystem` · texture `dry_and_upfront` · rhythm `half_time` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.35
  - chat (top): `chat` -28 dB · pan=-0.2
  - shaker (top): `shaker` -31 dB · pan=0.3
  - rim (top): `rim` -29 dB · pan=0.25
  - bass (bass): `wobble` -11 dB · sc=0.3 · alternatives ['sinebass', 'growl', 'reese']
  - chords (chords): `stab` -26 dB · rev=0.4 · dly=0.4 · alternatives ['organ', 'polysynth', 'm1piano']
  - pad (pad): `warmpad` -31 dB · rev=0.6 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `pluck` -30 dB · dly=0.4 · alternatives ['stab', 'pluck_saw', 'marimba']
  - lead (lead): `leadsaw` -25 dB · rev=0.4 · dly=0.4 · alternatives ['stab', 'softlead', 'supersaw_lead']
- **Mix** {'lufs': -9.5, 'air': 0.6, 'low': 2.2, 'width': 0.4} · reverb 2.4 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'dub': 0.4, 'dub_beats': 0.75, 'wobble_rates': [1, 2, 0.5, 1], 'wobble_rates_alt': [0.5, 0.3333333333333333, 0.5], 'wobble_lens': [4, 8, 4, 2], 'repetition': 0.9}
- **Sound brief** Half-time 140 kit, swung 2-step hats + shakers; sine sub + stepping mid-bass (square / wobble); eerie stabs, sirens, dub delays

### UK bassline (140) (`bassline_140`)

UK bassline (Northern / speed-garage style): a bouncy four-on-the-floor around 138-142 with shuffled garage hats, a warbling, organ-like wobble bass that bounces in octaves and talks between the kicks, bright stabs and a chopped vocal-style hook - cheeky, fast and built for the rave

- **Tempo** 136-142 BPM · **scales** minor, dorian · swing 0.55 (unit 16) · humanise 0.003
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 5, 3, 4], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3]]} · chord_bars 1 · chord size 3
- **Song form** `bassline_140`: intro 12 [chords, fx, pad] (filter_in) -> intro 8 [bass, chords, kick] -> build 8 [chords, fx, top] (build) -> drop 32 [bass, chords, kick, lead, snare, top] (drop) -> break 12 [chords, fx, pad] (alt) -> build 8 [bass, chords, fx, kick] (build) -> drop 36 [arp, bass, chords, kick, lead, snare, top] (drop, alt) -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `.xox.xox.xox.xox` / `x.xxx.xxx.xxx.xx`; **rim** `...x......x.....`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R.O.R.O.R.O.R.O.` / `.R.O.R.R.O.R.O.R` / `R..O..R.R.O..R..` · mode `wobble` · lowest note 31
- **Chord rhythm** `..x...x...x...x.` / `x..x..x...x.....`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x.x..x.x..x.....` / `..x.x..x.x......`
- **Build-ups** default `(category default)` · choices ['pause', 'stops', 'filter'] · transitions ['gap', 'none', 'crash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `rhythmic_stabs` · bass `wobble_modulated` · drop `long_build` · variation `sectional` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -15 dB · rev=0.2
  - chat (top): `chat` -27 dB · pan=0.2
  - ohat (top): `ohat` -28 dB · pan=-0.2
  - rim (top): `rim` -29 dB
  - bass (bass): `wobble` -11 dB · sc=0.7 · alternatives ['organbass', 'fmbass', 'growl']
  - chords (chords): `organ` -22 dB · rev=0.25 · sc=0.6 · alternatives ['stab', 'piano', 'epiano']
  - pad (pad): `warmpad` -29 dB · rev=0.4 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `stab` -28 dB · dly=0.25 · alternatives ['pluck', 'pluck_saw', 'organ']
  - lead (lead): `stab` -19 dB · rev=0.25 · dly=0.25 · alternatives ['pluck_saw', 'organ', 'acid']
- **Mix** {'lufs': -8.5, 'air': 1.4, 'low': 2.0, 'width': 0.6} · reverb 1.6 · sc_depth 0.55
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'wobble_rates': [0.5, 0.25, 0.5], 'wobble_rates_alt': [0.25, 0.5], 'wobble_lens': [2, 2, 4]}
- **Sound brief** Four-on-the-floor + shuffled garage hats; warbling organ / wobble bass in octaves; stabs; vocal-chop lead

### Grime (140) (`grime`)

Grime (140): cold, sparse, aggressive UK beats - a square-wave "eskimo" bass and icy synth riff, staccato string stabs, a hard snare with skippy 2-step kicks, gunshot-like hits and long gaps - made for MCs, built in 8-bar blocks

- **Tempo** 138-144 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.52 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 0, 0, 6], [0, 6, 5, 6]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 0]], 'harmonic_minor': [[0, 0, 4, 4]]} · chord_bars 1 · chord size 3
- **Song form** `grime`: intro 8 [fx, pad] -> intro 16 [chords, fx, lead] -> drop 24 [bass, chords, kick, lead, snare, top] (drop) -> verse 32 [bass, chords, kick, snare, top] -> break 8 [bass, fx, pad] (alt) -> verse 16 [bass, chords, kick, lead, snare] (alt) -> drop 28 [arp, bass, chords, kick, lead, snare, top] (drop) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X...X.X.........` / `X.....X...X.....`; **snare** `....X.......X...` / `....X......xX...`; **chat** `x.x.x.x.x.x.x.x.` / `x.x.xxx.x.x.xx..`; **clap** `....x.......x...`
- **Drum kit** punchy · preset `punchy`
- **Bass** `R.R.....R..R....` / `R...R.R.....R...` / `R-..R...R-..R...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.x...x.x.......` / `x...x.x.....x...` / `xx..x...x..x....`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x.x.x...x.x.x...` / `x..x..x.x.......` / `xx.x..x.x..x....`
- **Build-ups** default `(category default)` · choices ['pause', 'none', 'stops'] · transitions ['gap', 'none', 'none'] · drops land plainly
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -14 dB · rev=0.15
  - clap (snare): `clap` -21 dB
  - chat (top): `chat` -27 dB · pan=0.15
  - bass (bass): `chipbass` -12 dB · alternatives ['sawbass', 'sinebass', 'fmbass']
  - chords (chords): `spiccato` -19 dB · rev=0.2 · alternatives ['pizz', 'strings', 'stab']
  - pad (pad): `warmpad` -30 dB · rev=0.4 · alternatives ['choir', 'strings', 'glasspad']
  - arp (arp): `pizz` -26 dB · dly=0.2 · alternatives ['chip', 'bell', 'harp']
  - lead (lead): `chip` -19 dB · rev=0.2 · alternatives ['leadsaw', 'pluck', 'pluck_saw']
- **Mix** {'lufs': -9.0, 'air': 1.0, 'low': 1.8, 'width': 0.5} · reverb 1.4 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.45, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True}
- **Sound brief** Hard snare + skippy kicks; square-wave "eskimo" bass; icy square / pulse riff; staccato strings (pizz / spiccato); gunshot / laser hits; big gaps

### Riddim (`riddim`)

Riddim: minimal and hypnotic - a hollow, hard-chopped triplet mid-bass repeating its 2-bar phrase, deep sub, sparse half-time drums, a creepy bell or stab and almost nothing else

- **Tempo** 140-150 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 0], [0, 6, 0, 5]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 0]]} · chord_bars 2 · chord size 3
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.....X...X.....` / `X..........X....`; **snare** `........X.......`; **clap** `........X.......`; **chat** `x...x...x...x...` / `x.x.x...x.x.x...`; **crash** `X...............` / `................`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.......R.......` · mode `wobble` · lowest note 29
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-------........` / `x---....x---....` / `........x-------`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `switchup_heavy` · density `medium` · feel `robotic` · melody `minimal_motivic` · bass `wobble_modulated` · drop `sudden` · variation `switchup` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `half_time` · harmony `static_vamp` · energy `sudden_contrasts`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.25
  - clap (snare): `clap` -18 dB · rev=0.2
  - chat (top): `chat` -27 dB · pan=0.15
  - crash (top): `crash` -24 dB · rev=0.4
  - bass (bass): `riddim` -11 dB · sc=0.5 · alternatives ['wobble', 'fmbass', 'growl']
  - pad (pad): `warmpad` -30 dB · rev=0.5 · alternatives ['choir', 'strings', 'glasspad']
  - arp (arp): `bell` -27 dB · pan=0.3 · rev=0.5 · dly=0.35 · alternatives ['celesta', 'vibes', 'pluck']
  - lead (lead): `stab` -23 dB · rev=0.3 · alternatives ['bell', 'screech', 'pluck_saw']
  - texture (fx): `texture` -38 dB
- **Mix** {'lufs': -8.0, 'air': 1.4, 'low': 2.4, 'drive': 0.2} · reverb 2.0 · sc_depth 0.35
- **Other rules** {'sc_release': 0.25, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 52, 'punch': 95, 'drive': 2.0, 'len': 0.3}, 'snare': {'tone': 220, 'snap': 1.3, 'decay': 18}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'wobble_rates': [0.3333333333333333, 0.5, 0.5, 1, 0.25], 'repetition': 0.95}
- **Sound brief** Riddim bass (Serum / Vital: square + saw, comb or formant, hard LFO chops), sine sub, dry heavy drums, creepy bell

### Chillstep (`chillstep`)

Chillstep (the ambient side of dubstep): slow half-time dubstep at 140 with lush reverb pads, piano and gentle plucks drowned in delay, a soft rolling wobble and a warm sub - melancholic and floating

- **Tempo** 138-144 BPM · **scales** minor, major, dorian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4]], 'major': [[0, 5, 3, 4], [3, 0, 4, 5]], 'dorian': [[0, 3, 0, 3]]} · chord_bars 1 · chord size 4
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.....x...X.....`; **snare** `........X.......`; **chat** `x.x.x.x.x.x.x.x.` / `x...x...x.x.x...`; **shaker** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R-------R-------` · mode `wobble` · lowest note 29
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.8}
- **Lead rhythm** `x---x---x-------` / `x-------x---x---` / `x-x-x---x-------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `wobble_modulated` · drop `emotional_swell` · variation `sectional` · culture `uk_soundsystem` · texture `massive_reverb` · rhythm `half_time` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare` -18 dB · rev=0.45
  - chat (top): `chat` -29 dB
  - shaker (top): `shaker` -31 dB · pan=0.3
  - bass (bass): `wobble` -15 dB · sc=0.5 · alternatives ['reese', 'sinebass', 'growl']
  - chords (chords): `piano` -20 dB · rev=0.5 · dly=0.2 · alternatives ['supersaw', 'warmpad', 'epiano']
  - pad (pad): `warmpad` -23 dB · rev=0.6 · alternatives ['glasspad', 'choir', 'strings']
  - arp (arp): `pluck_saw` -25 dB · pan=0.25 · rev=0.5 · dly=0.4 · alternatives ['bell', 'piano', 'pluck']
  - lead (lead): `supersaw_lead` -20 dB · rev=0.55 · dly=0.3 · alternatives ['pluck_saw', 'softlead']
  - texture (fx): `texture` -36 dB
- **Mix** {'lufs': -10.0, 'air': 1.3, 'low': 1.6} · reverb 3.6 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'wobble_rates': [1, 1, 0.5, 2]}
- **Sound brief** Soft supersaw / Juno pads, piano, delayed pluck, gentle LFO wobble, sub, soft half-time drums, rain / vinyl texture

## Drum & Bass, Breaks & Hard

### Electro (`electro`)

Electro: robotic 808 funk, FM bass grit, zappy leads

- **Tempo** 125-132 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 5, 6], [0, 0, 0, 0], [0, 6, 5, 6]] · chord_bars 1 · chord size 3
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1
- **Drums** **kick** `X..X......X..X..` / `X......X..X.....`; **clap** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `xxx.x.x.xxx.x.x.`; **cowbell808** `......x.......x.` / `................`
- **Drum kit** (synth preset) · preset `808`
- **Bass** `R..R..R...R..RO.` / `R.R...RR..R.R...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.....x.........`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x.x.x...x.x.....` / `x..x..x.x..x....` / `xxx.x...x.......` / `x---x---........`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - clap (snare): `clap`  dB · rev=0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - cowbell808 (top): `cowbell808` -30 dB · pan=-0.3
  - bass (bass): `fmbass`  dB · sc=0.7 · alternatives ['sawbass', 'acid', 'moogbass']
  - chords (chords): `stab` -25 dB · rev=0.3 · dly=0.3 · alternatives ['brass', 'pluck_saw', 'synthbrass', 'polysynth']
  - arp (arp): `chip` -28 dB · pan=0.25 · dly=0.3 · alternatives ['pluck_saw', 'pluck', 'acid']
  - lead (lead): `leadsaw`  dB · rev=0.25 · dly=0.3 · alternatives ['chip', 'acid', 'supersaw_lead']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 1.0} · reverb 2.0 · sc_depth 0.4
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Hardstyle (`hardstyle`)

Hardstyle: distorted pitched kicks, screeching leads, euphoric supersaw melodies

- **Tempo** 148-152 BPM · **scales** minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 5, 3, 4], [0, 6, 5, 4]] · chord_bars 1 · chord size 3
- **Song form** `hardstyle`: intro 16 [bass, fx, kick, snare, top] -> verse 16 [arp, bass, kick, lead, snare, top] (crash) -> break 24 [chords, fx, lead, pad] (alt) -> build 8 [chords, lead, pad, snare] (build) -> climax 32 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [arp, bass, kick, snare, top] (alt) -> outro 16 [bass, fx, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `hard`
- **Bass** `..R-..R-..R-..R-` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-x-x-x-x---x-x-` / `x--x--x-x--x--x-` / `x-x-x---x-------` / `x---x---x---x---`
- **Build-ups** default `kick_roll` · choices ['kick_roll', 'roll', 'drumless']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `uk_soundsystem` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - clap (snare): `clap` -19 dB · rev=0.4
  - ohat (top): `ohat` -27 dB
  - chat (top): `chat` -29 dB
  - bass (bass): `sawbass` -18 dB · sc=1.0 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `supersaw`  dB · rev=0.45 · sc=1.0 · alternatives ['stab', 'polysynth', 'synthbrass']
  - pad (pad): `choir` -25 dB · rev=0.5 · sc=0.9 · alternatives ['strings', 'warmpad']
  - arp (arp): `pluck_saw` -27 dB · dly=0.35 · sc=0.9 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `supersaw_lead` -17 dB · rev=0.45 · dly=0.25 · sc=0.7 · alternatives ['hoover', 'leadsaw', 'polysynth']
- **Mix** {'lufs': -7.5, 'air': 2.0, 'low': 1.0} · reverb 3.0 · sc_depth 0.9
- **Other rules** {'sc_release': 0.35, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.45, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'tune_kick': True, 'kick_shape': {'tail': 1.0, 'punch': 320, 'sweep': 22, 'decay': 3.0, 'drive': 12.0, 'len': 0.5, 'click': 0.7}}

### Drum & Bass (`dnb`)

Drum & bass: two-step breaks at 174, growling reese bass, wide pads

- **Tempo** 170-176 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 6, 4], [0, 3, 5, 6], [0, 0, 5, 6]] · chord_bars 1 · chord size 4
- **Song form** `dnb`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, snare, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad, top] (alt, crash) -> build 8 [arp, chords, snare, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 8 [bass, kick, snare, top] (fade) · form_scale 2
- **Drums** **kick** `X.........X.....` / `X.........X..x..` / `X.X.......X.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`; **ride** `x...x...x...x...`
- **Drum kit** dnb_rollers · preset `punchy` · break chops 0.15
- **Bass** `R-------R-----..` / `R-----R---R-----` / `R---------------` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x---x-x-----` / `x-x---x-x---x---` / `x-------x---x---` / `x---------------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `sectional` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare` -16 dB · rev=0.2
  - chat (top): `chat` -26 dB · pan=0.2
  - ride (top): `ride` -31 dB · pan=-0.25
  - bass (bass): `reese` -11 dB · sc=1.0 · alternatives ['sawbass', 'sinebass', 'fmbass']
  - chords (chords): `epiano` -24 dB · rev=0.3 · sc=0.6 · alternatives ['warmpad', 'piano', 'strings', 'stab', 'wurli']
  - pad (pad): `supersaw`  dB · rev=0.4 · sc=0.8 · alternatives ['warmpad', 'strings', 'choir', 'glasspad']
  - arp (arp): `stab` -28 dB · pan=0.25 · rev=0.3 · dly=0.3 · sc=0.6 · alternatives ['pluck_saw', 'epiano', 'pluck']
  - lead (lead): `leadsaw`  dB · rev=0.35 · dly=0.25 · sc=0.5 · alternatives ['pluck', 'supersaw_lead', 'polysynth']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 1.0} · reverb 2.0 · sc_depth 0.55
- **Other rules** {'sc_release': 0.35, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True}

### Jungle (`jungle`)

Jungle / breakbeat: chopped amen-style breaks, deep subs, rave stabs and dub pads

- **Tempo** 160-172 BPM · **scales** minor · swing 0.56 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 5, 6], [0, 3, 0, 4]] · chord_bars 1 · chord size 3
- **Song form** `dnb`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, snare, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad, top] (alt, crash) -> build 8 [arp, chords, snare, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 8 [bass, kick, snare, top] (fade) · form_scale 2
- **Drums** **kick** `X.X.......X.....` / `X.........XX....` / `X.X.......X..X..`; **snare** `....X..x.x..X...` / `....X.......X..x` / `....X..x....X.x.`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** jungle_raw · preset `acoustic` · break chops 0.55
- **Bass** `R-------........` / `R-----..R-......` / `R---------------` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.......x.......` / `......x.........`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x---x---........` / `x-------x---x---` / `..x-x---x-------` / `x---------------`
- **Build-ups** default `stutter` · choices ['stutter', 'halftime', 'drumless', 'tapestop', 'hats', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `sub_only` · drop `sudden` · variation `sectional` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare` -15 dB · rev=0.15
  - chat (top): `chat` -27 dB
  - ride (top): `ride` -31 dB · pan=0.3
  - bass (bass): `sinebass` -14 dB · sc=0.5 · alternatives ['reese', 'sawbass', 'moogbass']
  - chords (chords): `stab` -25 dB · rev=0.4 · dly=0.4 · alternatives ['warmpad', 'organ', 'strings', 'epiano']
  - pad (pad): `warmpad` -26 dB · rev=0.5 · alternatives ['strings', 'choir', 'glasspad']
  - arp (arp): `stab` -28 dB · dly=0.4 · alternatives ['pluck_saw', 'pluck', 'organ']
  - lead (lead): `flute`  dB · rev=0.4 · dly=0.3 · alternatives ['sax', 'pluck', 'oboe']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 1.5} · reverb 2.2 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True}

### Breakcore (`breakcore`)

Breakcore: frantic chopped breaks at 180+, reese bass, melancholic pads and chiptune

- **Tempo** 170-190 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 3, 5, 6], [5, 6, 0, 0]] · chord_bars 1 · chord size 3
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1.5
- **Drums** **kick** `X.X...X..XX.....` / `X..X.X....X.X...` / `XX......X.X..X..`; **snare** `....X..x.X..X.xX` / `..x.X.x.....Xx.x` / `....X.xx..x.X..X`; **chat** `xxxxxxxxxxxxxxxx`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** amen · preset `punchy` · break chops 0.85
- **Bass** `R-------R-------` / `R---R---R-R-R---` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x---x---x-x-----` / `x-x-x-x-x-------` / `x-------x---x---` / `x---------------`
- **Build-ups** default `stutter` · choices ['stutter', 'halftime', 'drumless', 'tapestop', 'hats', 'stops', 'wash']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `sudden` · variation `progressive` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare` -15 dB · rev=0.15
  - chat (top): `chat` -27 dB
  - ride (top): `ride` -31 dB
  - bass (bass): `reese`  dB · sc=0.5 · alternatives ['sawbass', 'growl', 'fmbass']
  - chords (chords): `warmpad` -24 dB · rev=0.5 · alternatives ['piano', 'strings', 'supersaw']
  - pad (pad): `strings` -26 dB · rev=0.5 · alternatives ['choir', 'warmpad', 'solina']
  - arp (arp): `chip` -27 dB · dly=0.3 · alternatives ['piano', 'pluck_saw', 'pluck']
  - lead (lead): `piano`  dB · rev=0.4 · alternatives ['chip', 'violin', 'epiano']
- **Mix** {'lufs': -8.5, 'air': 1.5, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Braindance / IDM (`braindance`)

Braindance / IDM: hyperactive chopped breakbeats with ratchets and ghost notes, squelchy acid bass, music-box melodies over warm detuned pads, odd modes

- **Tempo** 120-168 BPM · **scales** minor, lydian, phrygian, dorian · swing 0.5 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 5, 3, 6], [0, 0, 6, 5], [0, 3, 6, 2]], 'lydian': [[0, 1, 0, 1], [0, 1, 4, 5]], 'phrygian': [[0, 1, 0, 6]], 'dorian': [[0, 3, 0, 6], [0, 6, 3, 3]]} · chord_bars 1 · chord size 4
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X..X.X....X..X..` / `X.X...X..X.X....` / `XX....X...X.X..X`; **snare** `....X..x.x.xX..x` / `..x.X.....x.X.xx` / `....X.x..X..X.X.`; **chat** `xxxxxxxxxxxxxxxx` / `x.xxx.xxxx.xx.xx`; **snap** `...x.....x..x...` / `.x.....x...x..x.`; **ohat** `..x.......x.....`
- **Drum kit** think · preset `punchy` · break chops 0.75
- **Bass** `R..R..R.R.R...R.` / `R-..R...R.R.R...` / `R...R.RR..R.R...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 6, 'prob': 0.7}
- **Lead rhythm** `x..x..x.x..x.x..` / `x.x...x.xx..x...` / `x---x-x-x--x----` / `x.xx.x...x.x.x..`
- **Build-ups** default `stutter` · choices ['stutter', 'halftime', 'drumless', 'tapestop', 'hats', 'stops', 'wash']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `sudden` · variation `progressive` · culture `uk_soundsystem` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -16 dB · rev=0.15
  - snap (snare): `snap` -24 dB
  - chat (top): `chat` -27 dB · pan=0.2
  - ohat (top): `ohat` -29 dB
  - bass (bass): `acid` -16 dB · alternatives ['reese', 'moogbass', 'sawbass', 'fmbass']
  - chords (chords): `polysynth` -23 dB · rev=0.4 · alternatives ['warmpad', 'glasspad', 'epiano', 'solina']
  - pad (pad): `glasspad` -27 dB · rev=0.5 · alternatives ['warmpad', 'solina', 'choir', 'strings']
  - arp (arp): `celesta` -24 dB · pan=-0.25 · rev=0.35 · dly=0.3 · alternatives ['bell', 'chip', 'vibes', 'marimba', 'pluck_saw']
  - lead (lead): `bell` -19 dB · rev=0.35 · dly=0.25 · alternatives ['acid', 'celesta', 'leadsaw', 'chip', 'polysynth']
- **Mix** {'lufs': -10.0, 'air': 1.4, 'low': 1.2} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'snap'], 'bass_gate': 0.7, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Acid bass (303); Detuned analog pads (Juno / CS-80 style); Music-box / celesta; Chopped breakbeats

### Liquid DnB (`liquid_dnb`)

Liquid drum & bass: rolling, swung two-step breaks at 174, warm melodic bass over a sine sub, Rhodes and jazzy 7th chords, lush pads, soulful leads

- **Tempo** 170-176 BPM · **scales** minor, dorian, major · swing 0.53 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 3, 6, 5], [5, 3, 0, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]], 'major': [[1, 4, 0, 5], [3, 2, 1, 4]]} · chord_bars 1 · chord size 4
- **Song form** `liquid`: intro 16 [chords, fx, pad, top] (filter_in) -> build 8 [chords, lead, pad] (build) -> drop 32 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, fx, lead, pad] (alt) -> build 8 [arp, chords, pad, top] (build, alt) -> drop 32 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 4 [bass, kick, pad, snare, top] (fade) · form_scale 2
- **Drums** **kick** `X.........X.....` / `X.........X..x..`; **snare** `....X.......X...`; **chat** `x.xxx.x.x.xxx.x.` / `x.x.x.x.x.x.x.x.`; **ride** `x...x...x...x...`; **shaker** `xxxxxxxxxxxxxxxx`
- **Drum kit** liquid · preset `punchy` · break chops 0.08
- **Bass** `R-------R-----..` / `R-----R---R-----` / `R---..R---R-....` · mode `pattern` · lowest note 28
- **Chord rhythm** `x-------x-------` / `x---------------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x-x-x---x-x-....` / `x---x-x-x---....` / `..x-x-x-x---x...` / `x-------x---....`
- **Build-ups** default `filter` · choices ['drumless', 'pause', 'none']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `sectional` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare` -17 dB · rev=0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - ride (top): `ride` -32 dB · pan=-0.25
  - shaker (top): `shaker` -32 dB
  - bass (bass): `moogbass` -15 dB · sc=0.8 · alternatives ['sinebass', 'reese', 'sf:fingerbass']
  - chords (chords): `epiano` -22 dB · rev=0.35 · sc=0.5 · alternatives ['piano', 'wurli', 'polysynth', 'strings']
  - pad (pad): `strings` -25 dB · rev=0.5 · sc=0.6 · alternatives ['glasspad', 'warmpad', 'choir', 'solina']
  - arp (arp): `vibes` -27 dB · pan=0.25 · rev=0.35 · dly=0.3 · alternatives ['piano', 'harp', 'epiano']
  - lead (lead): `flute` -19 dB · rev=0.4 · dly=0.25 · alternatives ['softlead', 'sax', 'guitar']
- **Mix** {'lufs': -8.5, 'air': 1.6, 'low': 1.2} · reverb 2.0 · sc_depth 0.45
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True}
- **Sound brief** Rhodes / piano 7th chords; Warm melodic bass + sine sub; Strings & pads; Vocal or flute lead; rolling breaks

### Neurofunk (`neurofunk`)

Neurofunk: tight, technical two-step at 174, dark and mechanical - growls, reese and FM stabs trading every bar over a sine sub, cold stabs and sparse atmospheres

- **Tempo** 172-176 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 6], [0, 6, 0, 5]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 0]]} · chord_bars 1 · chord size 3
- **Song form** `dnb`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, snare, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad, top] (alt, crash) -> build 8 [arp, chords, snare, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 8 [bass, kick, snare, top] (fade) · form_scale 2
- **Drums** **kick** `X.........X.....` / `X.X.......X..x..` / `X.........XX....`; **snare** `....X.......X...` / `....X.......X..x`; **chat** `x.xxx.x.x.xxx.x.` / `xxxxxxxxxxxxxxxx`; **rim** `......x.......x.`
- **Drum kit** neuro · preset `hard` · break chops 0.1
- **Bass** `R..R..R...R.R...` / `R-.R..R.R..R....` / `RR..R...R.R.R...` · mode `pattern` · lowest note 26
- **Chord rhythm** `x...............` / `......x.......x.`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.25}
- **Lead rhythm** `x-------........` / `x---x-----......` / `........x-------` / `x.x.............`
- **Build-ups** default `stutter` · choices ['stutter', 'halftime', 'drumless', 'tapestop', 'hats', 'stops', 'wash']
- **Traits** arrangement `switchup_heavy` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `wobble_modulated` · drop `sudden` · variation `switchup` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `static_vamp` · energy `sudden_contrasts`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -14 dB · rev=0.15
  - chat (top): `chat` -26 dB · pan=0.2
  - rim (top): `rim` -28 dB · pan=-0.2
  - bass (bass): `growl` -13 dB · sc=0.8 · alternatives ['reese', 'fmbass', 'wobble']
  - chords (chords): `stab` -25 dB · rev=0.3 · sc=0.5 · alternatives ['warmpad', 'organ', 'polysynth']
  - pad (pad): `warmpad` -29 dB · rev=0.5 · sc=0.5 · alternatives ['glasspad', 'choir', 'strings']
  - arp (arp): `stab` -29 dB · rev=0.3 · dly=0.3 · alternatives ['chip', 'pluck_saw', 'pluck']
  - lead (lead): `leadsaw` -22 dB · rev=0.35 · sc=0.4 · alternatives ['stab', 'hoover', 'supersaw_lead']
- **Mix** {'lufs': -7.0, 'air': 1.4, 'low': 1.6, 'drive': 0.2} · reverb 2.0 · sc_depth 0.6
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True, 'bass_switch': ['reese', 'fmbass'], 'switch_bars': 1}
- **Sound brief** Neuro / growl / reese mid-basses (resampled, distorted) over a mono sub; tight punchy breaks; cold stabs

### Hardcore / Gabber (`gabber`)

Hardcore / gabber (90s Rotterdam): 170-200 BPM four-on-the-floor of heavily distorted, pitched "gabber" kicks, screeching leads, hoovers and raw, confrontational energy

- **Tempo** 170-195 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 5, 6, 4]], 'phrygian': [[0, 1, 0, 1]]} · chord_bars 1 · chord size 3
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** (synth preset) · preset `hard`
- **Bass** `................` · mode `pattern` · lowest note 31
- **Chord rhythm** `x...x...x...x...` / `x.x.x.x.x.x.x.x.`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x.x.x.x.` / `x-x-x-x-x-x-x-x-` / `xxx.x.x.xxx.x.x.`
- **Build-ups** default `kick_roll` · choices ['kick_roll', 'roll', 'drumless', 'halftime', 'pulse', 'tapestop', 'wash']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `sub_only` · drop `long_build` · variation `progressive` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -10 dB
  - clap (snare): `clap` -18 dB · rev=0.2
  - ohat (top): `ohat` -27 dB
  - chat (top): `chat` -29 dB
  - bass (bass): `sinebass` -30 dB · alternatives ['808', 'moogbass', 'reese']
  - chords (chords): `hoover` -22 dB · rev=0.3 · alternatives ['stab', 'supersaw', 'organ']
  - pad (pad): `choir` -30 dB · rev=0.5 · alternatives ['strings', 'warmpad']
  - arp (arp): `pluck_saw` -27 dB · dly=0.2 · alternatives ['chip', 'pluck', 'stab']
  - lead (lead): `leadsaw` -18 dB · rev=0.3 · alternatives ['hoover', 'supersaw_lead', 'polysynth']
- **Mix** {'lufs': -7.0, 'air': 1.2, 'low': 1.8, 'drive': 0.6} · reverb 2.0 · sc_depth 0.5
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 14.0, 'pitch': 52, 'decay': 4.5, 'punch': 380, 'len': 0.5}}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.8, 'tune_kick': True, 'kick_shape': {'tail': 2.0, 'punch': 420, 'sweep': 30, 'decay': 4.5, 'drive': 18.0, 'len': 0.42, 'click': 0.8}}

### Breakbeat Hardcore / Rave (`rave_hardcore`)

Breakbeat hardcore / early UK rave (1990-93): Amen-style breaks over a four-on-the-floor kick, piano stabs, hoover and Mentasm leads, pitched-up vocal chops - funky, chaotic, euphoric

- **Tempo** 135-155 BPM · **scales** minor, major · swing 0.52 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 5, 6, 4]], 'major': [[0, 4, 5, 3], [0, 3, 4, 4]]} · chord_bars 1 · chord size 3
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X..x.x..X..x`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** amen · preset `acoustic` · break chops 0.3
- **Bass** `R...R...R...R...` / `R..RR..RR..RR..R` · mode `pattern` · lowest note 31
- **Chord rhythm** `x..x..x...x..x..` / `x.x..x..x.x..x..`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x---x-x-x---` / `x.x.x.x.x.x.x.x.`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.15
  - ride (top): `ride` -27 dB
  - bass (bass): `sinebass` -14 dB · sc=0.3 · alternatives ['reese', '808', 'moogbass']
  - chords (chords): `piano` -20 dB · rev=0.3 · alternatives ['stab', 'organ', 'epiano']
  - pad (pad): `choir` -28 dB · rev=0.5 · alternatives ['strings', 'warmpad', 'vox']
  - arp (arp): `stab` -24 dB · dly=0.25 · alternatives ['piano', 'm1piano', 'hoover']
  - lead (lead): `hoover` -19 dB · rev=0.3 · alternatives ['leadsaw', 'vox']
- **Mix** {'lufs': -8.5, 'air': 1.6, 'low': 1.2, 'drive': 0.3} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Funky breaks / glitch electro (`funky_breaks`)

Funky breaks / glitch electro (late-90s big beat & nu-skool breaks): a chopped, swung funk break around 125-130 BPM with stuttered edits, snare rushes and reversed hits, a fat rubbery bass that bends and slides, a warped, gliding synth lead, crunchy palm-muted guitar riffs doubled by the bass, Rhodes stabs - loud, bass-heavy and mono-tight

- **Tempo** 122-132 BPM · **scales** minor, dorian · swing 0.54 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 3, 0, 6], [0, 6, 5, 6], [0, 0, 3, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `edm_b`: intro 8 [chords, kick, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> break 8 [arp, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [kick, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.....x...X..x..` / `X.x.......X.....` / `X.....x.x.X...x.`; **snare** `....X..o.o..X..o` / `....X.......X.o.`; **chat** `x.xxx.xxx.xxx.xx` / `x.x.x.x.x.x.x.x.`; **ohat** `..............x.`
- **Drum kit** think · preset `think` · break chops 0.35
- **Bass** `R-.R..O.R-.R..Ob` / `R..R.-O...R-.RA.` / `R-..R.O.R-..O.R.` · mode `pattern` · lowest note 28
- **Chord rhythm** `x-..x-....x-....` / `..x-..x-..x-..x-` / `x-....x-..x-....`
- **Arp** {'rate': 4, 'mode': 'up', 'oct': 5, 'prob': 0.55}
- **Lead rhythm** `x---x-x-x-------` / `..x-x---x-x-x---` / `x-------x-x-x-x-` / `x-x-....x---x---`
- **Riffs** `pp.pp.ppX-pp.pp.` / `X-.pp.ppX-.pp.pp` / `pp.f-pp.m-pp.b--` / `p.ppp.ppb-p.ppm-`
- **Build-ups** default `stutter` · choices ['stutter', 'halftime', 'drumless', 'tapestop', 'hats', 'stops', 'wash']
- **Traits** arrangement `tension_release` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `sudden` · variation `progressive` · culture `uk_soundsystem` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.15
  - chat (top): `chat` -27 dB · pan=0.15
  - ohat (top): `ohat` -29 dB · pan=-0.15
  - bass (bass): `fmbass` -11 dB · alternatives ['moogbass', 'acid', 'sawbass']
  - chords (chords): `guitar` -18 dB · alternatives ['sf:distguitar', 'epiano', 'clav']
  - pad (pad): `epiano` -25 dB · rev=0.25 · alternatives ['polysynth', 'warmpad', 'organ']
  - arp (arp): `acid` -27 dB · pan=0.25 · dly=0.2 · alternatives ['pluck', 'bell', 'pluck_saw']
  - lead (lead): `whine` -17 dB · rev=0.25 · dly=0.25 · alternatives ['talkbox', 'softlead', 'leadsaw']
- **Mix** {'lufs': -9.5, 'air': -0.5, 'low': 4.0, 'width': 0.75} · reverb 1.4 · sc_depth 0.35
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.7, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'lead_glide': True, 'riff_lo': 40, 'riff_chorus': 0.55}
- **Sound brief** Chopped funk break (Think / Hot Pants style) with edits; rubbery FM / Moog bass with slides; warped portamento lead; distorted palm-muted guitar riff doubled by the bass; Rhodes stabs; acid squelch fills

### Jump-up DnB (`jump_up`)

Jump-up drum & bass: bouncy party two-step at 174 - a rubbery, talking mid-bass wobble riff that answers itself bar to bar over a sine sub, punchy breaks, short stabs and big drops; brighter and sillier than neurofunk

- **Tempo** 172-176 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 6], [0, 3, 0, 3]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 0]]} · chord_bars 1 · chord size 3
- **Song form** `jump_up`: intro 16 [fx, pad, top] (filter_in) -> intro 16 [chords, kick, pad, snare, top] -> build 8 [arp, chords, snare, top] (build) -> drop 32 [bass, chords, kick, lead, snare, top] (drop) -> break 16 [arp, chords, fx, pad] (alt, crash) -> build 8 [arp, snare, top] (build, alt) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop, alt) -> outro 16 [bass, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.....X...X.....` / `X.........X..x..`; **snare** `....X.......X...` / `....X.......X..x`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`
- **Drum kit** dnb_amen · preset `punchy`
- **Bass** `R.R...R.R.R.....` / `R...R.R...R.R...` / `R.......R.R.R...` · mode `wobble` · lowest note 28
- **Chord rhythm** `x...............` / `x.....x.........`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x.x.....x.x.....` / `x...x...x.......` / `........x.x.x...`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `switchup_heavy` · density `medium` · feel `robotic` · melody `minimal_motivic` · bass `wobble_modulated` · drop `long_build` · variation `switchup` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `static_vamp` · energy `sudden_contrasts`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -14 dB · rev=0.2
  - chat (top): `chat` -26 dB · pan=0.2
  - bass (bass): `wobble` -11 dB · sc=0.7 · alternatives ['growl', 'reese', 'fmbass']
  - chords (chords): `stab` -24 dB · rev=0.3 · sc=0.5 · alternatives ['organ', 'supersaw', 'synthbrass']
  - pad (pad): `warmpad` -29 dB · rev=0.45 · alternatives ['glasspad', 'strings']
  - arp (arp): `pluck_saw` -27 dB · pan=0.25 · rev=0.3 · dly=0.3 · alternatives ['stab', 'chip', 'pluck']
  - lead (lead): `hoover` -20 dB · rev=0.3 · sc=0.4 · alternatives ['stab', 'supersaw_lead', 'synthbrass']
  - texture (fx): `texture` -38 dB
- **Mix** {'lufs': -7.5, 'air': 1.6, 'low': 1.8, 'drive': 0.2} · reverb 2.0 · sc_depth 0.55
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True, 'wobble_rates': [0.5, 0.25, 0.5, 1, 0.3333333333333333], 'repetition': 0.9}
- **Sound brief** Rubbery wobble / "warp" mid-bass riffs (call and response, switching every 2-4 bars) over a mono sine sub; punchy two-step breaks; short brass-like or hoover stabs; very little harmony

### Neurofunk (lighter) (`neurofunk_lite`)

Neurofunk, lighter and more melodic: the tight 174 two-step and a dark reese, but with clearer chords, a pad underneath and a lead you can hum - less extreme sound design than full neurofunk

- **Tempo** 172-176 BPM · **scales** minor, phrygian, dorian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 5, 3, 4], [0, 3, 0, 3]], 'phrygian': [[0, 1, 0, 0]], 'dorian': [[0, 3, 0, 3]]} · chord_bars 1 · chord size 3
- **Song form** `dnb`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, snare, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad, top] (alt, crash) -> build 8 [arp, chords, snare, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 8 [bass, kick, snare, top] (fade) · form_scale 2
- **Drums** **kick** `X.........X.....` / `X.X.......X.....`; **snare** `....X.......X...` / `....X.......X..x`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`
- **Drum kit** (synth preset) · preset `hard`
- **Bass** `R..R..R...R.R...` / `R-.R..R.R..R....` · mode `pattern` · lowest note 26
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-----......` / `x-------x---....` / `x.x.x...x.......`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `sectional` · culture `uk_soundsystem` · texture `club_punchy` · rhythm `on_the_grid` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -14 dB · rev=0.2
  - chat (top): `chat` -26 dB · pan=0.2
  - bass (bass): `reese` -12 dB · sc=0.75 · alternatives ['fmbass', 'growl', 'wobble']
  - chords (chords): `stab` -24 dB · rev=0.3 · sc=0.5 · alternatives ['polysynth', 'organ', 'supersaw']
  - pad (pad): `warmpad` -27 dB · rev=0.45 · sc=0.5 · alternatives ['glasspad', 'strings', 'choir']
  - arp (arp): `pluck_saw` -27 dB · pan=0.2 · rev=0.3 · dly=0.3 · alternatives ['pluck', 'stab', 'bell']
  - lead (lead): `leadsaw` -20 dB · rev=0.35 · sc=0.4 · alternatives ['supersaw_lead', 'hoover', 'softlead']
- **Mix** {'lufs': -8.0, 'air': 1.8, 'low': 1.6, 'drive': 0.15} · reverb 2.0 · sc_depth 0.55
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sub_layer': True}
- **Sound brief** Reese mid-bass over a mono sub; tight punchy breaks; cold stab chords; a soft pad and a simple synth lead

## Hip-Hop, Trap & Phonk

### Trap (`trap`)

Modern trap: half-time snares, rolling hi-hats, gliding 808s, dark bells

- **Tempo** 136-150 BPM · **scales** minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 0, 5, 4], [0, 5, 3, 4], [0, 3, 0, 4], [0, 6, 5, 4]] · chord_bars 1 · chord size 3
- **Song form** `trap`: intro 8 [chords, pad] (filter_in) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....` / `X......X..X...X.` / `X.....X.X.......` / `X..X......X.....`; **snare** `........X.......`; **clap** `........X.......`; **ohat** `..............x.` / `................`
- **Drum kit** 808 · preset `default`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x...x...` / `x..x..x.x.......` / `x.xxx...x.x.....` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare`  dB · rev=0.15
  - clap (snare): `clap` -20 dB · rev=0.15
  - chat (top): `chat` -25 dB · pan=0.15
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - bass (bass): `808` -13 dB · sc=0.6
  - chords (chords): `piano` -21 dB · rev=0.4 · dly=0.15 · alternatives ['pluck', 'epiano', 'harp', 'strings', 'sf:nylon']
  - pad (pad): `warmpad` -27 dB · rev=0.5 · alternatives ['strings', 'choir', 'glasspad']
  - lead (lead): `bell`  dB · pan=0.1 · rev=0.4 · dly=0.3 · alternatives ['flute', 'celesta', 'pluck', 'violin']
- **Mix** {'lufs': -9.0, 'air': 2.0, 'low': 1.5} · reverb 2.2 · sc_depth 0.25
- **Other rules** {'sc_release': 0.3, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 55, 'punch': 90, 'decay': 14, 'drive': 1.8, 'len': 0.35}, 'snare': {'tone': 210, 'snap': 1.0, 'decay': 20}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}

### Drift Phonk (`phonk`)

Drift phonk: a heavily distorted pitched 808 cowbell riff on loop, clipped growling 808s, rolling hats, dark minor / phrygian mood, chopped vocals and tape grit - made at 3 a.m., played too loud in a car

- **Tempo** 145-165 BPM · **scales** phrygian, minor, harmonic_minor · swing 0.53 (unit 16) · humanise 0.005
- **Progressions** {'phrygian': [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], 'minor': [[0, 0, 0, 0], [0, 0, 5, 0], [0, 0, 0, 6]], 'harmonic_minor': [[0, 0, 0, 4], [0, 0, 5, 4]]} · chord_bars 1 · chord size 3
- **Song form** `phonk`: intro 8 [fx, lead, pad] (filter_in) -> verse 16 [bass, chords, fx, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] -> break 8 [arp, bass, fx, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 8 [fx, lead, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....` / `X..X......X..X..` / `X.....X.X...X...`; **snare** `........X.......`; **clap** `........X.......`; **cowbell808** `................` / `..x.......x.....`
- **Drum kit** phonk808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 26
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 4, 'prob': 0.25}
- **Lead rhythm** `x..x..x.........` / `x.x.x...x.......` / `x..x..x.x..x....` / `x.xx.x..x.x.....` / `x.x.x.x.x..x..x.`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `tight_swing` · melody `minimal_motivic` · bass `808_slide` · drop `sudden` · variation `low` · culture `street` · texture `tape_degraded` · rhythm `half_time` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -16 dB · rev=0.3
  - clap (snare): `clap` -18 dB · rev=0.25
  - chat (top): `chat` -25 dB · pan=0.2
  - cowbell808 (top): `cowbell808` -30 dB · pan=-0.2
  - bass (bass): `808` -11 dB · sc=0.35
  - chords (chords): `warmpad` -30 dB · rev=0.5 · alternatives ['organ', 'strings', 'epiano']
  - pad (pad): `choir` -30 dB · rev=0.6 · alternatives ['warmpad', 'glasspad', 'strings']
  - arp (arp): `vox` -25 dB · rev=0.35 · dly=0.3 · alternatives ['phonkbell', 'pluck', 'chip']
  - lead (lead): `cowbell` -15 dB · rev=0.25 · alternatives ['cowbell_long', 'cowbell_dist', 'cowbell_808', 'cowbell_crushed']
- **Mix** {'lufs': -7.0, 'air': -0.5, 'low': 2.5, 'drive': 0.45, 'lofi': True, 'wobble': 0.3} · reverb 1.6 · sc_depth 0.3
- **Other rules** {'sc_release': 0.25, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 6.0}, 'clap': {'drive': 2.5}, 'snare': {'drive': 3.0}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.9, 'simplicity': 0.25, 'lead_lo': 57}
- **Sound brief** Distorted pitched TR-808 cowbell (lead); clipped saturated 808; TR-808 kit with fast hats; pitched-down vocal chops; horror pad; vinyl crackle and tape saturation

### UK Drill (`uk_drill`)

UK/NY drill: sliding 808s, triplet hats, offbeat snares, dark piano & strings

- **Tempo** 140-145 BPM · **scales** minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 0, 4], [0, 0, 5, 4], [0, 3, 5, 4]] · chord_bars 1 · chord size 3
- **Song form** `trap`: intro 8 [chords, pad] (filter_in) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X......X..x.....`; **snare** `....X......X....` / `....X.......X..x`; **chat** `x..x..x.x..x..x.` / `x.xx..x.x..x.x..`; **snap** `........x.......`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x--x--x-x-------` / `x-x-x---x---x---` / `..x-x-x-x-------` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare`  dB · rev=0.15
  - snap (snare): `snap` -22 dB
  - chat (top): `chat` -25 dB · pan=0.2
  - bass (bass): `808` -12 dB · sc=0.4
  - chords (chords): `piano`  dB · rev=0.35 · alternatives ['strings', 'spiccato', 'epiano']
  - pad (pad): `strings` -26 dB · rev=0.45 · alternatives ['choir', 'tremolo', 'solina']
  - arp (arp): `piano` -27 dB · dly=0.3 · alternatives ['pizz', 'epiano']
  - lead (lead): `strings` -21 dB · rev=0.4 · alternatives ['violin', 'choir', 'flute']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 2.0} · reverb 2.0 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Orchestral Hip Hop (`orchestral_hiphop`)

Orchestral hip hop / drill: dramatic string stabs, choir, pizzicato, sliding 808s, rolling hats

- **Tempo** 132-145 BPM · **scales** harmonic_minor, minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'harmonic_minor': [[0, 5, 0, 4], [0, 3, 5, 4], [0, 0, 5, 4]], 'minor': [[0, 5, 3, 6], [0, 3, 5, 6], [0, 5, 6, 4]]} · chord_bars 1 · chord size 3
- **Song form** `trap`: intro 8 [chords, pad] (filter_in) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X......X..x.....` / `X.....X...X.....`; **snare** `........X.......` / `....X......X....`; **clap** `........X.......`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x..x..x.x..x..x.` / `x.x.....x.x.....` / `x--x--x-x-------` / `xxxx....xxxx....`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x--x--x-x-------` / `x-x-x---x---x---` / `..x-x-x-x-------` / `x-------x-------`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `sudden` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare`  dB · rev=0.2
  - clap (snare): `clap` -21 dB
  - bass (bass): `808` -12 dB · sc=0.4
  - chords (chords): `spiccato` -21 dB · rev=0.3 · alternatives ['strings', 'piano', 'brass']
  - pad (pad): `strings` -26 dB · rev=0.45 · alternatives ['choir', 'tremolo', 'horn']
  - arp (arp): `pizz` -25 dB · pan=-0.25 · rev=0.3 · alternatives ['celesta', 'harp', 'bell']
  - lead (lead): `violin` -19 dB · rev=0.4 · alternatives ['horn', 'choir', 'cello', 'flute']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 2.0} · reverb 2.0 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** String section stabs (staccato); Strings legato / choir (pad); Pizzicato; Violin or horn theme; 808

### Jersey Club (`jersey_club`)

Jersey club: kick triplets and bed-squeak bounce, chopped vocal hooks, sliding 808s

- **Tempo** 130-142 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 6, 5, 6], [0, 3, 5, 4]] · chord_bars 1 · chord size 3
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1.25
- **Drums** **kick** `X...X...X..X..X.` / `X...X.X.X.X.....` / `X...X...X..X..X.` / `X..X..X...X.X...`; **clap** `........X.......` / `....X.......X...`; **chat** `..x...x...x...x.`; **snap** `......x.......x.`; **squeak** `..x.x.....x.x...` / `......x.x.....x.`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x---------------` / `x..x..x.........`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x..x.x.x....` / `x..x..x.x..x..x.` / `xx.xx.x.x.x.....` / `x-x-x---x-------`
- **Build-ups** default `pause` · choices ['pause', 'stops'] · transitions ['gap', 'none']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `robotic` · melody `rhythmic_stabs` · bass `808_slide` · drop `sudden` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -17 dB · rev=0.2
  - squeak (top): `woodblock` -27 dB · pan=0.2
  - chat (top): `chat` -27 dB
  - snap (top): `snap` -24 dB
  - bass (bass): `808` -13 dB
  - chords (chords): `warmpad` -25 dB · rev=0.4 · alternatives ['piano', 'strings', 'pluck_saw']
  - lead (lead): `vox` -18 dB · rev=0.2 · dly=0.2 · alternatives ['pluck', 'chip', 'softlead']
- **Mix** {'lufs': -8.5, 'air': 1.6, 'low': 1.8} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** 808 kick & slides; Vocal chops (lead); Bed-squeak / snaps; Dark pad

### Luxury Rap (`luxury_rap`)

Luxury rap: majestic soul and orchestral samples - lush strings, choir, horn stabs and piano - over booming 808s and crisp trap drums, slow and triumphant

- **Tempo** 136-152 BPM · **scales** minor, major, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 6, 5, 6], [0, 3, 5, 4]], 'major': [[0, 4, 5, 3], [3, 4, 0, 5]], 'harmonic_minor': [[0, 5, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `trap`: intro 8 [chords, pad] (filter_in) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1.4
- **Drums** **kick** `X.........X.....` / `X.....X...X.....` / `X......X..X.....`; **snare** `........X.......`; **clap** `........X.......`; **ohat** `......x.......x.`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 26
- **Chord rhythm** `x-------x-------` / `x---------------` / `x--x--x-x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-x-x---x-------` / `x---------------`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `sudden` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.3
  - clap (snare): `clap` -20 dB
  - ohat (top): `ohat` -28 dB
  - bass (bass): `808` -12 dB
  - chords (chords): `piano` -21 dB · rev=0.35 · alternatives ['strings', 'epiano', 'brass', 'harp']
  - pad (pad): `strings` -23 dB · rev=0.45 · alternatives ['choir', 'horn', 'solina', 'sf:slowstrings']
  - arp (arp): `harp` -27 dB · rev=0.4 · alternatives ['pizz', 'piano']
  - lead (lead): `brass` -18 dB · rev=0.35 · alternatives ['horn', 'violin', 'choir', 'sax', 'trumpet']
- **Mix** {'lufs': -8.5, 'air': 1.4, 'low': 2.0} · reverb 2.0 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Soul / orchestral sample: lush strings, choir, horn stabs, piano; booming 808; trap drums

### House Phonk (`house_phonk`)

House phonk: four-on-the-floor phonk - distorted detuned cowbell hooks, punchy 808 bass on the offbeat, hard claps and Memphis vocal chops at club tempo

- **Tempo** 128-142 BPM · **scales** phrygian, minor, phrygian_dominant · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6]], 'minor': [[0, 0, 5, 6], [0, 5, 0, 6]], 'phrygian_dominant': [[0, 1, 0, 1], [0, 3, 1, 0]]} · chord_bars 1 · chord size 3
- **Song form** `phonk`: intro 8 [fx, lead, pad] (filter_in) -> verse 16 [bass, chords, fx, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] -> break 8 [arp, bass, fx, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 8 [fx, lead, pad] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **clap** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`; **ohat** `..x...x...x...x.`; **cowbell808** `..x.......x.....`
- **Drum kit** (synth preset) · preset `808`
- **Bass** `..R...R...R...R.` / `..R..RR...R..RR.` / `.RR..RR..RR..RR.` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.35}
- **Lead rhythm** `x..x..x.........` / `x.x.x...x.......` / `x..x..x.x..x....` / `x.xx.x..x.x.....` / `x.x.x.x.x..x..x.`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `robotic` · melody `minimal_motivic` · bass `rolling_groove` · drop `sudden` · variation `low` · culture `street` · texture `tape_degraded` · rhythm `on_the_grid` · harmony `modal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -17 dB · rev=0.2
  - chat (top): `chat` -27 dB
  - ohat (top): `ohat` -27 dB
  - cowbell808 (top): `cowbell808` -31 dB · pan=-0.2
  - bass (bass): `808` -12 dB · sc=0.6 · alternatives ['fmbass', 'moogbass', 'sawbass']
  - chords (chords): `warmpad` -29 dB · rev=0.4 · sc=0.6 · alternatives ['organ', 'epiano', 'strings']
  - arp (arp): `vox` -24 dB · rev=0.3 · dly=0.25 · alternatives ['phonkbell', 'pluck', 'chip']
  - lead (lead): `cowbell` -15 dB · rev=0.2 · sc=0.3 · alternatives ['cowbell_808', 'cowbell_dist', 'cowbell_long']
- **Mix** {'lufs': -7.0, 'air': 0.0, 'low': 2.4, 'drive': 0.4, 'lofi': True, 'wobble': 0.2} · reverb 2.0 · sc_depth 0.55
- **Other rules** {'sc_release': 0.25, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 5.0}, 'clap': {'drive': 2.0}}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 55, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'lead_lo': 57, 'repetition': 0.9, 'simplicity': 0.25}
- **Sound brief** Distorted phonk cowbell; offbeat distorted bass; hard four-on-the-floor kick; Memphis vocal chops

### Memphis Phonk (`memphis_phonk`)

Memphis phonk: the original - slow, dusty and lo-fi, eerie cowbell and piano loops, rattling 808 hats and cowbells, chopped vocal shouts, cassette grit

- **Tempo** 66-92 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 0, 5, 5], [0, 6, 5, 6], [0, 0, 0, 5]], 'phrygian': [[0, 1, 0, 0]], 'harmonic_minor': [[0, 0, 4, 4]]} · chord_bars 1 · chord size 3
- **Song form** `phonk`: intro 8 [fx, lead, pad] (filter_in) -> verse 16 [bass, chords, fx, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] -> break 8 [arp, bass, fx, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 8 [fx, lead, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....` / `X..X......X.....`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.xxx.xxx.xxx.xx` / `xxx.xxx.xxx.xxx.`; **cowbell808** `x.....x...x.....` / `..x...x...x...x.`
- **Drum kit** phonk808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 26
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x...x...x...x...` / `x.x...x.x.x.....` / `x---x---x-------` / `x..x..x.........`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `tight_swing` · melody `minimal_motivic` · bass `808_slide` · drop `sudden` · variation `low` · culture `street` · texture `tape_degraded` · rhythm `straight_16ths` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -17 dB · rev=0.2
  - clap (snare): `clap` -21 dB
  - chat (top): `chat` -26 dB · pan=0.2
  - cowbell808 (top): `cowbell808` -26 dB · pan=-0.25
  - bass (bass): `808` -12 dB
  - chords (chords): `piano` -23 dB · rev=0.3 · alternatives ['organ', 'warmpad', 'epiano']
  - arp (arp): `vox` -23 dB · rev=0.3 · dly=0.3 · alternatives ['phonkbell', 'pluck', 'chip']
  - pad (pad): `choir` -31 dB · rev=0.6 · alternatives ['strings', 'solina', 'glasspad', 'vox']
  - lead (lead): `cowbell` -16 dB · rev=0.25 · alternatives ['cowbell_808', 'cowbell_long', 'cowbell_crushed']
- **Mix** {'lufs': -9.0, 'air': -1.0, 'low': 2.0, 'lofi': True, 'wobble': 0.8} · reverb 2.0 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 3.0}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'lead_lo': 57, 'repetition': 0.9, 'simplicity': 0.3, 'sampler': True}
- **Sound brief** 808 kit (rattling hats, cowbell); eerie piano or bell loop; pitched-down Memphis vocal chops; tape hiss

### Brazilian Phonk (`brazilian_phonk`)

Brazilian phonk: baile-funk bounce under phonk grit - syncopated tamborzao drums, a distorted pitched cowbell riff, heavy distorted sub, chopped vocal shouts; gritty and danceable

- **Tempo** 130-150 BPM · **scales** minor, phrygian · swing 0.52 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 0]], 'phrygian': [[0, 0, 1, 0], [0, 0, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `phonk`: intro 8 [fx, lead, pad] (filter_in) -> verse 16 [bass, chords, fx, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] -> break 8 [arp, bass, fx, pad] (alt) -> drop 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 8 [fx, lead, pad] (fade) · form_scale 1
- **Drums** **kick** `X..X..X...X..X..` / `X..X..X...X.X...` / `X..X..X.X..X..X.`; **snare** `....X..X....X...` / `...X..X....X..X.`; **clap** `....x.......x...`; **conga** `..o..o..o..o..o.` / `.o..o.o..o..o.o.`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`; **cowbell808** `..x.......x.....` / `......x.......x.`
- **Drum kit** phonk808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 26
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 4, 'prob': 0.3}
- **Lead rhythm** `x..x..x.x..x....` / `x..x..x...x.x...` / `x.xx.x..x.x.....` / `x..x..x.........`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `minimal_motivic` · bass `808_slide` · drop `sudden` · variation `low` · culture `street` · texture `club_punchy` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -17 dB · rev=0.15
  - clap (snare): `clap` -20 dB · rev=0.2
  - conga (top): `conga` -24 dB · pan=-0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - cowbell808 (top): `cowbell808` -29 dB · pan=0.25
  - bass (bass): `808` -11 dB · sc=0.35
  - chords (chords): `warmpad` -31 dB · rev=0.4 · alternatives ['organ', 'stab', 'epiano']
  - pad (pad): `choir` -32 dB · rev=0.5 · alternatives ['strings', 'warmpad', 'vox']
  - arp (arp): `vox` -23 dB · rev=0.25 · dly=0.2 · alternatives ['phonkbell', 'pluck', 'chip']
  - lead (lead): `cowbell` -15 dB · rev=0.2 · alternatives ['cowbell_dist', 'cowbell_808', 'cowbell_long']
- **Mix** {'lufs': -7.0, 'air': 0.2, 'low': 2.4, 'drive': 0.4} · reverb 1.3 · sc_depth 0.35
- **Other rules** {'sc_release': 0.2, 'delay_beats': 0.75, 'kit_override': {'kick': {'drive': 5.0}, 'clap': {'drive': 2.0}, 'snare': {'drive': 2.5}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'lead_lo': 57, 'repetition': 0.9, 'simplicity': 0.25}
- **Sound brief** Distorted pitched 808 cowbell; baile funk tamborzao (kick, snare, congas); distorted sub 808; vocal shouts

### Rage (`rage`)

Rage: huge detuned supersaw synth leads and arps, distorted booming 808s, hard trap drums at 150+ - loud, bright and euphoric

- **Tempo** 150-165 BPM · **scales** minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 0, 5, 6], [0, 3, 6, 5]], 'harmonic_minor': [[0, 5, 0, 4], [0, 3, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `trap`: intro 8 [chords, pad] (filter_in) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....` / `X..X......X..X..` / `X.....X.X.......`; **snare** `........X.......`; **clap** `........X.......`; **ohat** `......x.......x.`
- **Drum kit** 808 · preset `default`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x-------x-------` / `x---x---x---x---`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.` / `xxxxxxxxxxxxxxxx` / `x.x.x...x.x.x...`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -17 dB · rev=0.2
  - clap (snare): `clap` -19 dB · rev=0.2
  - chat (top): `chat` -26 dB · pan=0.15
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - bass (bass): `808` -11 dB · sc=0.5
  - chords (chords): `supersaw` -22 dB · rev=0.35 · sc=0.6 · alternatives ['polysynth', 'stab', 'synthbrass']
  - arp (arp): `pluck_saw` -25 dB · pan=0.2 · rev=0.3 · dly=0.2 · sc=0.4 · alternatives ['supersaw_lead', 'bell', 'pluck']
  - lead (lead): `supersaw_lead` -17 dB · rev=0.35 · dly=0.2 · alternatives ['leadsaw', 'polysynth', 'hoover']
- **Mix** {'lufs': -8.0, 'air': 2.2, 'low': 1.8, 'drive': 0.15} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.25, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 55, 'punch': 95, 'drive': 2.2, 'len': 0.3}, 'snare': {'tone': 230, 'snap': 1.2, 'decay': 16}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Supersaw lead (Serum / Sylenth / Surge XT), distorted 808, hard trap kit

### Plugg / Pluggnb (`plugg`)

Plugg / pluggnb: dreamy major-key synth chords and soft bells, simple sliding 808s, sparse bouncy trap drums - floaty and sweet

- **Tempo** 140-160 BPM · **scales** major, dorian, minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'major': [[0, 5, 3, 4], [3, 4, 0, 5], [0, 3, 5, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 4]], 'minor': [[0, 5, 6, 3]]} · chord_bars 1 · chord size 4
- **Song form** `trap`: intro 8 [chords, pad] (filter_in) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....` / `X.........X..X..`; **snare** `........X.......`; **clap** `........X.......`; **ohat** `..............x.`
- **Drum kit** 808 · preset `default`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x-------x-------` / `x---------------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 6, 'prob': 0.8}
- **Lead rhythm** `x-x-x---x-x-....` / `x---x---x-x-x---` / `x-x-..x-x-x-....`
- **Build-ups** default `hats` · choices ['hats', 'pulse', 'filter', 'pickup', 'wash', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `groove_drop` · variation `sectional` · culture `street` · texture `wet_and_spacious` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -19 dB · rev=0.3
  - clap (snare): `clap` -21 dB · rev=0.3
  - chat (top): `chat` -27 dB · pan=0.15
  - ohat (top): `ohat` -30 dB · pan=-0.2
  - bass (bass): `808` -12 dB
  - chords (chords): `polysynth` -21 dB · rev=0.45 · dly=0.15 · alternatives ['warmpad', 'epiano', 'glasspad']
  - arp (arp): `bell` -26 dB · pan=0.25 · rev=0.5 · dly=0.3 · alternatives ['celesta', 'kalimba', 'vibes']
  - lead (lead): `softlead` -20 dB · rev=0.4 · dly=0.25 · alternatives ['bell', 'flute', 'pluck_saw']
- **Mix** {'lufs': -9.5, 'air': 2.0, 'low': 1.6} · reverb 2.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Warm saw / poly "plugg" pad, music-box bells, soft sine lead, 808 with slides

### Cloud Rap (`cloud_rap`)

Cloud rap: dreamy, washed-out and ethereal - huge reverb pads and choir-like haze, a soft melody drowned in echo, slow half-time drums and a deep, gentle 808

- **Tempo** 60-76 BPM · **scales** minor, dorian, major · swing 0.52 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 5, 3, 6], [0, 3, 5, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 2]], 'major': [[0, 5, 3, 4], [3, 0, 4, 5]]} · chord_bars 2 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.......X.X.....`; **snare** `........X.......`; **clap** `........X.......`; **ohat** `..............x.`
- **Drum kit** 808 · preset `default`
- **Bass** `R.......R.......` · mode `808` · lowest note 26
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 4, 'mode': 'up', 'oct': 6, 'prob': 0.5}
- **Lead rhythm** `x-------x-------` / `x---------------` / `x-----x---------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `808_slide` · drop `emotional_swell` · variation `sectional` · culture `street` · texture `massive_reverb` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare` -20 dB · rev=0.5
  - clap (snare): `clap` -22 dB · rev=0.5
  - chat (top): `chat` -29 dB · pan=0.15
  - ohat (top): `ohat` -31 dB · pan=-0.2
  - bass (bass): `808` -13 dB
  - chords (chords): `glasspad` -20 dB · rev=0.7 · alternatives ['warmpad', 'polysynth', 'epiano']
  - pad (pad): `choir` -25 dB · rev=0.7 · alternatives ['glasspad', 'warmpad', 'strings']
  - arp (arp): `bell` -28 dB · pan=0.3 · rev=0.7 · dly=0.4 · alternatives ['celesta', 'pluck_saw', 'vibes']
  - lead (lead): `softlead` -21 dB · rev=0.7 · dly=0.45 · alternatives ['bell', 'flute']
  - texture (fx): `texture` -38 dB
- **Mix** {'lufs': -11.0, 'air': 1.0, 'low': 2.0} · reverb 4.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Pitched / reversed vocal-pad samples, glassy pads, bell or soft lead in heavy reverb + delay, soft 808, sparse trap drums

### UK road rap (`uk_road_rap`)

UK road rap: a dark, half-time London rap beat around 150 BPM - a huge mono 808 sub sliding between the root, its leading tone and the fifth, steady ticking 8th hats with the odd roll, a hard snare on the half-time backbeat, sparse kicks, and a moody harmonic-minor piano line over low strings and choir - roomy for the bars

- **Tempo** 146-156 BPM · **scales** harmonic_minor, minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'harmonic_minor': [[0, 0, 5, 4], [0, 5, 0, 4], [0, 0, 3, 4]], 'minor': [[0, 0, 5, 6], [0, 5, 3, 4]]} · chord_bars 1 · chord size 3
- **Song form** `trap`: intro 8 [chords, pad] (filter_in) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.......X.....x.` / `X..........X....`; **snare** `........X.......` / `........X......x`; **chat** `x.x.x.x.x.x.x.x.` / `x.x.x.x.x.x.xxx.` / `x.x.x.x.x.xxx.x.`; **ohat** `......x.........`
- **Drum kit** (synth preset) · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.35}
- **Lead rhythm** `x---x---x-x-----` / `x-------x---x---` / `x---x-x-x-------` / `x-------x-------`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `sudden` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -15 dB · rev=0.2
  - chat (top): `chat` -26 dB · pan=0.1
  - ohat (top): `ohat` -30 dB · pan=-0.1
  - bass (bass): `808` -10 dB · sc=0.3
  - chords (chords): `strings` -25 dB · rev=0.35 · alternatives ['tremolo', 'piano', 'sf:slowstrings']
  - pad (pad): `choir` -29 dB · rev=0.45 · alternatives ['strings', 'warmpad']
  - arp (arp): `piano` -28 dB · rev=0.3 · dly=0.25 · alternatives ['pizz', 'bell', 'epiano']
  - lead (lead): `piano` -19 dB · rev=0.35 · alternatives ['strings', 'bell', 'flute']
- **Mix** {'lufs': -9.0, 'air': 0.0, 'low': 3.0, 'width': 0.4} · reverb 2.0 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.8}
- **Sound brief** 808 kick + long sliding 808 sub (mono, root / leading tone / fifth); half-time snare; 8th hats with short rolls; dark harmonic-minor piano melody; low strings and choir pad; plenty of space for vocals

### Hard trap (brass & strings) (`hard_trap`)

Hard trap (brass & strings, early 2010s - late 2010s): a menacing horn / string / choir loop in a minor key, huge distorted 808s pinned to the root, machine-gun hi-hat rolls, claps on the half-time backbeat, and the beat cutting out for 4 bars at a time so the 808 can slam back in

- **Tempo** 136-156 BPM · **scales** minor, harmonic_minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 5], [0, 0, 6, 5], [0, 5, 0, 6]], 'harmonic_minor': [[0, 0, 5, 4], [0, 0, 1, 4]], 'phrygian': [[0, 1, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `hard_trap`: intro 8 [chords, pad, top] -> break 4 [chords] -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 4 [chords, top] -> verse 16 [bass, chords, kick, snare, top] (crash) -> break 4 [chords, pad, top] -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 4 [chords, top] -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> break 4 [chords, pad, top] (alt) -> hook 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, top] (fade) · form_scale 1
- **Drums** **kick** `X.....X.....X...` / `X.......X.X.....` / `X.....X...X..X..`; **clap** `........X.......`; **snare** `........X.......`; **ohat** `..............x.`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x-----x-----x---` / `x-x---x-x---x---` / `x-------x---x-x-`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x-x-..x-x-......` / `x-----x-----x---` / `x.x.x...x.x.x...`
- **Build-ups** default `(category default)` · choices ['pause', 'none'] · transitions ['gap', 'none', 'none'] · drops land plainly
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `groove_drop` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - clap (snare): `clap` -15 dB · rev=0.15
  - snare (snare): `snare` -20 dB
  - chat (top): `chat` -25 dB · pan=0.15
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - bass (bass): `808` -10 dB · sc=0.4
  - chords (chords): `brass` -19 dB · rev=0.3 · alternatives ['synthbrass', 'strings', 'spiccato']
  - pad (pad): `strings` -24 dB · rev=0.4 · alternatives ['choir', 'tremolo', 'solina']
  - arp (arp): `pizz` -27 dB · dly=0.2 · alternatives ['piano', 'bell', 'harp']
  - lead (lead): `choir` -21 dB · rev=0.45 · alternatives ['bell', 'brass', 'strings']
- **Mix** {'lufs': -8.0, 'air': 1.2, 'low': 2.6, 'width': 0.6} · reverb 2.2 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 52, 'punch': 110, 'decay': 12, 'drive': 2.2, 'len': 0.3}, 'snare': {'tone': 220, 'snap': 1.3, 'decay': 16}}, 'snare_tracks': ['clap', 'snare'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'pedal_sub': True}
- **Sound brief** Distorted 808 + kick, claps / snare on 3, rolling hats; brass section stabs, low strings, choir; bell or synth lead; beat drop-outs every few bars

### Wonky / beat-scene bass (`wonky_beats`)

Wonky / beat-scene bass (purple sound): a lazy, drunken hip-hop swing around 86-92 with late snares and stuttered hats, a huge round sub, detuned, pitch-bending synth chords and squelchy G-funk-ish leads, warped tape and glitches - woozy, colourful and heavy

- **Tempo** 84-94 BPM · **scales** minor, dorian, mixolydian · swing 0.6 (unit 16) · humanise 0.01
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 1, 0, 6]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `wonky_beats`: intro 16 [bass, chords, fx, kick] (filter_in) -> break 8 [bass, fx, pad] (build) -> A 20 [bass, chords, fx, kick, lead, snare, top] (drop) -> break 8 [bass, chords, fx, kick, pad] (alt) -> A 20 [arp, bass, chords, fx, kick, lead, snare, top] (alt) -> outro 4 [chords, fx, pad] (fade) · form_scale 1
- **Drums** **kick** `X......X..X.....` / `X.....x..X......` / `X..x.....X..x...`; **snare** `....X.......X...` / `....X.......X..x`; **chat** `x.xxx.x.xx.x.xxx` / `x..x.xx..x.xx.x.`; **rim** `......x.......x.`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R-------..R-....` / `R---..R-R-------` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---..x-..x-....` / `x-------x---....`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-x-x-------` / `..x-x---x-x-....` / `x-x-x---x-------`
- **Build-ups** default `(category default)` · choices ['pause', 'drumless', 'none'] · transitions ['none', 'gap', 'tapestop']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `long_lyrical` · bass `sub_only` · drop `long_build` · variation `sectional` · culture `street` · texture `tape_degraded` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.25
  - chat (top): `chat` -28 dB · pan=0.2
  - rim (top): `rim` -29 dB · pan=-0.25
  - bass (bass): `sinebass` -10 dB · sc=0.3 · alternatives ['moogbass', 'reese', '808']
  - chords (chords): `polysynth` -21 dB · rev=0.35 · alternatives ['epiano', 'synthbrass', 'stab']
  - pad (pad): `glasspad` -28 dB · rev=0.5 · alternatives ['warmpad', 'solina']
  - arp (arp): `chip` -29 dB · dly=0.3 · alternatives ['pluck', 'pluck_saw', 'acid']
  - lead (lead): `whine` -19 dB · rev=0.3 · dly=0.3 · alternatives ['leadsaw', 'talkbox', 'softlead']
- **Mix** {'lufs': -9.5, 'air': 0.2, 'low': 2.4, 'width': 0.8, 'lofi': True, 'wobble': 2.0} · reverb 2.2 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'groove': 'dilla', 'lead_glide': True}
- **Sound brief** Drunk-swung drums with late snares and stuttered hats; sine / Moog sub; detuned poly-synth chords with pitch drift; gliding square / saw lead; tape warble and glitches

### Beat-switch trap (`switch_trap`)

Beat-switch trap (late 2010s): one track, several beats - dark psychedelic synths and a huge distorted 808, with the beat cutting out, a bar of dead silence, and a completely new loop and drum pattern taking over two or three times; hard, theatrical and unpredictable

- **Tempo** 140-156 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 5], [0, 6, 5, 6]], 'phrygian': [[0, 1, 0, 0]], 'harmonic_minor': [[0, 0, 4, 4]]} · chord_bars 1 · chord size 3
- **Song form** `switch_trap`: A 24 [bass, chords, kick, lead, snare, top] -> break 8 [chords, fx, pad] -> B 28 [bass, chords, kick, lead, pad, snare, top] (alt) -> stop 4 [fx] -> break 4 [chords] (alt) -> C 24 [arp, bass, chords, kick, snare, top] -> hook 20 [bass, chords, kick, lead, pad, snare, top] (crash) -> stop 4 [fx] -> D 36 [arp, bass, chords, kick, lead, pad, snare, top] (alt, drop) -> outro 8 [bass, chords, kick, top] (fade) · form_scale 1
- **Drums** **kick** `....X.....X.....` / `X.X.....X.....X.` / `X.....X...X.....`; **clap** `........X.......`; **snare** `........X.......` / `............X...`; **ohat** `..............x.`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 26
- **Chord rhythm** `x-------x-------` / `x---x---x-x-....` / `x-x-....x-x-....`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-x-..x-x-......` / `x-----x-----x---` / `x.x.x...x.x.x...`
- **Build-ups** default `(category default)` · choices ['pause', 'none'] · transitions ['gap', 'none', 'none'] · drops land plainly
- **Traits** arrangement `switchup_heavy` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `groove_drop` · variation `switchup` · culture `street` · texture `club_punchy` · rhythm `half_time` · harmony `static_vamp` · energy `sudden_contrasts`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -15 dB · rev=0.2
  - snare (snare): `snare` -19 dB
  - chat (top): `chat` -25 dB · pan=0.15
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - bass (bass): `808` -10 dB · sc=0.4
  - chords (chords): `polysynth` -21 dB · rev=0.4 · alternatives ['epiano', 'piano', 'strings']
  - pad (pad): `glasspad` -27 dB · rev=0.5 · alternatives ['choir', 'warmpad', 'solina']
  - arp (arp): `pluck` -27 dB · dly=0.3 · alternatives ['bell', 'chip', 'pluck_saw']
  - lead (lead): `whine` -21 dB · rev=0.35 · dly=0.3 · alternatives ['leadsaw', 'bell', 'choir']
- **Mix** {'lufs': -8.0, 'air': 1.2, 'low': 2.6, 'width': 0.7} · reverb 2.4 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 50, 'punch': 100, 'decay': 12, 'drive': 2.0, 'len': 0.3}}, 'snare_tracks': ['clap', 'snare'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': '', 'no_rotation': False, 'pedal_sub': True}
- **Sound brief** Huge distorted 808; trap kit with rolls; dark psychedelic synth loops (detuned keys, reversed pads); hard beat switches with silent bars between them

## Pop, R&B & Hopecore

### Synth-pop (`synthpop`)

Synth-pop: punchy LinnDrum-style beats, bright plucks, string pads, catchy leads

- **Tempo** 110-122 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'major': [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4]], 'minor': [[0, 5, 2, 6], [0, 3, 5, 4]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X...X...X...X...`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tom** `................`
- **Drum kit** linn · preset `punchy`
- **Bass** `R.R.R.R.R.R.R.R.` / `R.RRR.R.R.RRR.R.` · mode `pattern` · lowest note 33
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x--x--x-x--x--x-`
- **Arp** {'rate': 1, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x.x.x.x.x---....` / `x---x---x-x-x---` / `x-------x-------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `on_the_grid` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.4
  - chat (top): `chat` -27 dB · pan=0.2
  - bass (bass): `sawbass`  dB · sc=0.5 · alternatives ['fmbass', 'chipbass', 'moogbass']
  - chords (chords): `pluck_saw`  dB · rev=0.3 · dly=0.2 · sc=0.4 · alternatives ['stab', 'epiano', 'piano', 'brass', 'polysynth', 'synthbrass']
  - pad (pad): `strings`  dB · rev=0.4 · sc=0.4 · alternatives ['warmpad', 'choir', 'solina', 'glasspad']
  - arp (arp): `pluck_saw` -27 dB · pan=-0.25 · rev=0.3 · dly=0.3 · alternatives ['chip', 'pluck', 'stab']
  - lead (lead): `leadsaw`  dB · rev=0.3 · dly=0.25 · alternatives ['pluck', 'softlead', 'brass', 'synthbrass']
- **Mix** {'lufs': -9.5, 'air': 2.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.6, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Hyperpop (`hyperpop`)

Hyperpop: maximal, bright and glitchy - distorted 808s, supersaws, chiptune sparkle

- **Tempo** 150-170 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'major': [[0, 4, 5, 3], [3, 4, 5, 0]], 'minor': [[5, 6, 0, 0], [0, 5, 2, 6]]} · chord_bars 1 · chord size 4
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1.25
- **Drums** **kick** `X.....X...X.....` / `X..X......X..X..`; **snare** `........X.......`; **clap** `........X.......`
- **Drum kit** (synth preset) · preset `hard`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x.xx.x.xx.x.xx.x` / `x-x-x-x-x-x-x-x-`
- **Arp** {'rate': 0.5, 'mode': 'up', 'oct': 6}
- **Lead rhythm** `x.x.xx.x.x.xx.x.` / `xx.xx.x.x.xx.x..` / `x.x.x.x.x-x-x---` / `x-x-x-x-x-------`
- **Build-ups** default `triplet` · choices ['triplet', 'roll', 'hats', 'drumless', 'wash', 'pulse', 'stops']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `robotic` · melody `rhythmic_stabs` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `half_time` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare`  dB · rev=0.2
  - clap (snare): `clap` -20 dB
  - chat (top): `chat` -26 dB
  - bass (bass): `808` -13 dB · sc=0.6
  - chords (chords): `supersaw`  dB · rev=0.3 · sc=1.0 · alternatives ['pluck_saw', 'chip', 'polysynth']
  - pad (pad): `vox` -26 dB · rev=0.4 · sc=0.8 · alternatives ['warmpad', 'glasspad', 'choir', 'supersaw']
  - arp (arp): `chip` -26 dB · alternatives ['pluck_saw', 'pluck', 'acid']
  - lead (lead): `supersaw_lead`  dB · rev=0.3 · sc=0.5 · alternatives ['chip', 'vox', 'leadsaw']
- **Mix** {'lufs': -7.5, 'air': 3.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.6
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 66, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}

### K-pop (`kpop`)

K-pop: polished genre-hopping pop - punchy drums, bright plucks and piano, big pre-chorus lifts, catchy hooks

- **Tempo** 110-132 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [5, 6, 0, 0], [0, 3, 5, 4], [3, 4, 2, 5]], 'major': [[3, 4, 2, 5], [0, 4, 5, 3], [3, 4, 0, 5]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....` / `X..X..X...X.....` / `X...X...X...X...`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.xxx.x.x.xxx.x.` / `x.x.x.x.x.x.x.x.`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R..R..R.R..R....` / `R...R...R.R.R...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x..x..x.x..x..x.` / `x---x---x---x---` / `..x...x...x...x.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x.x.x..x..x.x...` / `x-x-x---x-x-x---` / `..x.x.x.x..x....` / `x--x--x-x-------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.2
  - clap (snare): `clap` -20 dB
  - chat (top): `chat` -27 dB
  - bass (bass): `fmbass` -14 dB · sc=0.5 · alternatives ['sawbass', '808', 'sf:slapbass', 'moogbass']
  - chords (chords): `pluck_saw`  dB · rev=0.25 · dly=0.15 · sc=0.4 · alternatives ['piano', 'stab', 'supersaw', 'guitar', 'epiano', 'polysynth', 'synthbrass']
  - pad (pad): `supersaw` -27 dB · rev=0.4 · sc=0.6 · alternatives ['strings', 'warmpad', 'choir', 'glasspad']
  - arp (arp): `pluck` -26 dB · dly=0.3 · alternatives ['chip', 'piano', 'mutedgtr']
  - lead (lead): `pluck` -18 dB · rev=0.3 · dly=0.2 · alternatives ['supersaw_lead', 'leadsaw']
- **Mix** {'lufs': -8.5, 'air': 2.0, 'low': 1.2} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.7, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Bright pluck & piano; Synth bass / 808; Supersaw pads; Vocal-chop hooks

### Teen Pop ('99) (`teen_pop`)

Late-90s teen pop: punchy dance-pop drums, dramatic minor chords, muted-guitar and synth-pluck riffs, string stabs, call-and-response hooks and a last-chorus key change

- **Tempo** 92-112 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4], [0, 5, 3, 4]], 'major': [[0, 4, 5, 3], [5, 3, 0, 4], [3, 4, 2, 5]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X.X.......` / `X..X..X...X.....` / `X.....X...X..X..`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.xxx.x.x.xxx.x.` / `xxxxxxxxxxxxxxxx`; **tamb** `....x.......x...`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R..R..R.R.R...R.` / `R...R..RR...R.R.` / `R.R...R.R.R...A.` · mode `pattern` · lowest note 28
- **Chord rhythm** `x..x..x.x..x..x.` / `x---x---x---x---` / `x.x...x.x.x...x.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.8}
- **Lead rhythm** `x.x.x..x..x.x...` / `x-x-x---x-x-x---` / `..x.x.x.x..x....` / `x--x--x-x-------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.25
  - clap (snare): `clap` -20 dB
  - chat (top): `chat` -27 dB
  - tamb (top): `tamb` -29 dB · pan=0.3
  - bass (bass): `moogbass` -14 dB · sc=0.4 · alternatives ['fmbass', 'sawbass', 'sf:fingerbass']
  - chords (chords): `pluck_saw` -22 dB · rev=0.25 · sc=0.3 · alternatives ['piano', 'mutedgtr', 'stab', 'guitar', 'polysynth']
  - pad (pad): `strings` -25 dB · rev=0.35 · alternatives ['polysynth', 'warmpad', 'choir']
  - arp (arp): `mutedgtr` -24 dB · pan=-0.3 · alternatives ['pluck', 'guitar', 'harp']
  - lead (lead): `pluck` -18 dB · rev=0.3 · dly=0.15 · alternatives ['guitar', 'strings', 'flute', 'synthbrass']
- **Mix** {'lufs': -9.0, 'air': 1.8, 'low': 1.2} · reverb 2.0 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.7, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Muted / funk guitar; Synth plucks & piano; String stabs; Punchy drum machine; Vocal-style lead with harmonies

### Alternative R&B (dark) (`alt_rnb`)

Alternative / dark R&B: slow half-time trap drums, deep gliding 808, washed-out reverb e-piano, airy pads and a lonely guitar or synth line

- **Tempo** 60-78 BPM · **scales** minor, dorian · swing 0.52 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 3, 5, 6], [0, 6, 5, 3]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 2]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X......X..X.....` / `X.........X..x..`; **snare** `........X.......`; **clap** `........X.......`; **ohat** `..............x.` / `................`
- **Drum kit** 808 · preset `default`
- **Bass** `R.......R.......` · mode `808` · lowest note 26
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x---..x-x-------` / `....x-x-x---....` / `x-------x-x-----` / `x---x-----x-....`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `808_slide` · drop `sudden` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -19 dB · rev=0.4
  - clap (snare): `clap` -21 dB · rev=0.4
  - chat (top): `chat` -28 dB · pan=0.15
  - ohat (top): `ohat` -30 dB · pan=-0.2
  - bass (bass): `808` -12 dB
  - chords (chords): `epiano` -20 dB · rev=0.55 · dly=0.2 · alternatives ['wurli', 'piano', 'polysynth']
  - pad (pad): `glasspad` -27 dB · rev=0.6 · alternatives ['warmpad', 'strings', 'choir']
  - lead (lead): `sf:cleanguitar` -22 dB · pan=-0.15 · rev=0.5 · dly=0.3 · alternatives ['softlead', 'epiano', 'guitar']
  - texture (fx): `texture` -40 dB
- **Mix** {'lufs': -10.5, 'air': 1.2, 'low': 2.2} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 50, 'punch': 70, 'decay': 12, 'len': 0.4}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': True, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Reverb-drenched Rhodes / DX e-piano; long 808; dark pads; reversed vocal textures; clean guitar

### Hopecore (euphoric breaks) (`hopecore`)

Hopecore (euphoric): bright, uplifting internet-core - fast chopped breakbeats and jersey-club kicks under big major chords on piano and supersaws, sparkling chiptune and bell arps, a soaring lead, stutter edits into emotional drops - nostalgic, hopeful and loud

- **Tempo** 150-172 BPM · **scales** major, lydian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'major': [[3, 4, 5, 0], [0, 4, 5, 3], [3, 4, 2, 5], [5, 3, 0, 4]], 'lydian': [[0, 1, 0, 1], [0, 1, 5, 1]]} · chord_bars 1 · chord size 4
- **Song form** `edm_b`: intro 8 [chords, kick, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [bass, chords, kick, snare, top] (crash) -> break 8 [arp, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [kick, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.X.......X..X..` / `X..X..X...X.....`; **snare** `....X.......X...` / `....X..x....X.x.`; **chat** `x.x.x.x.x.x.x.x.` / `xxxxxxxxxxxxxxxx`; **clap** `....x.......x...`; **crash** `X...............`
- **Drum kit** amen · preset `punchy` · break chops 0.45
- **Bass** `R-------R---R---` / `R-----R---R-R---` / `R-------R-------` · mode `808` · lowest note 29
- **Chord rhythm** `x-------x-------` / `x---x---x---x---` / `x-x---x-x---x---`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 6}
- **Lead rhythm** `x-x-x-x-x---x---` / `x---x-x-x-x-x---` / `x-xxx-x-x-------` / `x-x-x-x-x-x-x-x-`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `808_slide` · drop `long_build` · variation `progressive` · culture `radio_pop` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.25
  - clap (snare): `clap` -20 dB · rev=0.3
  - chat (top): `chat` -27 dB · pan=0.2
  - crash (top): `crash` -26 dB · rev=0.3
  - bass (bass): `808` -12 dB · sc=0.5 · alternatives ['reese', 'sinebass', 'sawbass']
  - chords (chords): `piano` -20 dB · rev=0.35 · sc=0.5 · alternatives ['supersaw', 'epiano', 'polysynth']
  - saws (chords): `supersaw` -25 dB · rev=0.4 · sc=0.8
  - pad (pad): `glasspad` -27 dB · rev=0.5 · sc=0.7 · alternatives ['warmpad', 'choir', 'solina']
  - arp (arp): `chip` -26 dB · pan=-0.25 · rev=0.3 · dly=0.3 · sc=0.6 · alternatives ['bell', 'pluck_saw', 'celesta', 'marimba']
  - lead (lead): `supersaw_lead` -19 dB · rev=0.4 · dly=0.3 · sc=0.3 · alternatives ['chip', 'leadsaw', 'bell']
- **Mix** {'lufs': -9.0, 'air': 2.0, 'low': 1.4, 'width': 1.2} · reverb 2.4 · sc_depth 0.45
- **Other rules** {'sc_release': 0.35, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Chopped Amen / Think break + punchy kick; 808; bright piano and supersaw chords; chiptune and bell arps; soaring saw or square lead; stutter / glitch edits

### Hopecore (dreamy, slow) (`hopecore_dreamy`)

Hopecore (dreamy): the slower, softer side - warm 120-135 BPM bounce with a sub-heavy kick and soft claps, gentle major piano and guitar loops, airy pads, music-box and bell melodies, a hopeful lead floating in reverb

- **Tempo** 118-136 BPM · **scales** major, lydian, mixolydian · swing 0.52 (unit 16) · humanise 0.0
- **Progressions** {'major': [[3, 4, 5, 0], [0, 4, 5, 3], [3, 0, 4, 5]], 'lydian': [[0, 1, 0, 1]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.......X.X.....` / `X..X......X.....`; **clap** `........X.......`; **chat** `x.x.x.x.x.x.x.x.` / `x...x...x.x.x...`; **shaker** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R---------------` / `R-------R-------` · mode `808` · lowest note 28
- **Chord rhythm** `x-------x-------` / `x---x---x-x-x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 6, 'prob': 0.85}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x-x-----` / `..x-x-x-x-------` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `half_time` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - clap (snare): `clap` -19 dB · rev=0.4
  - chat (top): `chat` -30 dB · pan=0.2
  - shaker (top): `shaker` -31 dB · pan=-0.3
  - bass (bass): `808` -12 dB · sc=0.4 · alternatives ['sinebass', 'moogbass', 'reese']
  - chords (chords): `piano` -20 dB · rev=0.45 · sc=0.4 · alternatives ['epiano', 'guitar', 'wurli']
  - gtr (chords): `guitar` -26 dB · pan=0.3 · rev=0.4
  - pad (pad): `warmpad` -26 dB · rev=0.6 · alternatives ['glasspad', 'choir', 'strings']
  - arp (arp): `celesta` -26 dB · pan=-0.25 · rev=0.5 · dly=0.35 · alternatives ['bell', 'kalimba', 'chip', 'marimba']
  - lead (lead): `softlead` -19 dB · rev=0.5 · dly=0.35 · alternatives ['bell', 'pluck']
- **Mix** {'lufs': -11.0, 'air': 1.4, 'low': 1.8} · reverb 3.0 · sc_depth 0.35
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Soft kick + 808 sub; claps; warm piano and clean guitar loops; airy pad; music box / bells; soft lead

### Minimal club pop (`club_pop`)

Minimal club pop (late-2010s-2020s): a dry, hard 4/4 around 123 with an off-kilter kick, a big low sub, cold detuned synth stabs and one bratty hook riff - sparse, loud, mono-ish in the low end, done in two minutes

- **Tempo** 120-126 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 0, 5, 5], [0, 6, 5, 6], [0, 0, 3, 4]], 'major': [[0, 0, 4, 4], [0, 5, 3, 4]]} · chord_bars 1 · chord size 3
- **Song form** `club_pop`: intro 4 [chords, fx] -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, snare, top] (crash) -> verse 12 [arp, bass, chords, kick, snare, top] -> break 4 [chords, fx] (build) -> chorus 12 [arp, bass, chords, kick, lead, snare, top] (drop) · form_scale 1
- **Drums** **kick** `X.X.............` / `X...X.X.........` / `X.X...X...X.....`; **snare** `....X.......X...` / `....X.......X..x`; **chat** `..x...x...x...x.` / `x.x.x.x.x.x.x.x.`
- **Drum kit** 707 · preset `hard`
- **Bass** `R-------R---....` / `R---..R-R-------` · mode `808` · lowest note 29
- **Chord rhythm** `x.x.....x.x.....` / `x...x...x...x...` / `x-..x-..x-..x-..`
- **Arp** {'rate': 4, 'mode': 'up', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x.x.x...x.x.....` / `x..x..x.x.......` / `x-x-x---x-------`
- **Build-ups** default `(category default)` · choices ['pause', 'none', 'stops'] · transitions ['gap', 'none', 'crash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -15 dB · rev=0.1
  - chat (top): `chat` -27 dB · pan=0.2
  - bass (bass): `808` -11 dB · sc=0.4
  - chords (chords): `supersaw` -22 dB · rev=0.2 · sc=0.5 · alternatives ['polysynth', 'stab', 'synthbrass']
  - arp (arp): `chip` -29 dB · dly=0.2 · alternatives ['pluck_saw', 'pluck', 'acid']
  - lead (lead): `leadsaw` -19 dB · rev=0.2 · alternatives ['supersaw_lead', 'chip', 'polysynth']
- **Mix** {'lufs': -7.5, 'air': 0.5, 'low': 2.5, 'width': 0.7} · reverb 1.2 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Hard dry drum machine (off-kilter kick), long 808 sub, detuned supersaw / square stabs, one bratty riff

### Glitchy IDM pop (`glitch_pop`)

Glitchy IDM pop / electronica: a soft, swung mid-tempo beat built from clicks, cut-up percussion and tiny edits, a warm melodic bass, plucked and mallet-like synths, gentle pads and a singing lead - intricate but warm, evolving for minutes without a real breakdown

- **Tempo** 96-108 BPM · **scales** major, minor, dorian · swing 0.55 (unit 16) · humanise 0.004
- **Progressions** {'major': [[0, 4, 5, 3], [0, 5, 3, 4]], 'minor': [[0, 5, 3, 4], [0, 6, 3, 4]], 'dorian': [[0, 3, 0, 6]]} · chord_bars 1 · chord size 4
- **Song form** `glitch_pop`: intro 8 [fx, pad, top] (filter_in) -> A 32 [bass, chords, fx, kick, pad, snare, top] -> B 32 [bass, chords, fx, kick, lead, pad, snare, top] -> C 32 [arp, bass, chords, fx, kick, lead, snare, top] (alt) -> B 24 [arp, bass, chords, fx, kick, lead, pad, snare, top] -> outro 8 [fx, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X..........X....` / `X.....x....X....` / `X..x.......X..x.`; **snare** `........X.......` / `........X.....x.`; **rim** `..x..x.x....x..x` / `.x..x...x.x...x.`; **chat** `x.xxx.x.xx.xx.x.` / `xxx.x.xx.x.xx.x.`; **shaker** `.o.o.o.o.o.o.o.o`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R--.R-.O..R-.R..` / `R-..R-.F..R-....` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---..x-..x-....` / `x-..x-..x-..x-..`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x---x-x-x-------` / `..x-x---x-x-....` / `x-------x-x-x---`
- **Build-ups** default `(category default)` · choices ['none', 'pickup', 'pause'] · transitions ['none', 'none', 'gap']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `half_time` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -17 dB · rev=0.3
  - rim (top): `rim` -27 dB · pan=0.3 · dly=0.2
  - chat (top): `chat` -29 dB · pan=-0.25
  - shaker (top): `shaker` -33 dB · pan=0.35
  - bass (bass): `moogbass` -14 dB · alternatives ['sinebass', 'sf:fingerbass', 'fmbass']
  - chords (chords): `epiano` -23 dB · rev=0.35 · alternatives ['polysynth', 'piano', 'wurli']
  - pad (pad): `glasspad` -28 dB · rev=0.5 · alternatives ['warmpad', 'solina']
  - arp (arp): `marimba` -27 dB · pan=0.25 · dly=0.3 · alternatives ['kalimba', 'pluck', 'vibes']
  - lead (lead): `softlead` -20 dB · rev=0.4 · dly=0.3 · alternatives ['flute', 'polysynth']
- **Mix** {'lufs': -11.0, 'air': 0.4, 'low': 1.4, 'width': 1.1} · reverb 2.4 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'eno_loops': False}
- **Sound brief** Clicky, cut-up soft drums with tiny stutter edits; warm Moog-ish bass; marimba / kalimba-like plucks; pads; a soft lead

## Afro, Latin & Caribbean

### Afrobeats (`afrobeats`)

Afrobeats: bouncy syncopated percussion, warm guitar chops, marimba hooks

- **Tempo** 98-112 BPM · **scales** major, minor, dorian · swing 0.56 (unit 16) · humanise 0.006
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X..x..X...X..x..` / `X.....X.X.....x.`; **snare** `....x.......x...` / `......x.......x.`; **rim** `..x..x....x..x..` / `...x..x..x..x...`; **shaker** `oxoxoxoxoxoxoxox`; **conga** `..o.x..o..o.x...` / `x..o..x...o..x..`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R..R....R.R.....` / `R...R.R...R..A..` / `R-..R...R-..R...` · mode `pattern` · lowest note 31
- **Chord rhythm** `.x.x..x..x.x..x.` / `x..x..x...x..x..`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5, 'rh': ['..x.x..x..x.x..x', '.x..x.x..x..x.x.', 'x..x.x..x.x..x..']}
- **Lead rhythm** `x.x..x.x..x.....` / `..x.x..x..x.x...` / `x..x..x.x.......` / `x-.x-.x-x-......`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `sub_only` · drop `sudden` · variation `sectional` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare` -19 dB · rev=0.15
  - rim (top): `rim` -27 dB · pan=0.3
  - shaker (top): `shaker` -28 dB · pan=-0.3
  - conga (top): `conga` -25 dB · pan=0.2
  - bass (bass): `sinebass`  dB · alternatives ['sf:fingerbass', 'fmbass', '808']
  - chords (chords): `epiano` -24 dB · pan=-0.25 · alternatives ['piano', 'sf:cleanguitar', 'guitar', 'organ']
  - pad (pad): `warmpad` -28 dB · rev=0.4 · alternatives ['strings', 'organ', 'glasspad']
  - arp (arp): `guitar` -23 dB · pan=0.25 · rev=0.15 · dly=0.15 · alternatives ['marimba', 'kalimba', 'pluck']
  - lead (lead): `flute`  dB · rev=0.3 · dly=0.2 · alternatives ['sax', 'pluck', 'marimba']
- **Mix** {'lufs': -9.5, 'air': 1.5, 'low': 1.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Amapiano (`amapiano`)

Amapiano: log-drum basslines, jazzy piano chords, rolling shakers, deep groove

- **Tempo** 108-115 BPM · **scales** minor, dorian · swing 0.57 (unit 16) · humanise 0.005
- **Progressions** {'minor': [[0, 3, 6, 5], [0, 5, 3, 4], [0, 6, 3, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]]} · chord_bars 1 · chord size 5
- **Song form** `amapiano`: intro 16 [chords, pad, top] (filter_in) -> verse 16 [chords, kick, pad, snare, top] -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> verse 16 [arp, bass, chords, kick, top] -> outro 16 [chords, kick, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X...X...X...X...`; **clap** `....x.......x...`; **shaker** `oxoxoxoxoxoxoxox` / `oxoXoxoxoxoXoxox`; **woodblock** `..x.....x.x.....` / `......x.....x...`; **chat** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R..F..R...R..F..` / `..R...F.R...R..O` / `R..R....F..R..R.` / `...R..R...F..R..` · mode `pattern` · lowest note 33
- **Chord rhythm** `x--.......x--...` / `...x-.....x-....` / `x---------------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x---........` / `..x-x-x---......` / `x-------x-------` / `....x-x-x-------`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `sudden` · variation `sectional` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - clap (snare): `clap` -21 dB · rev=0.3
  - shaker (top): `shaker` -27 dB · pan=0.3
  - woodblock (top): `woodblock` -27 dB · pan=-0.3
  - chat (top): `chat` -29 dB
  - bass (bass): `logdrum` -13 dB · sc=0.5
  - chords (chords): `piano`  dB · rev=0.3 · sc=0.4 · alternatives ['epiano', 'organ', 'wurli']
  - pad (pad): `warmpad` -27 dB · rev=0.5 · alternatives ['strings', 'choir', 'glasspad']
  - arp (arp): `kalimba` -26 dB · rev=0.3 · dly=0.3 · alternatives ['marimba', 'vibes', 'pluck']
  - lead (lead): `flute`  dB · rev=0.3 · dly=0.3 · alternatives ['sax', 'piano', 'kalimba']
- **Mix** {'lufs': -9.5, 'air': 1.0, 'low': 2.0} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Reggaeton (`reggaeton`)

Reggaeton: dembow rhythm, deep 808s, plucky synths, latin percussion

- **Tempo** 88-100 BPM · **scales** minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 5, 3, 4], [0, 3, 5, 4], [5, 3, 0, 4]] · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...` / `X...X...X...X..x` / `X...X..xX...X...`; **snare** `...X..X....X..X.` / `...X..X....X..XX` / `...X..X..x.X..X.` / `...X..X....X.XX.`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`; **tamb** `....x.......x...`; **conga** `..o...o...o...o.` / `..o..oo...o..oo.`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x..x..x...x..x..` / `x---------------`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 4, 'rh': ['x..x..x...x.x...', 'x..x..x.x.x..x..']}
- **Lead rhythm** `x.x.x..x..x.x...` / `x..x..x.x.x.....` / `..x.x.x.x..x....` / `x-x-x---x-------`
- **Build-ups** default `pause` · choices ['pause', 'stops', 'none'] · transitions ['gap', 'none', 'crash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `call_and_response` · bass `808_slide` · drop `sudden` · variation `sectional` · culture `underground_club` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -17 dB · rev=0.15
  - chat (top): `chat` -28 dB
  - tamb (top): `tamb` -28 dB · pan=0.3
  - conga (top): `conga` -27 dB · pan=-0.3
  - bass (bass): `808` -13 dB
  - chords (chords): `pluck_saw` -25 dB · rev=0.25 · dly=0.2 · alternatives ['piano', 'epiano', 'warmpad']
  - pad (pad): `warmpad` -27 dB · rev=0.4 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `acguitar` -22 dB · pan=-0.2 · rev=0.2 · alternatives ['sf:nylon', 'guitar', 'pluck_saw']
  - lead (lead): `pluck`  dB · rev=0.3 · dly=0.25 · alternatives ['acguitar', 'pluck_saw', 'flute']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 1.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.0}

### Moombahton (`moombahton`)

Moombahton: dembow groove at 110 with big-room synths and heavy drops

- **Tempo** 106-112 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 6, 5, 6], [0, 5, 3, 4]] · chord_bars 1 · chord size 3
- **Song form** `edm`: intro 8 [chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [chords, lead, pad] (alt, crash) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, kick, pad, top] (fade, crash) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `...X..X....X..X.`; **clap** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R..R..R.R..R..R.` / `R...R.R...R.R...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x..x..x.x..x..x.`
- **Arp** {'rate': 1, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x...x.x.x...x.` / `x..x..x.x.......` / `x.x.x.x.x.x.x.x.` / `x---x---x-------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `tension_release` · density `medium` · feel `robotic` · melody `call_and_response` · bass `rolling_groove` · drop `long_build` · variation `progressive` · culture `underground_club` · texture `club_punchy` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.2
  - clap (snare): `clap` -21 dB · rev=0.3
  - chat (top): `chat` -28 dB
  - tamb (top): `tamb` -28 dB · pan=0.3
  - bass (bass): `fmbass`  dB · sc=0.8 · alternatives ['sawbass', 'moogbass', 'reese']
  - chords (chords): `stab`  dB · rev=0.3 · sc=0.7 · alternatives ['supersaw', 'pluck_saw', 'organ']
  - pad (pad): `supersaw` -26 dB · rev=0.4 · sc=0.8 · alternatives ['warmpad', 'organ', 'strings']
  - arp (arp): `pluck_saw` -27 dB · dly=0.3 · sc=0.5 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `hoover`  dB · rev=0.3 · sc=0.5 · alternatives ['leadsaw', 'flute', 'supersaw_lead']
- **Mix** {'lufs': -8.5, 'air': 1.5, 'low': 1.5} · reverb 2.0 · sc_depth 0.5
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Dancehall (`dancehall`)

Dancehall: digital riddim, syncopated kick and snare, sub bass, synth stabs and chanted hooks

- **Tempo** 92-106 BPM · **scales** minor, dorian · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 5, 6, 0], [0, 3, 0, 3], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X..X......X.....` / `X.....X...X.....`; **snare** `...X..X....X..X.` / `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **rim** `..x...x...x...x.` / `...x..x....x..x.`
- **Drum kit** (synth preset) · preset `808`
- **Bass** `R..R......R.....` / `R..R...R..R.....` · mode `pattern` · lowest note 28
- **Chord rhythm** `..x...x...x...x.` / `x..x..x...x.....`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x..x.x..x.....` / `x..x..x.x.......` / `..x.x..x..x.x...` / `x-x-x---x-------`
- **Build-ups** default `(category default)` · choices ['pause', 'stops', 'none'] · transitions ['gap', 'none', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `sub_only` · drop `long_build` · variation `sectional` · culture `underground_club` · texture `club_punchy` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.15
  - chat (top): `chat` -27 dB
  - rim (top): `rim` -27 dB · pan=0.25
  - bass (bass): `sinebass` -12 dB · alternatives ['808', 'fmbass', 'moogbass']
  - chords (chords): `stab` -22 dB · rev=0.2 · alternatives ['pluck_saw', 'organ', 'marimba', 'steeldrum', 'mutedgtr']
  - pad (pad): `warmpad` -29 dB · rev=0.4 · alternatives ['strings', 'organ', 'glasspad']
  - lead (lead): `pluck` -19 dB · rev=0.3 · dly=0.25 · alternatives ['leadsaw', 'flute', 'steeldrum']
- **Mix** {'lufs': -9.0, 'air': 1.4, 'low': 2.0} · reverb 2.0 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.8, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'dub': 0.3, 'dub_beats': 0.75}
- **Sound brief** Synth stabs; Sub bass; Digital drums; Vocal chant / hook

### Baile Funk (`baile_funk`)

Baile funk (Brazilian funk carioca): tamborzao beat, booming 808, chanted vocal hooks, horn stabs

- **Tempo** 126-134 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 0, 5, 5], [0, 6, 5, 6], [0, 5, 6, 0]], 'phrygian': [[0, 1, 0, 1]]} · chord_bars 1 · chord size 3
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X..X..X...X..X..` / `X..X..X...X.X...`; **snare** `....X..X....X...` / `...X..X....X..X.`; **conga** `..o..o..o..o..o.` / `.o..o.o..o..o.o.`; **chat** `x.x.x.x.x.x.x.x.`; **clap** `....x.......x...`
- **Drum kit** (synth preset) · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x..x..x...x.....` / `x.......x.......`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x..x.x..x.....` / `x..x..x.x.......` / `xx.x.x..x.x.....` / `x-x-x---x-------`
- **Build-ups** default `stutter` · choices ['pause', 'stops'] · transitions ['gap', 'none', 'gap']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `robotic` · melody `call_and_response` · bass `808_slide` · drop `sudden` · variation `sectional` · culture `underground_club` · texture `club_punchy` · rhythm `half_time` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -17 dB · rev=0.15
  - clap (snare): `clap` -21 dB
  - conga (top): `conga` -21 dB · pan=0.25
  - chat (top): `chat` -28 dB
  - bass (bass): `808` -12 dB
  - chords (chords): `brass` -22 dB · rev=0.2 · alternatives ['stab', 'organ', 'pluck_saw']
  - lead (lead): `vox` -17 dB · rev=0.25 · dly=0.2 · alternatives ['brass', 'leadsaw', 'flute', 'cowbell']
- **Mix** {'lufs': -8.0, 'air': 1.5, 'low': 2.0, 'drive': 0.45} · reverb 2.0 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Tamborzao drums (kick + congas/toms); 808; Vocal chant hooks; Brass stabs

### Funk 150 / mandelao (`funk_150`)

Funk 150 / mandelao (Brazilian funk): the tamborzao groove sped up to 150 BPM - a driving kick pattern, bright clipped claps, tom and rim fills, a blown-out distorted sub, minimal synth stabs and chanted hooks; raw, sparse and relentless, with the beat cutting out for call-and-response

- **Tempo** 145-155 BPM · **scales** minor, phrygian · swing 0.52 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 6]], 'phrygian': [[0, 1, 0, 0], [0, 0, 1, 0]]} · chord_bars 1 · chord size 3
- **Song form** `funk_150`: intro 4 [chords, fx] -> drop 16 [bass, kick, lead, snare, top] (drop) -> break 4 [fx, lead] -> drop 16 [bass, chords, kick, lead, snare, top] (drop) -> verse 16 [bass, kick, snare, top] -> break 4 [chords, fx] (alt) -> drop 16 [arp, bass, chords, kick, lead, snare, top] (drop, alt) -> outro 4 [bass, kick] (fade) · form_scale 1
- **Drums** **kick** `X..X..X...X..X..` / `X..X..X...X.X...` / `X..X......X..X..`; **clap** `....x..x....x..x` / `....x.......x.x.`; **rim** `..x..x....x..x..` / `.x..x...x..x..x.`; **tom_lo** `......x.......x.` / `..............xx`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x..x..x...x.....` / `x.......x.......`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.3}
- **Lead rhythm** `x.x..x.x..x.....` / `xx.x.x..x.x.....` / `x..x..x.x.......`
- **Build-ups** default `(category default)` · choices ['pause', 'stops'] · transitions ['gap', 'none', 'gap'] · drops land plainly
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `808_slide` · drop `groove_drop` · variation `sectional` · culture `underground_club` · texture `club_punchy` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - clap (snare): `clap` -14 dB · rev=0.1
  - rim (top): `rim` -24 dB · pan=0.3
  - tom_lo (top): `tom` -22 dB · pan=-0.2
  - chat (top): `chat` -27 dB · pan=0.15
  - bass (bass): `808` -9 dB · sc=0.3
  - chords (chords): `stab` -21 dB · alternatives ['brass', 'organ', 'pluck_saw']
  - arp (arp): `pluck` -27 dB · dly=0.2 · alternatives ['chip', 'stab', 'pluck_saw']
  - lead (lead): `brass` -18 dB · rev=0.15 · alternatives ['leadsaw', 'flute', 'trumpet']
- **Mix** {'lufs': -7.0, 'air': 1.4, 'low': 2.6, 'width': 0.5, 'drive': 0.5} · reverb 2.0 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'pedal_sub': True}
- **Sound brief** 808 kick in the tamborzao pattern, clipped claps, rims and toms; distorted 808 sub; minimal stabs; chant hooks

## Chill, Lo-fi & Ambient

### Downtempo (`downtempo`)

Downtempo / chillout: laid-back beats, Rhodes & piano, warm pads, glassy bells

- **Tempo** 85-100 BPM · **scales** dorian, minor, major · swing 0.56 (unit 16) · humanise 0.008
- **Progressions** {'dorian': [[0, 3, 6, 2], [0, 3, 0, 4]], 'minor': [[0, 5, 3, 4], [0, 3, 6, 5]], 'major': [[0, 5, 3, 4], [3, 4, 2, 5]]} · chord_bars 1 · chord size 4
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.....x...X.....` / `X.......X.x.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **shaker** `.o.o.o.o.o.o.o.o`
- **Drum kit** back_to_life · preset `soft`
- **Bass** `R-----..R...F...` / `R-------R---A---` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x---x---x-------` / `....x-x-x-------` / `x-------x---x---` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `sub_only` · drop `long_build` · variation `sectional` · culture `bedroom_lofi` · texture `wet_and_spacious` · rhythm `swung_16ths` · harmony `modal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.3
  - chat (top): `chat` -28 dB
  - shaker (top): `shaker` -31 dB · pan=0.3
  - bass (bass): `sinebass`  dB · sc=0.4 · alternatives ['sf:fingerbass', 'sf:acbass', '808']
  - chords (chords): `epiano`  dB · rev=0.3 · alternatives ['piano', 'sf:nylon', 'guitar', 'harp', 'wurli', 'polysynth']
  - pad (pad): `warmpad` -26 dB · rev=0.5 · alternatives ['strings', 'choir', 'glasspad']
  - arp (arp): `bell` -27 dB · rev=0.5 · dly=0.35 · alternatives ['epiano', 'pluck', 'guitar', 'kalimba']
  - lead (lead): `softlead`  dB · rev=0.4 · dly=0.3 · alternatives ['flute', 'sax', 'cello']
  - vinyl (fx): `vinyl` -44 dB
- **Mix** {'lufs': -12.0, 'air': 0.5, 'low': 1.0} · reverb 2.6 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Lo-fi Hip Hop (`lofi`)

Lo-fi hip hop: swung boom-bap, jazzy 7th/9th Rhodes chords, warm bass, vinyl + tape wobble

- **Tempo** 72-88 BPM · **scales** major, dorian · swing 0.6 (unit 16) · humanise 0.012
- **Progressions** {'major': [[1, 4, 0, 5], [3, 2, 1, 4], [0, 5, 1, 4], [3, 4, 2, 5]], 'dorian': [[0, 3, 6, 2], [0, 3, 0, 4], [3, 4, 0, 0], [0, 6, 3, 4]]} · chord_bars 1 · chord size 5
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.....x...X.....` / `X......xX.....x.` / `X.x.......X..x..`; **snare** `....X.......X...`; **rim** `......o.......o.` / `..........o.....`; **chat** `x.ox.ox.x.ox.oxo` / `x.x.x.x.x.x.x.x.`
- **Drum kit** vintage · preset `soft`
- **Bass** `R.....R...F.....` / `R-----..A.R.....` / `R-------F---A---` · mode `pattern` · lowest note 33
- **Chord rhythm** `x-------x-------` / `x--------..x----` / `x---------------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x--.x-x---......` / `..x-x-x-x---....` / `x---..x-x-x-----` / `....x-x-x---x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `loose_human` · melody `long_lyrical` · bass `sub_only` · drop `long_build` · variation `sectional` · culture `bedroom_lofi` · texture `lofi_degraded` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare`  dB · rev=0.2
  - rim (top): `rim` -30 dB · pan=0.25
  - chat (top): `chat` -24 dB · pan=-0.15
  - bass (bass): `sinebass`  dB · sc=0.6 · alternatives ['sf:acbass', 'sf:fingerbass', '808']
  - chords (chords): `epiano`  dB · rev=0.25 · sc=0.8 · alternatives ['piano', 'sf:nylon', 'guitar', 'organ', 'wurli']
  - lead (lead): `pluck`  dB · pan=0.2 · rev=0.3 · dly=0.2 · alternatives ['epiano', 'flute', 'sax', 'kalimba', 'bell', 'sf:cleanguitar', 'vibes']
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -12.0, 'air': -3.0, 'low': 1.5, 'lofi': True} · reverb 1.6 · sc_depth 0.35
- **Other rules** {'sc_release': 0.6, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.015, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True}

### Ambient (`ambient`)

Ambient: slow evolving pads, glassy bells and a soft lead on tape loops of different lengths that drift against each other, huge reverbs, no drums

- **Tempo** 66-80 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.02
- **Progressions** [[0, 3, 5, 4], [0, 4, 5, 3], [3, 0, 4, 5]] · chord_bars 2 · chord size 4
- **Song form** `ambient`: intro 8 [fx, pad] (filter_in) -> A 16 [arp, bass, fx, pad] -> B 16 [arp, bass, fx, lead, pad, top] -> C 16 [bass, chords, fx, lead, pad] (alt) -> outro 8 [fx, pad] (fade) · form_scale 1
- **Drums** **shaker** `..o.......o.....` / `......o.......o.`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.45}
- **Lead rhythm** `x-------x-------` / `x-----------x---` / `....x-------x---` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `loose_human` · melody `long_lyrical` · bass `sub_only` · drop `none` · variation `sectional` · culture `bedroom_lofi` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - shaker (top): `shaker` -34 dB · pan=0.3 · rev=0.6
  - bass (bass): `sinebass` -20 dB · alternatives ['moogbass', '808', 'reese']
  - chords (chords): `epiano` -24 dB · rev=0.6 · alternatives ['piano', 'harp', 'strings', 'warmpad']
  - pad (pad): `warmpad` -20 dB · rev=0.7 · alternatives ['strings', 'choir', 'tremolo', 'glasspad', 'solina']
  - arp (arp): `bell` -26 dB · pan=-0.3 · rev=0.7 · dly=0.4 · alternatives ['celesta', 'kalimba', 'harp', 'marimba', 'vibes']
  - lead (lead): `softlead` -21 dB · pan=0.15 · rev=0.6 · dly=0.35 · alternatives ['flute', 'cello']
  - texture (fx): `texture` -36 dB · rev=0.5
- **Mix** {'lufs': -14.0, 'air': 1.5, 'low': 0.5, 'wobble': 0.15} · reverb 6.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 1.5, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.08, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'eno_loops': {'arp': 17, 'lead': 23}, 'no_rotation': True}

### Vaporwave (`vaporwave`)

Vaporwave: slowed 80s nostalgia - lush Rhodes, sax, chorused pads, tape haze

- **Tempo** 58-74 BPM · **scales** major, dorian · swing 0.52 (unit 16) · humanise 0.01
- **Progressions** {'major': [[3, 2, 1, 4], [1, 4, 0, 5], [3, 4, 2, 5]], 'dorian': [[0, 3, 6, 2]]} · chord_bars 1 · chord size 5
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.......X.x.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** vintage · preset `soft`
- **Bass** `R-----..R-..F...` / `R-------A-------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-----x-x-------` / `....x---x---x---` / `x---x---x-------` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `sub_only` · drop `long_build` · variation `sectional` · culture `bedroom_lofi` · texture `lofi_degraded` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.5
  - chat (top): `chat` -30 dB
  - bass (bass): `sinebass`  dB · alternatives ['fmbass', '808', 'moogbass']
  - chords (chords): `epiano`  dB · rev=0.5 · dly=0.2 · alternatives ['warmpad', 'organ', 'polysynth', 'wurli']
  - pad (pad): `warmpad`  dB · rev=0.6 · alternatives ['strings', 'choir', 'solina', 'glasspad']
  - lead (lead): `sax`  dB · rev=0.5 · dly=0.3 · alternatives ['epiano', 'softlead', 'sf:tenorsax', 'polysynth']
  - vinyl (fx): `vinyl` -42 dB
- **Mix** {'lufs': -12.0, 'air': -3.0, 'low': 1.4, 'lofi': True, 'wobble': 1.8} · reverb 4.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.02, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True}

### Ambient beat (dark, sub-heavy) (`ambient_beat`)

Ambient beat (dark, sub-heavy, airy): slow half-time drums tucked under washed-out pads, a long sustained 808 sub doing most of the work, soft ticking hats, reversed swells and distant bells - wide, dark and weightless

- **Tempo** 140-150 BPM · **scales** minor, major, lydian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 3, 6], [0, 3, 5, 4], [5, 3, 0, 0]], 'major': [[0, 3, 5, 4], [3, 0, 4, 5]], 'lydian': [[0, 1, 0, 1]]} · chord_bars 2 · chord size 4
- **Song form** `halftime`: intro 8 [chords, pad, top] (filter_in) -> build 8 [arp, chords, pad, top] (build) -> drop 16 [bass, chords, kick, lead, pad, snare, top] (drop) -> break 8 [arp, chords, lead, pad] (alt) -> build 8 [arp, chords, lead, top] (build, alt) -> drop 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.......X.....x.` / `X..........X....`; **snare** `........X.......`; **chat** `x...x...x...x...` / `x.x...x.x...x.x.` / `..x...x...x...x.`; **rim** `......x.......x.` / `...x.......x....`
- **Drum kit** (synth preset) · preset `808`
- **Bass** `R---------------` / `R-------R-------` · mode `808` · lowest note 28
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.35}
- **Lead rhythm** `x-------........` / `........x-------` / `x---....x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `robotic` · melody `minimal_motivic` · bass `808_slide` · drop `long_build` · variation `sectional` · culture `bedroom_lofi` · texture `massive_reverb` · rhythm `half_time` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -20 dB · rev=0.6
  - chat (top): `chat` -32 dB · pan=0.25
  - rim (top): `rim` -31 dB · pan=-0.3 · rev=0.5
  - bass (bass): `808` -11 dB · alternatives ['sinebass', 'moogbass', 'reese']
  - chords (chords): `glasspad` -24 dB · rev=0.7 · alternatives ['warmpad', 'epiano', 'piano']
  - pad (pad): `warmpad` -24 dB · rev=0.8 · alternatives ['glasspad', 'choir', 'strings']
  - arp (arp): `bell` -30 dB · pan=-0.3 · rev=0.8 · dly=0.5 · alternatives ['celesta', 'kalimba', 'pluck']
  - lead (lead): `softlead` -24 dB · pan=0.2 · rev=0.7 · dly=0.4 · alternatives ['glasspad', 'bell', 'flute']
  - texture (fx): `texture` -34 dB · rev=0.5
- **Mix** {'lufs': -12.0, 'air': -2.0, 'low': 2.4, 'width': 1.4} · reverb 4.0 · sc_depth 0.25
- **Other rules** {'sc_release': 0.5, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.85}
- **Sound brief** Long 808 sub; quiet half-time kit; huge reverb pads (Juno / glass); reversed swells; bells far away

### 90s new-age chill (chant) (`new_age_chant`)

Early-90s new-age chill: a slow, heavy hip-hop funk break around 96 under monk-like chanted choir chords, a breathy bamboo-flute melody, deep pads and a single pedal bass note - mysterious, spacious and hypnotic

- **Tempo** 92-100 BPM · **scales** minor, dorian, phrygian · swing 0.52 (unit 16) · humanise 0.005
- **Progressions** {'minor': [[0, 0, 6, 0], [0, 0, 5, 6]], 'dorian': [[0, 3, 0, 0]], 'phrygian': [[0, 1, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `new_age_chant`: intro 4 [fx, kick, pad, top] -> A 16 [bass, fx, kick, pad, snare, top] -> B 20 [bass, chords, fx, kick, lead, pad, snare, top] -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (crash) -> outro 8 [fx, lead, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.....X...X.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** funky_drummer · preset `soft`
- **Bass** `R---------------` / `R-------R-------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'up', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `........x-------`
- **Build-ups** default `(category default)` · choices ['none', 'pickup'] · transitions ['none', 'crash', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `sub_only` · drop `long_build` · variation `sectional` · culture `bedroom_lofi` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.35
  - chat (top): `chat` -28 dB
  - bass (bass): `sinebass` -15 dB · alternatives ['808', 'moogbass', 'reese']
  - chords (chords): `choir` -21 dB · rev=0.6 · alternatives ['strings', 'warmpad', 'organ']
  - pad (pad): `warmpad` -26 dB · rev=0.6 · alternatives ['choir', 'glasspad', 'strings']
  - arp (arp): `harp` -29 dB · rev=0.5 · dly=0.3 · alternatives ['celesta', 'pizz', 'piano']
  - lead (lead): `flute` -19 dB · rev=0.5 · dly=0.3 · alternatives ['tinwhistle', 'oboe', 'clarinet']
  - texture (fx): `texture` -36 dB · rev=0.6
- **Mix** {'lufs': -11.0, 'air': 0.8, 'low': 1.2, 'width': 1.2} · reverb 3.6 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 56, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'pedal_sub': True, 'repetition': 0.8}
- **Sound brief** Funk breakbeat (slow); male choir chant chords; shakuhachi / pan flute melody; deep pads; one pedal bass note

### Mid-fi synth-funk / chillwave (`midfi_synthfunk`)

Mid-fi synth-funk / chillwave: a slow, crunchy drum-machine groove around 80-100 with a fat gated snare, a rubbery analog bass, detuned, warbly poly-synth chords and arps soaked in tape wobble and chorus, a warm square lead - nostalgic, hazy and funky, like a worn 80s VHS

- **Tempo** 80-100 BPM · **scales** major, dorian, minor, lydian · swing 0.52 (unit 16) · humanise 0.003
- **Progressions** {'major': [[3, 4, 2, 5], [0, 5, 3, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]], 'minor': [[0, 5, 3, 6]], 'lydian': [[0, 1, 0, 1]]} · chord_bars 1 · chord size 4
- **Song form** `midfi_synthfunk`: intro 16 [bass, kick, pad, snare] (filter_in) -> A 32 [bass, chords, kick, lead, pad, snare, top] -> B 20 [arp, bass, chords, kick, lead, snare, top] (crash) -> break 8 [bass, kick, pad, snare] -> A 16 [bass, chords, kick, lead, pad, snare, top] -> break 12 [chords, pad, top] (alt) -> B 8 [arp, bass, chords, kick, lead, snare, top] (alt) -> outro 4 [pad] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X..X....X.......` / `X.....X.X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`; **tamb** `......x.......x.`
- **Drum kit** linn · preset `linn`
- **Bass** `R--.R-.O..R-.R..` / `R-..R-R-..R-..O.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---..x-..x-....` / `x-------x-------`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.85}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x-x-x---`
- **Build-ups** default `(category default)` · choices ['filter', 'pause', 'none'] · transitions ['none', 'none', 'tapestop', 'gap']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `nostalgic_simple` · bass `rolling_groove` · drop `long_build` · variation `sectional` · culture `bedroom_lofi` · texture `tape_degraded` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - tamb (top): `tamb` -31 dB · pan=-0.3
  - bass (bass): `moogpluck` -12 dB · sc=0.3 · alternatives ['sawbass', 'fmbass', 'sf:fingerbass']
  - chords (chords): `polysynth` -21 dB · rev=0.35 · alternatives ['synthbrass', 'epiano', 'stab']
  - pad (pad): `solina` -26 dB · rev=0.5 · alternatives ['glasspad', 'strings', 'warmpad']
  - arp (arp): `pluck_saw` -26 dB · pan=0.25 · dly=0.3 · alternatives ['chip', 'pluck', 'stab']
  - lead (lead): `softlead` -19 dB · rev=0.3 · dly=0.3 · alternatives ['leadsaw', 'polysynth', 'flute']
- **Mix** {'lufs': -10.0, 'air': 0.2, 'low': 1.8, 'width': 1.1, 'lofi': True, 'wobble': 2.5} · reverb 2.6 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** LinnDrum-style kit with gated snare; Juno / Moog bass; detuned poly-synth chords; bright arps; square lead; tape wobble + chorus on everything

## Retro & Video Game

### Synthwave (`synthwave`)

80s synthwave/retrowave: gated-reverb snares, pulsing octave bass, supersaws, saw lead

- **Tempo** 90-112 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 6, 5, 6], [5, 3, 0, 4], [0, 3, 5, 4]] · chord_bars 1 · chord size 3
- **Song form** `synthwave`: intro 8 [arp, chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> solo 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [arp, chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...` / `X.......X.x.....`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `xoxoxoxoxoxoxoxo`; **tom** `................` / `................`
- **Drum kit** linn · preset `punchy`
- **Bass** `R.O.R.O.R.O.R.O.` / `RRRRRRRRRRRRRRRR` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x---x---x-x-` / `x---x---x-x-x---` / `x-----x-x---x---` / `x-------x-------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `underground_club` · texture `dry_and_upfront` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.5
  - clap (snare): `clap` -22 dB · rev=0.4
  - chat (top): `chat`  dB · pan=0.2
  - tom (top): `tom` -20 dB · pan=-0.2 · rev=0.45
  - bass (bass): `sawbass`  dB · sc=0.9 · alternatives ['fmbass', 'moogbass', 'reese']
  - chords (chords): `supersaw`  dB · rev=0.35 · sc=0.7 · alternatives ['brass', 'stab', 'epiano', 'warmpad', 'polysynth', 'synthbrass']
  - pad (pad): `warmpad`  dB · rev=0.4 · sc=0.7 · alternatives ['strings', 'choir', 'solina', 'polysynth', 'glasspad']
  - arp (arp): `pluck_saw` -27 dB · pan=-0.2 · rev=0.25 · dly=0.35 · sc=0.6 · alternatives ['chip', 'pluck', 'stab']
  - lead (lead): `leadsaw`  dB · rev=0.35 · dly=0.3 · sc=0.3 · alternatives ['supersaw_lead', 'sax', 'softlead', 'brass', 'synthbrass', 'polysynth']
  - solo_sax (lead): `sax` -18 dB · rev=0.45 · dly=0.3
  - solo_gtr (lead): `guitar` -19 dB · rev=0.4 · dly=0.35
- **Mix** {'lufs': -9.5, 'air': 2.0, 'low': 1.0} · reverb 2.4 · sc_depth 0.5
- **Other rules** {'sc_release': 0.5, 'delay_beats': 0.75, 'kit_override': {'snare': {'tone': 200, 'snap': 1.0, 'decay': 12}}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.7, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'solos': ['solo_sax', 'solo_gtr']}

### Chiptune (`chiptune`)

8-bit chiptune: pulse-wave leads, triangle bass, noise drums, lightning arpeggios

- **Tempo** 140-160 BPM · **scales** major · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 4, 5, 3], [0, 5, 3, 4], [5, 3, 0, 4], [0, 3, 4, 4]] · chord_bars 1 · chord size 3
- **Song form** `chip`: intro 4 [arp, bass] -> verse 16 [arp, bass, kick, snare, top] -> chorus 16 [arp, bass, kick, lead, snare, top] -> verse 16 [arp, bass, kick, snare, top] -> chorus 16 [arp, bass, kick, lead, snare, top] -> bridge 8 [arp, bass, lead, top] (alt) -> chorus 16 [arp, bass, kick, lead, snare, top] -> outro 4 [arp, bass, kick] (fade) · form_scale 1
- **Drums** **chipkick** `X.......X.x.....` / `X...X...X...X...`; **chipsnare** `....X.......X...`; **chiphat** `x.x.x.x.x.x.x.x.` / `xxxxxxxxxxxxxxxx`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.O.R.O.R.O.R.O.` / `R.R.O.R.R.R.O.R.` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 0.5, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x-x-x.x.x---` / `x-x-x-x-x---x---` / `x.xxx.x.x-x-x---` / `x-----x-x-------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `sparse` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `underground_club` · texture `dry_and_upfront` · rhythm `on_the_grid` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - chipkick (kick role - the genre's low drum): `chipkick`  dB
  - chipsnare (snare): `chipsnare`  dB
  - chiphat (top): `chiphat` -27 dB
  - bass (bass): `chipbass` -16 dB · alternatives ['sawbass', 'sinebass', 'fmbass']
  - arp (arp): `chip` -26 dB · pan=-0.2 · alternatives ['pluck_saw', 'pluck', 'acid']
  - lead (lead): `chip`  dB · pan=0.1 · rev=0.12 · dly=0.15 · alternatives ['leadsaw', 'pluck_saw', 'pluck']
- **Mix** {'lufs': -10.0, 'air': 0.5, 'low': 0.5} · reverb 0.8 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['chipsnare'], 'bass_gate': 0.8, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'chipkick', 'suggest': ''}

### 90s video game (PS1-era) (`ps1_game`)

90s video game soundtrack (PlayStation-era): sample-based breakbeats and electronic drums, a funky synth / slap bass, sampled strings and brass stabs, Rhodes and bell arps, a heroic synth lead - all through the console sound chip: 22 kHz, a little crunchy, with its own reverb

- **Tempo** 104-128 BPM · **scales** minor, dorian, harmonic_minor · swing 0.52 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 6, 4], [0, 3, 5, 4], [0, 6, 5, 4], [5, 6, 0, 0]], 'dorian': [[0, 3, 0, 6], [0, 6, 3, 4]], 'harmonic_minor': [[0, 5, 4, 4], [0, 3, 4, 0]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.X.......X.....` / `X.........XX....` / `X.X.......X..X..`; **snare** `....X..x.x..X...` / `....X.......X..x`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.xxx.x.x.xx`; **ohat** `..............x.`; **crash** `X...............` / `................`
- **Drum kit** think · preset `707` · break chops 0.12
- **Bass** `R..O.R...RR.O..A` / `R.R..O.R..R.O.R.` / `R...R.O.R..O.R..` · mode `pattern` · lowest note 31
- **Chord rhythm** `x...x.....x.x...` / `x-------x-------` / `..x...x...x...x.`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5, 'prob': 0.85}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x-x-x---` / `x-------x---x-x-` / `x--.x--.x-x-x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `sectional` · culture `underground_club` · texture `tape_degraded` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -16 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - crash (top): `crash` -27 dB · rev=0.3
  - bass (bass): `fmbass` -14 dB · alternatives ['sf:slapbass', 'sawbass', 'moogbass']
  - chords (chords): `strings` -23 dB · rev=0.35 · alternatives ['polysynth', 'synthbrass', 'epiano']
  - stabs (chords): `brass` -24 dB · rev=0.3
  - pad (pad): `epiano` -27 dB · rev=0.3 · alternatives ['strings', 'warmpad', 'choir']
  - arp (arp): `bell` -28 dB · pan=0.25 · rev=0.35 · dly=0.25 · alternatives ['marimba', 'pluck_saw', 'vibes']
  - lead (lead): `leadsaw` -19 dB · rev=0.35 · dly=0.2 · alternatives ['softlead', 'synthbrass', 'sax', 'flute']
- **Mix** {'lufs': -11.0, 'air': 0.0, 'low': 1.2, 'lofi': 0.25} · reverb 2.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.55, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True}
- **Sound brief** Sampled break + 707 / 909 hits; slap or synth bass; ROM strings & brass stabs; Rhodes; bell arp; synth lead; console reverb (PlayStation SPU)

### Dark Synthwave (`dark_synthwave`)

Dark synthwave (neon-noir): slower and minor - a heavy pulsing analog bass, cold supersaw chords, string-machine fog, a lonely saw lead and a stark gated drum machine; night-drive rather than sunset

- **Tempo** 85-105 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 6, 5, 3], [0, 3, 0, 4], [0, 5, 6, 0]], 'phrygian': [[0, 1, 0, 1], [0, 1, 5, 0]], 'harmonic_minor': [[0, 3, 4, 0], [0, 5, 4, 4]]} · chord_bars 1 · chord size 4
- **Song form** `synthwave`: intro 8 [arp, chords, kick, pad, top] (filter_in) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> solo 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [arp, chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...` / `X.......X.......` / `X.......X.x.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x...x...x...x...`
- **Drum kit** linn · preset `punchy`
- **Bass** `RRRRRRRRRRRRRRRR` / `R.O.R.O.R.O.R.O.` / `R-------R-------` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-----x-x-------`
- **Build-ups** default `filter` · choices ['filter', 'hats', 'drumless', 'wash', 'pulse', 'tapestop', 'pickup', 'ride']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `underground_club` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -17 dB · rev=0.45
  - chat (top): `chat` -29 dB · pan=0.2
  - bass (bass): `moogbass` -14 dB · sc=0.4 · alternatives ['sawbass', 'reese', 'sinebass']
  - chords (chords): `supersaw` -22 dB · rev=0.45 · sc=0.5 · alternatives ['polysynth', 'solina', 'warmpad']
  - pad (pad): `solina` -25 dB · rev=0.55 · alternatives ['warmpad', 'choir', 'glasspad']
  - arp (arp): `pluck_saw` -26 dB · pan=0.2 · rev=0.3 · dly=0.35 · alternatives ['pluck', 'bell', 'chip']
  - lead (lead): `leadsaw` -19 dB · rev=0.45 · dly=0.3 · alternatives ['supersaw_lead', 'softlead', 'hoover']
  - texture (fx): `texture` -34 dB
- **Mix** {'lufs': -11.0, 'air': 0.8, 'low': 1.8} · reverb 2.8 · sc_depth 0.25
- **Other rules** {'sc_release': 0.5, 'delay_beats': 0.75, 'kit_override': {'snare': {'tone': 190, 'snap': 1.0, 'decay': 14}}, 'snare_tracks': ['snare'], 'bass_gate': 0.8, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Pulsing analog bass (16ths or octaves); dark supersaw / poly chords; string machine; mono saw lead; gated-reverb snare; low air, heavy low end

## Hauntology

### Hauntology (`hauntology`)

Hauntology: warped-tape analog synths, slow dusty hip-hop breaks, nostalgic melodies and string-machine haze, all drifting like an old cassette

- **Tempo** 78-96 BPM · **scales** major, dorian, mixolydian, minor · swing 0.56 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 3, 0, 3], [0, 5, 3, 4], [3, 0, 3, 0], [0, 2, 3, 0]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]], 'mixolydian': [[0, 6, 0, 6], [0, 3, 6, 0]], 'minor': [[0, 5, 6, 0], [0, 3, 0, 3]]} · chord_bars 1 · chord size 4
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.......X.x.....` / `X......XX.......` / `X.....x...X.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x...x...x...x...`
- **Drum kit** vintage · preset `soft`
- **Bass** `R-------R---....` / `R-----..R-......` / `R-------F-------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-----x-x-------` / `x---------------`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `nostalgic_simple` · bass `sub_only` · drop `sudden` · variation `sectional` · culture `nostalgic_memory` · texture `tape_degraded` · rhythm `swung_16ths` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -16 dB
  - snare (snare): `snare` -19 dB · rev=0.35
  - chat (top): `chat` -30 dB
  - bass (bass): `sinebass` -15 dB · alternatives ['moogbass', 'fmbass', '808']
  - chords (chords): `polysynth` -22 dB · rev=0.45 · dly=0.15 · alternatives ['solina', 'wurli', 'epiano', 'warmpad']
  - pad (pad): `solina` -25 dB · rev=0.5 · alternatives ['warmpad', 'glasspad', 'choir', 'strings']
  - arp (arp): `polysynth` -26 dB · pan=0.25 · rev=0.4 · dly=0.3 · alternatives ['vibes', 'bell', 'celesta']
  - lead (lead): `softlead` -19 dB · rev=0.45 · dly=0.3 · alternatives ['vox', 'polysynth', 'flute', 'vibes']
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -12.5, 'air': -1.5, 'low': 1.5, 'lofi': True, 'wobble': 3.0} · reverb 3.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Detuned analog poly (Prophet / Juno); String machine; Sine lead or vocal sample; Dusty drum break; tape + vinyl

### Hauntology II (sunlit tape) (`hauntology_sunlit`)

Hauntology II - sunlit tape: warm detuned analog chords and a wobbling mono-synth melody over a mellow hip-hop break, nostalgic and bright, like a 1970s nature film on a stretched cassette

- **Tempo** 82-96 BPM · **scales** major, mixolydian, dorian · swing 0.55 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 3, 0, 3], [0, 5, 3, 4], [3, 0, 3, 4]], 'mixolydian': [[0, 6, 0, 6], [0, 6, 3, 0]], 'dorian': [[0, 3, 0, 3], [0, 1, 0, 3]]} · chord_bars 1 · chord size 4
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.....x.X.......` / `X.......X.x.....` / `X......XX.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x...x...x...x...`
- **Drum kit** vintage · preset `soft`
- **Bass** `R-------R-------` / `R-----..R---....` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.75}
- **Lead rhythm** `x-------x-------` / `x---x---x-------` / `x-------x---x---` / `x-----x-x-------`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `nostalgic_simple` · bass `rolling_groove` · drop `sudden` · variation `sectional` · culture `nostalgic_memory` · texture `tape_degraded` · rhythm `swung_16ths` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare` -18 dB · rev=0.3
  - chat (top): `chat` -30 dB
  - bass (bass): `moogbass` -15 dB · alternatives ['sinebass', 'sf:fingerbass', 'fmbass']
  - chords (chords): `polysynth` -21 dB · rev=0.45 · dly=0.1 · alternatives ['solina', 'wurli', 'epiano']
  - pad (pad): `solina` -26 dB · rev=0.5 · alternatives ['warmpad', 'choir', 'strings']
  - arp (arp): `vibes` -27 dB · pan=0.25 · rev=0.45 · dly=0.25 · alternatives ['bell', 'celesta', 'polysynth']
  - lead (lead): `polysynth` -19 dB · rev=0.4 · dly=0.3 · alternatives ['softlead', 'flute', 'vibes']
  - texture (fx): `texture` -39 dB
  - vinyl (fx): `vinyl` -41 dB
- **Mix** {'lufs': -12.0, 'air': -1.0, 'low': 1.6, 'lofi': True, 'wobble': 4.5} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.85}
- **Sound brief** Detuned Prophet / Juno chords; wobbling mono lead; Moog bass; mellow sampled break; children's choir pad; tape

### Hauntology III (dark film haze) (`hauntology_dark`)

Hauntology III - dark film haze: slower and eerier - long detuned drones, a ghostly choir, sparse heavy drums, bells half-buried in hiss, a melody that sounds remembered wrong

- **Tempo** 64-80 BPM · **scales** minor, dorian, phrygian · swing 0.54 (unit 16) · humanise 0.014
- **Progressions** {'minor': [[0, 5, 0, 5], [0, 3, 5, 6], [0, 6, 5, 0]], 'dorian': [[0, 3, 0, 3], [0, 0, 6, 3]], 'phrygian': [[0, 1, 0, 1], [0, 1, 6, 0]]} · chord_bars 2 · chord size 4
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.......X.......`; **snare** `....X.......X...`; **chat** `x...x...x...x...` / `..x...x...x...x.`
- **Drum kit** vintage · preset `soft`
- **Bass** `R---------------` / `R-------R-------` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.45}
- **Lead rhythm** `x---------------` / `x-------x-------` / `x-----------x---`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `nostalgic_simple` · bass `sub_only` · drop `sudden` · variation `low` · culture `nostalgic_memory` · texture `lofi_degraded` · rhythm `swung_16ths` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare` -19 dB · rev=0.45
  - chat (top): `chat` -31 dB
  - bass (bass): `sinebass` -15 dB · alternatives ['moogbass', '808', 'reese']
  - chords (chords): `polysynth` -22 dB · rev=0.55 · dly=0.15 · alternatives ['solina', 'glasspad', 'warmpad']
  - pad (pad): `choir` -27 dB · rev=0.6 · alternatives ['solina', 'glasspad', 'strings']
  - arp (arp): `bell` -29 dB · pan=0.3 · rev=0.6 · dly=0.35 · alternatives ['celesta', 'vibes', 'pluck']
  - lead (lead): `softlead` -21 dB · rev=0.55 · dly=0.35 · alternatives ['polysynth', 'flute']
  - texture (fx): `texture` -38 dB
  - vinyl (fx): `vinyl` -39 dB
- **Mix** {'lufs': -13.0, 'air': -2.5, 'low': 1.5, 'lofi': True, 'wobble': 4.0} · reverb 4.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.9}
- **Sound brief** Detuned analog drones; choir / vocal pad; bell & music box; distant break; heavy tape wobble and hiss

### Hauntology - wobbly melody (slow beat) (`hauntology_melody`)

Hauntology - wobbly melody, slow beat: a dusty 80-90 BPM hip-hop beat under a simple, sad-happy detuned synth melody that drifts in and out of tune on old tape, a round warm bass, faded analog pads and very little top end

- **Tempo** 78-90 BPM · **scales** dorian, major, mixolydian · swing 0.55 (unit 16) · humanise 0.006
- **Progressions** {'dorian': [[0, 3, 0, 3], [0, 6, 3, 0], [0, 3, 6, 0]], 'mixolydian': [[0, 6, 0, 6], [0, 6, 3, 0]], 'major': [[0, 3, 0, 4], [3, 0, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.......X.x.....` / `X.....x.X.......` / `X.......X...x...`; **snare** `....X.......X...`; **clap** `....x.......x...`; **chat** `x.x.x.x.x.x.x.x.` / `..x...x...x...x.`
- **Drum kit** vintage · preset `soft`
- **Bass** `R-------R-------` / `R-----..R---....` / `R-------F-------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x---x-x-x-------` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `nostalgic_simple` · bass `rolling_groove` · drop `long_build` · variation `low` · culture `nostalgic_memory` · texture `lofi_degraded` · rhythm `swung_16ths` · harmony `modal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -18 dB · rev=0.35
  - clap (snare): `clap` -24 dB · rev=0.4
  - chat (top): `chat` -31 dB
  - bass (bass): `moogbass` -14 dB · alternatives ['sinebass', 'sf:fingerbass', 'fmbass']
  - chords (chords): `solina` -24 dB · rev=0.5 · alternatives ['polysynth', 'warmpad', 'synthbrass']
  - pad (pad): `warmpad` -27 dB · rev=0.55 · alternatives ['solina', 'choir', 'strings']
  - arp (arp): `vibes` -28 dB · pan=-0.25 · rev=0.5 · dly=0.3 · alternatives ['bell', 'polysynth', 'epiano']
  - lead (lead): `polysynth` -18 dB · rev=0.45 · dly=0.3 · alternatives ['softlead', 'vibes', 'synthbrass']
  - texture (fx): `texture` -39 dB
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -13.0, 'air': -3.0, 'low': 1.6, 'lofi': True, 'wobble': 4.5} · reverb 2.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True, 'repetition': 0.9}
- **Sound brief** Detuned mono synth melody (pitch drifting on tape); warm sub; faded string-machine pad; dusty soft kit

### Hauntology - beatless tape lullaby (`hauntology_lullaby`)

Hauntology - beatless tape lullaby: no drums at all, just slow, warm chords on a detuned piano or string machine and a little melody, played off a worn tape that sags in pitch - quiet, muffled, short and wistful

- **Tempo** 60-76 BPM · **scales** major, lydian, mixolydian · swing 0.5 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 3, 0, 4], [0, 5, 3, 4], [3, 0, 3, 0]], 'lydian': [[0, 1, 0, 1]], 'mixolydian': [[0, 6, 0, 3]]} · chord_bars 2 · chord size 4
- **Song form** `ambient`: intro 8 [fx, pad] (filter_in) -> A 16 [arp, bass, fx, pad] -> B 16 [arp, bass, fx, lead, pad, top] -> C 16 [bass, chords, fx, lead, pad] (alt) -> outro 8 [fx, pad] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R---------------` · mode `pattern` · lowest note 36
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 4, 'mode': 'up', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x-------x-------` / `x---x---x-------` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `drifting` · melody `nostalgic_simple` · bass `sub_only` · drop `none` · variation `sectional` · culture `nostalgic_memory` · texture `lofi_degraded` · rhythm `straight_16ths` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - bass (bass): `sinebass` -22 dB · alternatives ['808', 'moogbass', 'reese']
  - chords (chords): `piano` -20 dB · rev=0.55 · alternatives ['epiano', 'solina', 'polysynth']
  - pad (pad): `solina` -24 dB · rev=0.6 · alternatives ['warmpad', 'strings', 'glasspad']
  - arp (arp): `celesta` -29 dB · pan=0.25 · rev=0.6 · dly=0.3 · alternatives ['vibes', 'bell', 'harp']
  - lead (lead): `softlead` -21 dB · rev=0.55 · dly=0.3 · alternatives ['polysynth', 'flute']
  - texture (fx): `texture` -42 dB
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -17.0, 'air': -6.0, 'low': 0.4, 'lofi': True, 'wobble': 6.0, 'width': 1.4} · reverb 3.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True, 'repetition': 0.85}
- **Sound brief** Detuned piano / string machine chords; a soft melody; heavy tape wow and flutter; no drums

### Hauntology - campfire guitar haze (`hauntology_campfire`)

Hauntology - campfire guitar haze: looping acoustic guitar figures and slowly strummed chords over a warm, loose 90 BPM beat, a deep round bass, reversed swells and soft synths - sunlit, hazy and outdoors

- **Tempo** 82-94 BPM · **scales** major, mixolydian, dorian · swing 0.55 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 3, 0, 3], [0, 4, 3, 0], [3, 0, 4, 0]], 'mixolydian': [[0, 6, 3, 0]], 'dorian': [[0, 3, 0, 3]]} · chord_bars 1 · chord size 4
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.......X.x.....` / `X.....x...X.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **shaker** `..x...x...x...x.`
- **Drum kit** vintage · preset `soft`
- **Bass** `R-------R---....` / `R-----..R-------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x-----x-x-------` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4, 'rh': ['x.x.x.x.x.x.x.x.', 'x..x..x.x..x..x.']}
- **Lead rhythm** `x-------x-------` / `x---x---x-------` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `nostalgic_simple` · bass `rolling_groove` · drop `long_build` · variation `low` · culture `nostalgic_memory` · texture `tape_degraded` · rhythm `swung_16ths` · harmony `static_vamp` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -18 dB · rev=0.3
  - chat (top): `chat` -30 dB
  - shaker (top): `shaker` -31 dB · pan=0.3
  - bass (bass): `moogbass` -14 dB · alternatives ['sinebass', 'sf:fingerbass', 'fmbass']
  - chords (chords): `acguitar` -21 dB · pan=-0.2 · rev=0.4 · alternatives ['guitar', 'sf:nylon', 'sf:steelguitar']
  - pad (pad): `warmpad` -27 dB · rev=0.55 · alternatives ['solina', 'strings', 'glasspad']
  - arp (arp): `acguitar` -23 dB · pan=0.25 · rev=0.4 · alternatives ['guitar', 'harp', 'mutedgtr']
  - lead (lead): `polysynth` -21 dB · rev=0.45 · dly=0.3 · alternatives ['softlead', 'acguitar', 'synthbrass']
  - texture (fx): `texture` -40 dB
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -13.0, 'air': -2.0, 'low': 1.4, 'lofi': True, 'wobble': 4.0} · reverb 2.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.02, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True, 'repetition': 0.9}
- **Sound brief** Acoustic guitar loops (fingerpicked + strummed); warm loose drums; round bass; reversed swells; soft synth

### Hauntology - cold dystopian synths (`hauntology_cold`)

Hauntology - cold dystopian synths: slow, heavy and minor - a stark kick and snare with lots of space, cold analog arpeggios, a dark drone bass, eerie detuned pads and a lonely melody, like a 70s public-information film played back decades later

- **Tempo** 64-76 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.52 (unit 16) · humanise 0.005
- **Progressions** {'minor': [[0, 0, 5, 6], [0, 6, 5, 6], [0, 3, 0, 6]], 'phrygian': [[0, 1, 0, 0]], 'harmonic_minor': [[0, 4, 0, 5]]} · chord_bars 2 · chord size 3
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X.......X.......` / `X..........X....`; **snare** `....X.......X...`; **chat** `x...x...x...x...` / `..x...x...x...x.`
- **Drum kit** vintage · preset `soft`
- **Bass** `R---------------` / `R-------R-------` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 4, 'prob': 0.9}
- **Lead rhythm** `x-------........` / `x---x-------....` / `........x-------` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `drifting` · melody `nostalgic_simple` · bass `sub_only` · drop `long_build` · variation `low` · culture `nostalgic_memory` · texture `tape_degraded` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -17 dB · rev=0.45
  - chat (top): `chat` -31 dB
  - bass (bass): `sinebass` -14 dB · alternatives ['moogbass', '808', 'reese']
  - chords (chords): `polysynth` -24 dB · rev=0.5 · alternatives ['solina', 'warmpad', 'synthbrass']
  - pad (pad): `choir` -27 dB · rev=0.6 · alternatives ['warmpad', 'solina', 'strings']
  - arp (arp): `polysynth` -25 dB · pan=0.25 · rev=0.4 · dly=0.35 · alternatives ['pluck_saw', 'bell', 'pluck']
  - lead (lead): `softlead` -20 dB · rev=0.5 · dly=0.35 · alternatives ['polysynth', 'flute']
  - texture (fx): `texture` -36 dB
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -13.0, 'air': -1.5, 'low': 1.4, 'lofi': True, 'wobble': 3.5} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True, 'repetition': 0.9}
- **Sound brief** Stark slow kit; cold analog arpeggio; drone bass; detuned eerie pads; a lonely synth / flute melody

# Classic

## Rock & Metal

### Rock (`rock`)

Rock: driving drums, distorted power-chord guitars, solid bass, lead guitar

- **Tempo** 110-140 BPM · **scales** minor, mixolydian, major · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 5, 6, 0], [0, 3, 5, 6]], 'mixolydian': [[0, 6, 3, 0]], 'major': [[0, 4, 5, 3], [0, 3, 4, 3]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.....X.X.......` / `X.......X.X.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** rusty · preset `acoustic`
- **Bass** `R.R.R.R.R.R.R.R.` / `R-R-R-R-R-R-A-R-` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x-x-x-x-x-x-x-x-` / `x--x--x-x--x--x-`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 4}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `x.x.x.x.x---x---` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - ride (top): `ride` -32 dB · pan=-0.3
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'sf:pickbass', 'moogbass']
  - chords (chords): `guitar`  dB · alternatives ['sf:odguitar', 'sf:distguitar', 'mutedgtr']
  - pad (pad): `organ` -28 dB · rev=0.3 · alternatives ['strings', 'warmpad', 'solina']
  - arp (arp): `guitar` -27 dB · pan=0.4 · alternatives ['piano', 'sf:cleanguitar', 'mutedgtr']
  - lead (lead): `guitar`  dB · rev=0.35 · dly=0.25 · alternatives ['sf:odguitar', 'organ', 'sf:distguitar']
- **Mix** {'lufs': -9.5, 'air': 1.5, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.85, 'chord_center': 52, 'strum': 0.0, 'voicing': 'power', 'lead_oct': 4, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Metal (`metal`)

Metal: palm-muted power chords, double-kick drums, shredding lead guitar

- **Tempo** 140-180 BPM · **scales** phrygian, minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.003
- **Progressions** [[0, 0, 1, 0], [0, 5, 6, 0], [0, 6, 5, 4]] · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `XxXxXxXxXxXxXxXx` / `X.X.X.X.X.X.X.X.` / `XxXxXxXxX.X.XxXx` / `X.xxX.xxX.xxX.xx`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x...x...x...x...`
- **Drum kit** rock · preset `acoustic`
- **Bass** `RRRRRRRRRRRRRRRR` / `R.R.R.R.R.R.R.R.` · mode `pattern` · lowest note 26
- **Chord rhythm** `xxxxxxxxxxxxxxxx` / `x.xxx.xxx.xxx.xx` / `x-x-xxx-x-x-xxx-`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 4}
- **Lead rhythm** `xxxxx.x.x-x-x---` / `x-x-x-x-xxxx----` / `x.x.x.x.x-------` / `x-------x-------`
- **Riffs** `pp.pp.ppX-pp.pp.` / `p.ppp.ppb-p.ppm-` / `p.ppp.ppp.ppp.pp` / `X---pppppppppppp` / `pp.f-pp.m-pp.b--` / `ppppX-ppppm-ppb-` / `X-.pp.ppX-.pp.pp`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `virtuosic` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -15 dB · rev=0.2
  - chat (top): `chat` -28 dB
  - ride (top): `ride` -30 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `guitar` -16 dB · alternatives ['sf:distguitar', 'sf:odguitar', 'mutedgtr']
  - arp (arp): `guitar` -26 dB · pan=0.4 · alternatives ['sf:distguitar', 'spiccato', 'mutedgtr']
  - lead (lead): `guitar`  dB · rev=0.3 · dly=0.2 · alternatives ['sf:distguitar', 'sf:odguitar', 'organ']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {'kick': {'pitch': 60, 'punch': 200, 'sweep': 60, 'decay': 14, 'drive': 2.0, 'len': 0.25, 'click': 0.9}}, 'snare_tracks': ['snare'], 'bass_gate': 0.8, 'chord_center': 48, 'strum': 0.0, 'voicing': 'power', 'lead_oct': 4, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'riff_lo': 38, 'riff_chorus': 0.35}

### Symphonic Metal (`symphonic_metal`)

Symphonic metal: double-kick drums and power chords under choir, string ostinatos and a soaring lead

- **Tempo** 120-170 BPM · **scales** harmonic_minor, minor, phrygian · swing 0.5 (unit 16) · humanise 0.003
- **Progressions** {'harmonic_minor': [[0, 5, 3, 4], [0, 3, 4, 0], [0, 5, 0, 4]], 'minor': [[0, 5, 2, 6], [0, 6, 5, 4], [0, 3, 6, 5]], 'phrygian': [[0, 1, 0, 6], [0, 0, 1, 0]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `XxXxXxXxXxXxXxXx` / `X.X.X.X.X.X.X.X.` / `XxXxXxXxX.X.XxXx` / `X.xxX.xxX.xxX.xx`; **snare** `....X.......X...` / `........X.......`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x...x...x...x...`
- **Drum kit** rock · preset `acoustic`
- **Bass** `RRRRRRRRRRRRRRRR` / `R.R.R.R.R.R.R.R.` · mode `pattern` · lowest note 26
- **Chord rhythm** `x.xxx.xxx.xxx.xx` / `xxxxxxxxxxxxxxxx` / `x-x-x-x-x-x-x-x-`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x---x---` / `x-------x---x---` / `x-.x-.x-x-------`
- **Riffs** `pp.pp.ppX-pp.pp.` / `p.ppp.ppb-p.ppm-` / `p.ppp.ppp.ppp.pp` / `X---pppppppppppp` / `pp.f-pp.m-pp.b--` / `ppppX-ppppm-ppb-` / `X-.pp.ppX-.pp.pp`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `virtuosic` · bass `rolling_groove` · drop `long_build` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -15 dB · rev=0.25
  - chat (top): `chat` -28 dB
  - ride (top): `ride` -30 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `guitar` -16 dB · alternatives ['sf:distguitar', 'sf:odguitar', 'mutedgtr']
  - pad (pad): `choir` -22 dB · rev=0.5 · alternatives ['strings', 'organ', 'horn', 'tremolo']
  - arp (arp): `spiccato` -25 dB · pan=0.3 · rev=0.3 · alternatives ['harp', 'piano', 'pizz']
  - lead (lead): `violin` -17 dB · rev=0.4 · dly=0.2 · alternatives ['guitar', 'sf:distguitar', 'choir', 'horn', 'flute']
- **Mix** {'lufs': -9.5, 'air': 1.5, 'low': 1.0} · reverb 2.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.8, 'chord_center': 48, 'strum': 0.0, 'voicing': 'power', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'riff_lo': 38, 'riff_chorus': 0.35}
- **Sound brief** Distorted guitars; Choir (pad); Strings spiccato (ostinato); Violin / guitar / horn lead; Organ

### Punk (`punk`)

Punk rock: fast down-picked power chords, driving 8th-note bass, pounding drums, shouty guitar hooks

- **Tempo** 160-200 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'major': [[0, 3, 4, 0], [0, 4, 5, 3], [0, 3, 0, 4]], 'minor': [[0, 5, 6, 0], [0, 6, 5, 6]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...` / `X.X...X.X.X...X.`; **snare** `....X.......X...` / `..X...X...X...X.`; **chat** `x.x.x.x.x.x.x.x.`; **crash** `X...............`
- **Drum kit** rusty · preset `hard`
- **Bass** `R.R.R.R.R.R.R.R.` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x-x-x-x-x-x-x-x-`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x-x-x---x---` / `x---x---x-x-x---` / `x-x-x---x-x-x---`
- **Riffs** `p.p.p.p.p.p.p.p.` / `x.x.x.x.x.x.x.x.` / `p.p.p.p.X-x.x.x.` / `X.x.x.x.q.q.q.q.`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `sparse` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -15 dB · rev=0.2
  - chat (top): `chat` -27 dB
  - crash (top): `crash` -28 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `guitar`  dB · pan=-0.2 · alternatives ['sf:distguitar', 'sf:odguitar', 'mutedgtr']
  - lead (lead): `guitar` -18 dB · pan=0.2 · rev=0.2 · alternatives ['sf:odguitar', 'sf:distguitar', 'organ']
- **Mix** {'lufs': -9.0, 'air': 1.5, 'low': 0.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.85, 'chord_center': 50, 'strum': 0.0, 'voicing': 'power', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'riff_lo': 40, 'riff_chorus': 0.0}
- **Sound brief** Distorted guitars (down-picked); Bass guitar (8ths); Drums

### Indie Rock (`indie_rock`)

Indie rock: jangly clean guitars in 8ths, melodic bass, straight-ahead drums, a hooky guitar lead

- **Tempo** 108-140 BPM · **scales** major, minor, mixolydian · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 4, 5, 3], [3, 0, 4, 5], [0, 3, 5, 4], [5, 3, 0, 4]], 'minor': [[0, 5, 2, 6], [0, 3, 5, 6]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X...X...X..X....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** rusty · preset `punchy`
- **Bass** `R.R.R.R.R.R.R.R.` / `R...R.R.R...A...` / `R.......R.R.A...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x.xx.xx.x.xx.xx.` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.8}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `..x-x-x-x---x---` / `x-x-x-x-x---....`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.3
  - chat (top): `chat` -28 dB
  - ride (top): `ride` -32 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `guitar`  dB · pan=-0.25 · rev=0.25 · dly=0.15 · alternatives ['sf:cleanguitar', 'sf:odguitar', 'piano', 'wurli']
  - pad (pad): `organ` -29 dB · rev=0.35 · alternatives ['warmpad', 'strings', 'solina', 'polysynth']
  - arp (arp): `guitar` -24 dB · pan=0.3 · rev=0.3 · dly=0.25 · alternatives ['sf:cleanguitar', 'piano', 'mutedgtr']
  - lead (lead): `guitar` -18 dB · rev=0.3 · dly=0.2 · alternatives ['sf:odguitar', 'sf:cleanguitar', 'leadsaw', 'piano']
- **Mix** {'lufs': -10.0, 'air': 1.6, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Clean / chorus guitars (jangle); Arpeggiated lead guitar; Bass guitar; Drums; Synth or organ pad

### Jam Band (`jam_band`)

Jam band / psychedelic Americana: noodling clean lead guitar, melodic wandering bass, organ, loose two-drummer groove, long improvised sections

- **Tempo** 100-132 BPM · **scales** mixolydian, major, dorian · swing 0.54 (unit 16) · humanise 0.012
- **Progressions** {'mixolydian': [[0, 6, 3, 0], [0, 3, 0, 6], [0, 6, 0, 3]], 'major': [[0, 4, 3, 0], [0, 3, 4, 3], [0, 5, 3, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `jazz`: intro 4 [bass, chords, top] -> head 16 [bass, chords, kick, lead, snare, top] -> solo 16 [bass, chords, kick, lead, snare, top] (alt) -> solo 16 [arp, bass, chords, kick, snare, top] -> head 16 [bass, chords, kick, lead, snare, top] -> outro 4 [bass, chords, top] (fade) · form_scale 1.5
- **Drums** **kick** `X.......X.x.....` / `X...X.....X.X...`; **snare** `....X.......X...`; **ride** `x.x.x.x.x.x.x.x.`; **chat** `x.x.x.x.x.x.x.x.`; **tom** `.............x.x` / `................`
- **Drum kit** rusty · preset `acoustic`
- **Bass** `R.R.F.A.R..RF.A.` / `R...F.R.A..RF...` / `R.FA.R..F.A.R.F.` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x---x---x---x---` / `..x...x...x...x.`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x.x.x.x.x-x-x---` / `x.xx.x.xx.x.x...` / `x-x-x.x.x.x-x---` / `..x.x-x.x.x.x.x.`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `modal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - snare (snare): `snare` -18 dB · rev=0.3
  - ride (top): `ride` -26 dB · pan=0.25
  - chat (top): `chat` -29 dB · pan=-0.25
  - tom (top): `tom` -24 dB · rev=0.3
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'upright', 'sf:pickbass']
  - chords (chords): `guitar` -22 dB · pan=-0.25 · rev=0.3 · alternatives ['sf:cleanguitar', 'piano', 'organ']
  - pad (pad): `organ` -26 dB · pan=0.25 · rev=0.3 · alternatives ['wurli', 'pedalsteel', 'strings']
  - arp (arp): `piano` -27 dB · rev=0.3 · alternatives ['guitar', 'wurli', 'epiano']
  - lead (lead): `guitar` -18 dB · rev=0.35 · dly=0.2 · alternatives ['sf:cleanguitar', 'organ', 'pedalsteel', 'harmonica', 'piano']
- **Mix** {'lufs': -12.0, 'air': 1.2, 'low': 0.9} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Clean electric guitars (lead + rhythm); Bass guitar (melodic); Hammond organ; Piano; two drummers

### 70s Soft Rock (`soft_rock`)

70s soft rock (California): steady groove, round melodic bass, strummed acoustic and clean electric guitars, Rhodes and organ, a smooth vocal-style lead

- **Tempo** 100-126 BPM · **scales** major, dorian, mixolydian, minor · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 4, 5, 3], [3, 0, 4, 0], [0, 3, 0, 4], [5, 3, 0, 4]], 'dorian': [[0, 6, 0, 6], [0, 3, 0, 3]], 'mixolydian': [[0, 6, 3, 0]], 'minor': [[0, 6, 5, 6], [5, 6, 0, 0]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X.....X.X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `xxxxxxxxxxxxxxxx`; **tom** `............x.x.` / `................`; **tamb** `....x.......x...`
- **Drum kit** dead70s · preset `soft`
- **Bass** `R.....R.R...F...` / `R...R...F...A...` / `R.......R.R.F...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x---x---x---x---` / `x..x..x.x.x.x...`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x-x-x---x-x-....` / `x---x-x-x---....` / `..x-x-x-x---x...` / `x-x-x-x-x-------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -16 dB
  - snare (snare): `snare` -18 dB · rev=0.35
  - chat (top): `chat` -28 dB
  - tom (top): `tom` -23 dB · rev=0.35
  - tamb (top): `tamb` -30 dB · pan=0.3
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'moogbass', 'sf:pickbass']
  - chords (chords): `acguitar`  dB · pan=-0.25 · rev=0.25 · alternatives ['guitar', 'sf:steelguitar', 'sf:cleanguitar', 'epiano', 'piano', 'wurli']
  - pad (pad): `organ` -27 dB · pan=0.25 · rev=0.3 · alternatives ['strings', 'solina', 'polysynth', 'pedalsteel']
  - arp (arp): `epiano` -25 dB · pan=0.2 · rev=0.3 · alternatives ['guitar', 'piano', 'pluck']
  - lead (lead): `guitar` -18 dB · rev=0.35 · dly=0.2 · alternatives ['sf:cleanguitar', 'epiano', 'pedalsteel', 'flute', 'sax']
- **Mix** {'lufs': -11.0, 'air': 1.3, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.01, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Acoustic + clean electric guitars; Fender Rhodes; Hammond organ; Bass guitar (melodic); soft drums with tom fills

### 90s alt rock (`alt_rock_90s`)

90s alternative rock: jangly clean arpeggios in the verses, crunchy distorted power chords that explode in the choruses, an eighth-note pick bass, a big dry room kit - catchy, major-key and a little melancholy, mastered with 90s dynamics

- **Tempo** 104-132 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 0, 4], [5, 3, 0, 4], [0, 6, 3, 0]], 'mixolydian': [[0, 6, 3, 0], [0, 3, 6, 3]]} · chord_bars 1 · chord size 3
- **Song form** `alt90`: intro 4 [arp, bass, kick, snare, top] -> verse 16 [arp, bass, kick, lead, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, kick, lead, snare, top] (crash) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, bass, pad, top] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 4 [bass, chords, kick, snare, top] (cad) · form_scale 1
- **Drums** **kick** `X.....X.X.......` / `X.......X.X.....` / `X.....X...X..X..`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.xxx.xxx.xx`; **ride** `x.x.x.x.x.x.x.x.`; **crash** `X...............` / `................`; **tamb** `....x.......x...`
- **Drum kit** rock · preset `acoustic`
- **Bass** `R.R.R.R.R.R.R.R.` / `R.R.R.R.R.R.F.F.` / `R...R.R.R...R.R.` · mode `pattern` · lowest note 33
- **Chord rhythm** `x-x-x-x-x-x-x-x-` / `X---x-x-X---x-x-` / `x.x.x.x.x.x.x.x.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4}
- **Lead rhythm** `x-x-x---x-x-----` / `x---x-x-x-x-x---` / `..x-x-x-x-------` / `x-x-x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `live_drums` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -14 dB · rev=0.25
  - chat (top): `chat` -27 dB · pan=0.2
  - ride (top): `ride` -30 dB · pan=-0.3
  - crash (top): `crash` -25 dB · rev=0.3
  - tamb (top): `tamb` -30 dB · pan=0.35
  - bass (bass): `ebass` -14 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `guitar` -17 dB · pan=-0.35 · alternatives ['sf:distguitar', 'sf:odguitar', 'mutedgtr']
  - chords_r (chords): `guitar` -18 dB · pan=0.35
  - arp (arp): `guitar` -21 dB · pan=0.3 · rev=0.3 · alternatives ['sf:cleanguitar', 'acguitar', 'mutedgtr']
  - pad (pad): `organ` -28 dB · rev=0.3 · alternatives ['strings', 'warmpad', 'solina']
  - lead (lead): `guitar` -19 dB · rev=0.35 · dly=0.2 · alternatives ['organ', 'piano', 'sf:distguitar']
- **Mix** {'lufs': -12.0, 'air': 1.2, 'low': 1.0} · reverb 1.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.85, 'chord_center': 55, 'strum': 0.0, 'voicing': 'power', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'no_rotation': True}
- **Sound brief** Clean jangly guitar (Rickenbacker-ish, chorus); distorted power chords in the chorus; pick bass; big room kit; a little organ or lead guitar

### Jam-band rock (80s, upbeat) (`jam_rock_80s`)

Jam-band rock (80s, upbeat sing-along): a bright, bouncing major-key groove from two drummers, chiming chorused rhythm guitar, a melodic bass that never sits still, 80s digital keys and organ, and a clean lead guitar that noodles around the tune - then stretches out in long solo jams

- **Tempo** 108-126 BPM · **scales** major, mixolydian · swing 0.52 (unit 16) · humanise 0.009
- **Progressions** {'major': [[0, 4, 0, 4], [0, 3, 4, 0], [5, 4, 3, 0], [0, 4, 5, 3]], 'mixolydian': [[0, 6, 3, 0], [0, 6, 0, 6]]} · chord_bars 1 · chord size 3
- **Song form** `jam80`: intro 4 [bass, chords, kick, lead, snare, top] -> verse 16 [bass, chords, kick, pad, snare, top] -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [bass, chords, kick, pad, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> solo 16 [bass, chords, kick, lead, pad, snare, top] (alt) -> solo 16 [arp, bass, chords, kick, lead, pad, snare, top] -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [bass, chords, kick, lead, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....` / `X.....X.X.X.....`; **snare** `....X.......X...`; **chat** `x.xxx.xxx.xxx.xx`; **kick2** `X.......X.....x.` / `X.........X.....`; **snare2** `....x.......x..o`; **ride** `x.x.x.x.x.x.x.x.`; **tom** `................` / `............x.x.`; **tamb** `..x...x...x...x.`
- **Drum kit** big80s · preset `acoustic`
- **Bass** `R...O.R.F...R.A.` / `R.R...F.R...O.R.` / `R...R.F...R.F.A.` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x...x...x...x.` / `x.x..x.x.x.x..x.` / `..x.x...x.x...x.`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x.x.x-x.x.x-x---` / `x-x.x.x-x.x.x.x.` / `xx.x.x.xx.x.x---` / `x.x-x.x-x.x.x.x-`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `live_drums` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB · pan=-0.25
  - snare (snare): `snare` -16 dB · pan=-0.25 · rev=0.3
  - chat (top): `chat` -28 dB · pan=-0.3
  - kick2 (kick role - the genre's low drum): `kick` -17 dB · pan=0.25
  - snare2 (snare): `snare` -20 dB · pan=0.25 · rev=0.3
  - ride (top): `ride` -30 dB · pan=0.35
  - tom (top): `tom` -22 dB · pan=0.2 · rev=0.3
  - tamb (top): `tamb` -30 dB · pan=0.4
  - bass (bass): `ebass` -14 dB · alternatives ['sf:fingerbass', 'sf:pickbass', 'moogbass']
  - chords (chords): `guitar` -21 dB · pan=-0.35 · rev=0.25 · alternatives ['sf:cleanguitar', 'acguitar', 'sf:distguitar']
  - pad (pad): `epiano` -25 dB · rev=0.3 · alternatives ['organ', 'polysynth', 'warmpad']
  - arp (arp): `organ` -27 dB · pan=0.3 · rev=0.3 · alternatives ['piano', 'epiano', 'twang']
  - lead (lead): `guitar` -19 dB · pan=0.2 · rev=0.35 · dly=0.2 · alternatives ['sf:cleanguitar', 'organ', 'sf:distguitar']
  - solo_keys (lead): `epiano` -19 dB · pan=-0.1 · rev=0.3
- **Mix** {'lufs': -12.0, 'air': 1.4, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.75, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'solos': ['lead', 'solo_keys', 'lead'], 'no_rotation': True}
- **Sound brief** Two drum kits panned left / right; chorused clean rhythm guitar; melodic bass; DX7-style keys and organ; clean lead guitar noodling

### Lo-fi bedroom rock (`lofi_rock`)

Lo-fi bedroom rock: a raw, mono, home-recorded rock song - a fuzzy overdriven rhythm guitar playing a simple chord riff, a plain driving bass, a dry boxy kit, a wobbly lead guitar line, all a bit too loud for the tape; short, direct, sincere

- **Tempo** 100-116 BPM · **scales** major, mixolydian, minor · swing 0.52 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 0, 4], [5, 3, 0, 4]], 'mixolydian': [[0, 6, 3, 0]], 'minor': [[0, 6, 3, 4], [0, 3, 6, 5]]} · chord_bars 1 · chord size 3
- **Song form** `lofi_rock`: intro 4 [chords, kick, top] -> verse 8 [bass, chords, kick, snare, top] -> chorus 8 [bass, chords, kick, lead, snare, top] (crash) -> verse 8 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, snare, top] (crash) -> outro 8 [bass, chords, kick, lead, snare, top] · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X.....X.X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **crash** `................`
- **Drum kit** rusty · preset `acoustic`
- **Bass** `R.R.R.R.R.R.R.R.` / `R...R...R.R.R...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x-x-x-x-x-x-x-x-` / `x---x---x-x-x---`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x---x---`
- **Build-ups** default `(category default)` · choices ['pickup', 'none'] · transitions ['crash', 'none', 'none']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `tape_degraded` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -15 dB · rev=0.12
  - chat (top): `chat` -27 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `guitar` -15 dB · alternatives ['sf:distguitar', 'sf:odguitar', 'mutedgtr']
  - lead (lead): `guitar` -19 dB · rev=0.2 · alternatives ['sf:distguitar', 'sf:odguitar', 'organ']
- **Mix** {'lufs': -10.0, 'air': -2.0, 'low': 1.0, 'width': 0.3, 'lofi': True, 'wobble': 1.2} · reverb 1.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 55, 'strum': 0.0, 'voicing': 'power', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Overdriven / fuzzy rhythm guitar, plain bass on 8ths, dry boxy drums, a wobbly lead guitar, mono, tape saturation

### 80s boogie rock (`boogie_rock`)

Mid-80s boogie rock: a fast, bouncing two-beat shuffle around 170 driven by a cheerful combo-organ riff, clean chorused electric guitar licks, a pumping root-fifth bass and a big, roomy kit with a backbeat snare - feel-good and radio-bright

- **Tempo** 164-176 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 0, 4, 3], [0, 3, 4, 3], [0, 4, 3, 4]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `boogie_rock`: intro 8 [chords] -> intro 8 [bass, chords, kick, snare, top] -> verse 24 [arp, bass, chords, kick, snare, top] -> chorus 12 [bass, chords, kick, lead, snare, top] (crash) -> verse 24 [arp, bass, chords, kick, snare, top] -> chorus 8 [bass, chords, kick, lead, snare, top] (crash) -> solo 32 [bass, chords, kick, lead, snare, top] (alt) -> chorus 8 [bass, chords, kick, lead, snare, top] (crash) -> outro 24 [arp, bass, chords, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X.....X.X.......` / `X.......X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `x.x.x.x.x.x.x.x.`
- **Drum kit** rock · preset `acoustic`
- **Bass** `R...F...R...F...` / `R.R.F.F.R.R.F.F.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.xxx.x.x.xxx.x.` / `x.x.xxx.x.x.xxx.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x-x-x-x-x---x---` / `x---x-x-x-x-x---`
- **Build-ups** default `(category default)` · choices ['pickup', 'lift', 'stops'] · transitions ['crash', 'none', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -14 dB · rev=0.3
  - chat (top): `chat` -27 dB
  - tamb (top): `tamb` -31 dB · pan=0.3
  - bass (bass): `ebass` -14 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `organ` -17 dB · rev=0.25 · alternatives ['polysynth', 'epiano', 'piano']
  - arp (arp): `guitar` -23 dB · pan=-0.3 · rev=0.3 · alternatives ['mutedgtr', 'piano', 'sf:cleanguitar']
  - lead (lead): `guitar` -19 dB · rev=0.3 · dly=0.2 · alternatives ['organ', 'synthbrass', 'sf:distguitar']
- **Mix** {'lufs': -11.0, 'air': 1.4, 'low': 0.8, 'width': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Combo organ / synth-organ riff (the hook); clean chorused Strat licks; root-fifth bass; big roomy kit

### Spooky 60s surf / TV theme (`spooky_surf`)

Spooky 60s surf / TV-theme rock: a fast, driving beat around 150 with a twangy, heavily reverbed electric guitar melody, a walking / chromatic bass line, stabbing brass and a cheesy combo organ - campy, creepy and fun

- **Tempo** 144-160 BPM · **scales** minor, harmonic_minor, phrygian_dominant · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'minor': [[0, 0, 5, 4], [0, 3, 0, 4]], 'harmonic_minor': [[0, 5, 1, 4]], 'phrygian_dominant': [[0, 1, 0, 1]]} · chord_bars 1 · chord size 3
- **Song form** `spooky_surf`: intro 4 [bass, kick, snare, top] -> A 16 [bass, chords, kick, lead, snare, top] -> B 16 [arp, bass, chords, kick, lead, snare, top] (alt) -> A 16 [bass, chords, kick, lead, snare, top] (crash) -> B 16 [arp, bass, chords, kick, lead, snare, top] (alt) -> outro 8 [bass, chords, kick, lead, snare, top] · form_scale 1
- **Drums** **kick** `X.......X.......` / `X.....X.X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x.xxx.xxx.xxx.xx`
- **Drum kit** vintage · preset `acoustic`
- **Bass** `R.F.R.F.O.F.R.A.` / `R...F...R...A...` · mode `walk` · lowest note 31
- **Chord rhythm** `x...x...x...x...` / `x.x.....x.x.....`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x-x-x-x-x---x---` / `x---x-x-x-x-x---` / `x-x-x---x-x-x---`
- **Build-ups** default `(category default)` · choices ['pickup', 'stops'] · transitions ['crash', 'none', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `walking` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -15 dB · rev=0.3
  - chat (top): `chat` -27 dB
  - ride (top): `ride` -30 dB
  - bass (bass): `ebass` -14 dB · alternatives ['upright', 'sf:fingerbass', 'sf:pickbass']
  - chords (chords): `brass` -20 dB · rev=0.3 · alternatives ['organ', 'synthbrass', 'sf:trumpetsection']
  - arp (arp): `organ` -24 dB · pan=0.3 · rev=0.25 · alternatives ['twang', 'guitar', 'piano']
  - lead (lead): `twang` -17 dB · rev=0.45 · dly=0.15 · alternatives ['guitar', 'organ', 'sf:cleanguitar']
- **Mix** {'lufs': -11.0, 'air': 1.2, 'low': 0.6, 'width': 1.1} · reverb 2.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'no_fx_sounds': True, 'spring': True}
- **Sound brief** Twangy reverb-drenched guitar melody (low strings); walking bass; brass stabs; combo organ; fast straight beat

### Nu-metal (`nu_metal`)

Nu-metal / alt-metal (late 90s - early 2000s): down-tuned, chugging power-chord riffs with lots of rests and syncopation around 95-105, a slapping, clanky bass, a groovy half-hip-hop beat with hard snares, scratchy turntable-ish noises and eerie clean guitar lines in the gaps

- **Tempo** 94-106 BPM · **scales** phrygian, minor · swing 0.52 (unit 16) · humanise 0.004
- **Progressions** {'phrygian': [[0, 0, 1, 0], [0, 1, 0, 6]], 'minor': [[0, 0, 6, 5], [0, 0, 3, 1]]} · chord_bars 1 · chord size 2
- **Song form** `nu_metal`: intro 4 [bass, chords, kick] -> verse 12 [arp, bass, chords, kick, snare, top] -> chorus 8 [bass, chords, kick, lead, snare, top] (crash) -> verse 12 [arp, bass, chords, kick, snare, top] -> chorus 8 [bass, chords, kick, lead, snare, top] (crash) -> outro 8 [bass, chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X..X......X.X...` / `X.XX......X.....` / `X..X..X...X..X..`; **snare** `....X.......X...` / `....X.......X..x`; **chat** `x.x.x.x.x.x.x.x.`; **crash** `X...............`
- **Drum kit** rock · preset `acoustic`
- **Bass** `RRR.R.....R.R...` / `R.RR......R.RR..` · mode `pattern` · lowest note 26
- **Chord rhythm** `xxx.x.....x.x...` / `x.xx......x.xx..` / `xx.xx.xx..x.....`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x---x-------` / `x-x-x---x---x---`
- **Riffs** `ppp.p.....X-p...` / `p.pp......X-pp..` / `pp.pp.pp..X-....`
- **Build-ups** default `(category default)` · choices ['stops', 'pickup'] · transitions ['crash', 'gap', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `virtuosic` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `straight_16ths` · harmony `modal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -13 dB · rev=0.15
  - chat (top): `chat` -27 dB
  - crash (top): `crash` -28 dB
  - bass (bass): `ebass` -14 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `guitar` -14 dB · alternatives ['sf:distguitar', 'sf:odguitar', 'mutedgtr']
  - arp (arp): `guitar` -24 dB · pan=0.4 · rev=0.3 · dly=0.2 · alternatives ['sf:distguitar', 'mutedgtr', 'piano']
  - lead (lead): `guitar` -18 dB · rev=0.3 · dly=0.2 · alternatives ['sf:distguitar', 'sf:odguitar', 'organ']
- **Mix** {'lufs': -8.5, 'air': 1.2, 'low': 1.4, 'width': 1.0} · reverb 1.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 46, 'strum': 0.0, 'voicing': 'power', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'riff_lo': 33, 'riff_chorus': 0.6}
- **Sound brief** Down-tuned 7-string chug riffs with rests; clanky slap bass; hip-hop-ish hard drums; eerie clean guitar; scratch noises

### Surf rock (60s) (`surf_rock`)

Surf rock (early-60s instrumental surf): a fast, straight beat driven by the floor tom, a twangy guitar melody tremolo-picked in bursts on the low strings and drowned in spring reverb, a strummed rhythm guitar, a root-fifth bass and now and then a combo organ or sax - sunny, wet and full speed ahead

- **Tempo** 132-156 BPM · **scales** major, mixolydian, minor, phrygian_dominant · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 3, 4, 3], [0, 5, 3, 4], [0, 0, 3, 3], [0, 3, 0, 4]], 'mixolydian': [[0, 6, 3, 0], [0, 6, 0, 6]], 'minor': [[0, 5, 6, 0], [0, 6, 5, 4]], 'phrygian_dominant': [[0, 1, 0, 1], [0, 1, 6, 0]]} · chord_bars 1 · chord size 3
- **Song form** `surf_rock`: intro 4 [kick, lead, snare, top] -> A 16 [bass, chords, kick, lead, snare, top] (crash) -> B 16 [arp, bass, chords, kick, lead, snare, top] (alt) -> break 4 [kick, snare, top] -> solo 16 [arp, bass, chords, kick, lead, snare, top] (alt) -> A 16 [bass, chords, kick, lead, snare, top] (crash) -> outro 4 [bass, chords, kick, lead, snare, top] · form_scale 1
- **Drums** **kick** `X.......X.......` / `X.....X.X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tom** `x...x...x...x...` / `x...x...x.x.x...`
- **Drum kit** vintage · preset `acoustic`
- **Bass** `R...F...R...F...` / `R...F...O...F...` / `R.R.F...R.R.F...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x...x...x...x...` / `x..x..x.x.......` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-x-x-x-x---x---` / `x.x.x.x.x.x.x---` / `x---x-x-x-x-x---` / `x-x-x-x-xxxx----`
- **Build-ups** default `(category default)` · choices ['pickup', 'stops'] · transitions ['crash', 'none', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.35
  - chat (top): `chat` -26 dB
  - tom (top): `tom` -18 dB · pan=-0.2 · rev=0.3
  - bass (bass): `ebass` -12 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'upright']
  - chords (chords): `guitar` -23 dB · pan=0.25 · rev=0.35 · alternatives ['acguitar', 'twang', 'organ']
  - arp (arp): `organ` -24 dB · pan=-0.3 · rev=0.3 · alternatives ['guitar', 'twang', 'sax']
  - lead (lead): `twang` -18 dB · rev=0.55 · dly=0.12 · alternatives ['guitar', 'sax', 'sf:cleanguitar']
- **Mix** {'lufs': -11.0, 'air': 1.2, 'low': 2.0, 'width': 1.1} · reverb 2.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.012, 'voicing': 'close', 'lead_oct': 4, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'no_fx_sounds': True, 'spring': True, 'repetition': 0.75}
- **Sound brief** Twangy single-coil guitar (tremolo-picked, low strings) in a spring reverb tank; strummed rhythm guitar; electric bass; floor-tom surf beat; combo organ or tenor sax for a chorus

### Spooky surf - monster TV theme (`monster_theme`)

Spooky surf - 60s monster-sitcom theme: a driving 150 BPM surf beat under a low, creeping chromatic riff (root, a half step up, back, a half step down) played by the bass and a twangy baritone guitar together, punchy brass stabs, a bright brass-melody bridge in the relative major, a honking sax-section stretch, and a big chromatic stab ending - campy, creepy and catchy

- **Tempo** 146-158 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.007
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 4], [2, 6, 5, 2]]} · chord_bars 1 · chord size 3
- **Song form** `monster_theme`: intro 4 [bass, kick, snare, top] -> A 16 [bass, chords, kick, snare, top] (crash) -> bridge 8 [bass, chords, kick, lead, snare, top] (alt, crash) -> horns 12 [arp, bass, chords, kick, snare, top] -> bridge 8 [bass, chords, kick, lead, snare, top] (alt, crash) -> A 16 [bass, chords, kick, snare, top] (crash) -> A 8 [bass, chords, kick, lead, snare, top] -> outro 4 [bass, chords, kick, lead, snare, top] · form_scale 1
- **Drums** **kick** `X.......X.......` / `X.....X.X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** vintage · preset `acoustic`
- **Bass** `R.R.u.R.d.R.R...` / `R.u.R.d.R.R.u.R.` / `R.R.R.u.R.d.R...` · mode `pattern` · lowest note 28
- **Chord rhythm** `..x...x...x...x.` / `x.......x.x.....` / `....x.......x.x.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4, 'prob': 0.7}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `x-x-x-x-x---x---`
- **Build-ups** default `(category default)` · choices ['pickup', 'stops'] · transitions ['crash', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `minimal_motivic` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -15 dB · rev=0.3
  - chat (top): `chat` -27 dB
  - ride (top): `ride` -28 dB
  - bass (bass): `ebass` -11 dB · alternatives ['sf:pickbass', 'sf:fingerbass', 'upright']
  - riff (bass): `twang` -13 dB · rev=0.45
  - chords (chords): `brass` -23 dB · pan=0.25 · rev=0.3 · alternatives ['synthbrass', 'organ', 'sf:trumpetsection']
  - arp (arp): `sax` -22 dB · pan=-0.25 · rev=0.3 · alternatives ['brass', 'organ']
  - lead (lead): `brass` -17 dB · rev=0.35 · dly=0.1 · alternatives ['sax', 'twang', 'organ']
- **Mix** {'lufs': -11.0, 'air': 1.2, 'low': 1.5, 'width': 1.0} · reverb 2.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'no_fx_sounds': True, 'spring': True, 'no_rotation': True, 'own_progs': True, 'no_layers': True, 'riff_locked': True, 'section_progs': {'verse': [0, 0, 0, 0], 'main': [0, 0, 5, 4], 'alt': [2, 6, 5, 2]}, 'repetition': 0.85}
- **Sound brief** Twangy baritone / six-string guitar doubling the bass on a low chromatic riff (spring reverb); electric bass; brass section stabs; trumpet melody for the bridge; sax section; driving surf drums with ride

## Pop & Indie

### Pop (`pop`)

Pop: four-chord hooks, piano & guitar, punchy drums, sing-along lead line

- **Tempo** 95-122 BPM · **scales** major · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4], [3, 4, 0, 5]] · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X...X...X...X...`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** unruly · preset `punchy`
- **Bass** `R.......R...R...` / `R...R...R.R.R...` / `R-..R-..R-..A...` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---x---x---x---` / `x-.x-.x-x-.x-.x-`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `x-x-x-x-x---x---` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `on_the_grid` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.3
  - clap (snare): `clap` -21 dB
  - chat (top): `chat` -28 dB · pan=0.2
  - bass (bass): `sawbass`  dB · sc=0.3 · alternatives ['sf:fingerbass', 'sinebass', 'moogbass']
  - chords (chords): `piano`  dB · rev=0.25 · alternatives ['guitar', 'sf:cleanguitar', 'epiano', 'pluck_saw', 'polysynth', 'wurli']
  - pad (pad): `strings` -26 dB · rev=0.4 · alternatives ['warmpad', 'organ', 'glasspad']
  - arp (arp): `guitar` -27 dB · pan=-0.3 · rev=0.2 · alternatives ['sf:cleanguitar', 'piano', 'pizz']
  - lead (lead): `pluck`  dB · rev=0.3 · dly=0.25 · alternatives ['piano', 'guitar', 'violin', 'flute']
- **Mix** {'lufs': -9.5, 'air': 2.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### City Pop (`city_pop`)

City pop: 80s Japanese pop - slap-style bass, lush 7th chords, Rhodes, brass & sax

- **Tempo** 104-120 BPM · **scales** major, dorian · swing 0.53 (unit 16) · humanise 0.005
- **Progressions** {'major': [[3, 2, 1, 4], [1, 4, 0, 5], [3, 4, 2, 5], [0, 5, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]]} · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X..x....X.X.....`; **snare** `....X.......X...`; **chat** `x.xxx.xxx.xxx.xx`; **ohat** `......x.......x.`
- **Drum kit** linn · preset `punchy`
- **Bass** `R..RO.R.R..R.OA.` / `R.R..O.R.RR..O.A` / `R..O.RR..R.O.R..` / `R.RO..R..RO..R.A` · mode `pattern` · lowest note 31
- **Chord rhythm** `x--.x--...x.x...` / `.x.x..x..x.x..x.` / `x--..x-..x-.x...`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x--.x--.x.x.x---` / `..x.x-x-x-------` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.35
  - chat (top): `chat` -28 dB
  - ohat (top): `ohat` -29 dB
  - bass (bass): `fmbass`  dB · alternatives ['sf:slapbass', 'sf:fingerbass', 'moogbass']
  - chords (chords): `epiano`  dB · rev=0.3 · alternatives ['piano', 'guitar', 'brass', 'polysynth', 'wurli', 'synthbrass']
  - pad (pad): `strings` -26 dB · rev=0.4 · alternatives ['warmpad', 'solina', 'sf:slowstrings']
  - arp (arp): `guitar` -27 dB · pan=-0.3 · alternatives ['sf:cleanguitar', 'epiano', 'marimba', 'mutedgtr', 'vibes']
  - lead (lead): `sax`  dB · rev=0.35 · dly=0.2 · alternatives ['sf:tenorsax', 'brass', 'leadsaw', 'epiano', 'flute', 'synthbrass', 'trumpet']
- **Mix** {'lufs': -10.0, 'air': 2.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.5, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Holiday (`holiday`)

Holiday / Christmas: sleigh bells, celesta, pizzicato, warm strings, brass and a cosy swing

- **Tempo** 100-140 BPM · **scales** major · swing 0.57 (unit 16) · humanise 0.008
- **Progressions** [[0, 5, 1, 4], [0, 3, 4, 0], [0, 2, 3, 4], [0, 3, 1, 4], [0, 5, 3, 4]] · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X.......X.x.....`; **snare** `....X.......X...`; **sleigh** `x.x.x.x.x.x.x.x.` / `xxxxxxxxxxxxxxxx`; **tamb** `....x.......x...`
- **Drum kit** brushes · preset `soft`
- **Bass** `R...F...R...F...` / `R.......F.......` / `R...F...R...A...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---x---x---x---` / `..x...x...x...x.` / `x--.x--.x---x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 6}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `x-x-x-x-x---x---` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -19 dB
  - snare (snare): `snare` -22 dB · rev=0.3
  - sleigh (top): `sleigh` -28 dB · pan=0.25
  - tamb (top): `tamb` -29 dB · pan=-0.25
  - bass (bass): `ebass` -16 dB · alternatives ['sf:acbass', 'sf:fingerbass', 'sf:pickbass']
  - chords (chords): `piano` -22 dB · rev=0.3 · alternatives ['epiano', 'guitar', 'harp', 'strings']
  - pad (pad): `strings` -25 dB · rev=0.4 · alternatives ['organ', 'choir', 'horn']
  - arp (arp): `celesta` -26 dB · pan=-0.2 · rev=0.35 · alternatives ['bell', 'pizz', 'harp', 'marimba', 'vibes']
  - lead (lead): `brass` -19 dB · rev=0.35 · alternatives ['flute', 'clarinet', 'violin', 'celesta', 'sax', 'sf:trumpet', 'oboe', 'trumpet', 'vibes']
- **Mix** {'lufs': -12.0, 'air': 1.8, 'low': 0.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Sleigh bells; Glockenspiel / celesta; Strings; Brass section; Pizzicato; Upright bass

### Chamber Pop (`chamber_pop`)

Chamber / orchestral pop: pop drums & piano with a string section, horns, pizzicato and glockenspiel

- **Tempo** 90-124 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4], [3, 4, 0, 5], [0, 2, 3, 4]], 'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X...X...X...X...`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `....x.......x...`
- **Drum kit** studio · preset `punchy`
- **Bass** `R.......R...R...` / `R...R...R.R.R...` / `R-..R-..R-..A...` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---x---x---x---` / `x-.x-.x-x-.x-.x-` / `x.x.x.x.x.x.x.x.`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.8}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `x-x-x-x-x---x---` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - tamb (top): `tamb` -30 dB · pan=-0.25
  - bass (bass): `upright` -16 dB · alternatives ['sf:fingerbass', 'cello', 'sf:acbass']
  - chords (chords): `piano`  dB · rev=0.25 · alternatives ['guitar', 'epiano', 'harp', 'spiccato']
  - pad (pad): `strings` -24 dB · rev=0.4 · alternatives ['sf:slowstrings', 'horn', 'organ']
  - arp (arp): `pizz` -25 dB · pan=-0.3 · rev=0.3 · alternatives ['celesta', 'harp', 'bell', 'marimba', 'spiccato', 'vibes']
  - lead (lead): `violin` -18 dB · rev=0.35 · alternatives ['flute', 'horn', 'cello', 'piano', 'oboe', 'clarinet', 'trumpet']
- **Mix** {'lufs': -10.5, 'air': 1.8, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Piano; String section (legato pad + spiccato); Pizzicato / glockenspiel; Horns; Violin or flute counter-melody

### Bedroom / indie pop (`bedroom_pop`)

Bedroom / indie pop: a bouncy drum machine with a syncopated kick, warm synth bass, chorused clean guitar and soft poly synths, bubbly plucks and sparkly bells, sweet major chords with 7ths - dreamy, cute and loud

- **Tempo** 108-122 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'major': [[0, 5, 3, 4], [3, 4, 0, 5], [0, 2, 3, 4], [1, 4, 0, 5]], 'mixolydian': [[0, 6, 3, 0], [0, 3, 6, 0]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X..X.X......X.X.` / `X..X.X....X.....` / `X..X..X...X..X..`; **snare** `....X.......X...`; **clap** `....x.......x...`; **chat** `x.x.x.x.x.x.x.x.` / `xxx.xxx.xxx.xxx.`; **shaker** `..x...x...x...x.`; **tamb** `....x.......x...`
- **Drum kit** 707 · preset `707`
- **Bass** `R..R.R....R.R...` / `R.......R..R.R..` / `R..R..R...R..R.A` · mode `pattern` · lowest note 33
- **Chord rhythm** `x-x-..x-x-..x-..` / `x--.x--.x--.x---` / `x.x...x.x.x...x.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 6, 'prob': 0.8}
- **Lead rhythm** `x-x-x---x-x-----` / `..x-x-x-x---....` / `x---x---x-x-x---` / `x-x-x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -16 dB · rev=0.25
  - clap (snare): `clap` -22 dB · rev=0.25
  - chat (top): `chat` -28 dB · pan=0.2
  - shaker (top): `shaker` -30 dB · pan=-0.3
  - tamb (top): `tamb` -31 dB · pan=0.3
  - bass (bass): `moogbass` -14 dB · alternatives ['ebass', 'sawbass', 'sf:fingerbass']
  - chords (chords): `guitar` -21 dB · pan=-0.3 · rev=0.3 · alternatives ['sf:cleanguitar', 'polysynth', 'epiano', 'wurli']
  - keys (chords): `polysynth` -25 dB · pan=0.3 · rev=0.3
  - pad (pad): `warmpad` -28 dB · rev=0.4 · alternatives ['solina', 'glasspad', 'strings']
  - arp (arp): `bell` -27 dB · pan=0.25 · rev=0.4 · dly=0.3 · alternatives ['pluck', 'chip', 'marimba', 'celesta', 'kalimba']
  - lead (lead): `pluck` -19 dB · rev=0.35 · dly=0.25 · alternatives ['chip', 'bell', 'softlead', 'glasspad', 'guitar']
- **Mix** {'lufs': -8.0, 'air': 1.0, 'low': 1.4, 'width': 0.6} · reverb 2.0 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Drum machine (707 / Linn-ish) with a bouncy kick; warm synth bass; chorused clean electric guitar; soft poly synth; bubbly plucks / bells (KKB); glassy synth lead

### 80s sophisti-pop / jazz-funk pop (`sophisti_pop`)

Mid-80s sophisti-pop / jazz-funk pop: a tight, bright drum-machine-and-live groove around 103, a busy slap / thumbed bass, lush synth pads and chorused electric piano, jazzy major-7 and 9th chords, crisp synth brass and a smooth sung-style lead - polished, upbeat and wistful

- **Tempo** 98-110 BPM · **scales** major, dorian, minor · swing 0.52 (unit 16) · humanise 0.004
- **Progressions** {'major': [[3, 4, 2, 5], [1, 4, 0, 5], [0, 3, 1, 4]], 'dorian': [[0, 3, 0, 3]], 'minor': [[5, 3, 0, 6]]} · chord_bars 1 · chord size 4
- **Song form** `sophisti_pop`: intro 8 [bass, kick, pad, top] -> verse 16 [bass, chords, kick, pad, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, kick, pad, top] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [bass, chords, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X..x....X.......`; **snare** `....X.......X...`; **chat** `x.xxx.xxx.xxx.xx`; **tamb** `....x.......x...`
- **Drum kit** big80s · preset `linn`
- **Bass** `R.xR.R.O.xR.R.O.` / `R.R..O.xR..R.Ox.` / `R..RO..xR.R..O..` · mode `pattern` · lowest note 33
- **Chord rhythm** `x-..x-....x-....` / `..x-..x-..x-..x-`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-x-x-------` / `..x-x---x-x-....` / `x-x-x---x-------`
- **Build-ups** default `(category default)` · choices ['pickup', 'lift', 'stops']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -15 dB · rev=0.3
  - chat (top): `chat` -27 dB · pan=0.2
  - tamb (top): `tamb` -31 dB · pan=-0.3
  - bass (bass): `fmbass` -13 dB · alternatives ['sf:slapbass', 'moogbass', 'sawbass']
  - chords (chords): `m1piano` -22 dB · rev=0.3 · alternatives ['epiano', 'polysynth', 'piano']
  - pad (pad): `polysynth` -26 dB · rev=0.4 · alternatives ['strings', 'solina', 'warmpad']
  - arp (arp): `synthbrass` -27 dB · pan=0.25 · alternatives ['epiano', 'brass', 'polysynth']
  - lead (lead): `softlead` -19 dB · rev=0.35 · dly=0.25 · alternatives ['sax', 'synthbrass', 'flute']
- **Mix** {'lufs': -10.5, 'air': 1.6, 'low': 1.2, 'width': 1.0} · reverb 2.4 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.55, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Tight 80s kit (gated snare) + live hats; slap bass; chorused DX-style electric piano; lush pads; synth brass

### Psychedelic synth-pop (`psych_pop`)

Psychedelic synth-pop (2010s-20s): punchy, dry, compressed drums with a fat kick around 112-120, a melodic, busy bass guitar, phased and chorused synth chords that swell and swirl, dreamy pads and a wistful synth / guitar lead - big, warm and woozy

- **Tempo** 110-122 BPM · **scales** major, mixolydian, dorian · swing 0.52 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 4, 5, 3], [0, 2, 3, 4], [3, 4, 0, 5]], 'mixolydian': [[0, 6, 3, 0]], 'dorian': [[0, 3, 0, 6]]} · chord_bars 1 · chord size 4
- **Song form** `psych_pop`: intro 4 [bass, chords, kick, snare, top] -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 12 [arp, bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 12 [bass, chords, kick, pad, snare] (alt) -> chorus 8 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> break 8 [chords, fx, pad, top] -> chorus 8 [arp, bass, chords, kick, lead, pad, snare, top] (crash) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X..X....X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `..x...x...x...x.`
- **Drum kit** dead70s · preset `acoustic`
- **Bass** `R--.R-.O..R-.F..` / `R-..R-R-..R-.O..` / `R.R.O...R..R.F..` · mode `pattern` · lowest note 31
- **Chord rhythm** `x-------x-------` / `x---x---x---x---` / `x-..x-..x-..x-..`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x---x-x-x-------` / `..x-x---x-x-x---`
- **Build-ups** default `(category default)` · choices ['pickup', 'lift', 'none'] · transitions ['crash', 'none', 'swell']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `club_punchy` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -14 dB · rev=0.25
  - chat (top): `chat` -28 dB · pan=0.2
  - tamb (top): `tamb` -30 dB · pan=-0.3
  - bass (bass): `ebass` -13 dB · sc=0.3 · alternatives ['moogbass', 'sf:fingerbass', 'sf:pickbass']
  - chords (chords): `polysynth` -20 dB · rev=0.35 · sc=0.4 · alternatives ['epiano', 'synthbrass', 'stab']
  - pad (pad): `glasspad` -26 dB · rev=0.5 · alternatives ['solina', 'warmpad']
  - arp (arp): `pluck_saw` -27 dB · dly=0.3 · alternatives ['pluck', 'stab', 'acid']
  - lead (lead): `softlead` -19 dB · rev=0.35 · dly=0.3 · alternatives ['guitar', 'polysynth', 'flute']
- **Mix** {'lufs': -9.0, 'air': 1.0, 'low': 1.8, 'width': 1.1} · reverb 2.4 · sc_depth 0.35
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Punchy, dry, heavily compressed drums; melodic bass guitar; phased Juno / Prophet chords; dreamy pads; wistful synth or guitar lead; lots of phaser / chorus

## Funk & Disco

### Disco (`disco`)

Disco / nu-disco: four-on-the-floor, octave bass, string sweeps, brass hits, funky guitar

- **Tempo** 112-124 BPM · **scales** minor, dorian · swing 0.52 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 3, 6, 5], [0, 5, 3, 4]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 4]]} · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`; **conga** `...x..x....x.x..`
- **Drum kit** studio · preset `acoustic`
- **Bass** `R.O.R.O.R.O.R.O.` / `R.ORR.O.R.ORR.O.` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x.x..x..x.x..x` / `x.xx.xx.x.xx.xx.`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x-..x-x.x-..` / `x--.x--.x.x.x---` / `..x.x..x..x.x...` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.2
  - ohat (top): `ohat` -26 dB
  - chat (top): `chat` -29 dB · pan=0.2
  - conga (top): `conga` -29 dB · pan=-0.3
  - bass (bass): `ebass`  dB · sc=0.4 · alternatives ['sf:fingerbass', 'sf:slapbass', 'moogpluck']
  - chords (chords): `guitar` -24 dB · pan=-0.3 · rev=0.15 · alternatives ['sf:cleanguitar', 'sf:muted', 'epiano', 'piano', 'clav']
  - pad (pad): `strings` -24 dB · pan=0.2 · rev=0.4 · alternatives ['sf:slowstrings', 'organ', 'solina', 'synthbrass']
  - arp (arp): `epiano` -27 dB · rev=0.2 · alternatives ['guitar', 'piano', 'clav', 'mutedgtr']
  - lead (lead): `brass` -20 dB · rev=0.3 · alternatives ['sf:trumpet', 'strings', 'flute', 'sax', 'violin', 'trumpet']
- **Mix** {'lufs': -10.0, 'air': 2.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.6, 'chord_center': 66, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Funk (`funk`)

Funk: the one, syncopated 16th grooves, slap / finger bass, clavinet chops, chicken-scratch guitar, horn stabs

- **Tempo** 96-112 BPM · **scales** dorian, mixolydian · swing 0.54 (unit 16) · humanise 0.006
- **Progressions** {'dorian': [[0, 0, 3, 3], [0, 3, 0, 4]], 'mixolydian': [[0, 0, 3, 0], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X..x..X...X..x..` / `X.x...X..x..X...`; **snare** `....X.......X...`; **chat** `xxxxxxxxxxxxxxxx` / `x.xxx.xxx.xxx.xx`; **ohat** `......x.........`
- **Drum kit** seventies · preset `acoustic`
- **Bass** `R..O.R...RR.O..A` / `R.R..O.R..R.O.R.` / `R...O.RR..R.O..A` · mode `pattern` · lowest note 31
- **Chord rhythm** `.x.xX.x..x.xX.x.` / `x.xX..x.x.xX..x.` / `.xX.x.x..xX.x.x.` / `X.x..x.xX.x..x.x`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'rh': ['.x.x.x.x.x.x.x.x', 'xx.xx.x.xx.xx.x.', '.x.xx.x..x.xx.x.']}
- **Lead rhythm** `x.x.x...x.x.....` / `..x..x.x..x.....` / `x..x..x.x.......` / `x-x-x-..x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `groove_locked` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `static_vamp` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare`  dB · rev=0.15
  - chat (top): `chat` -22 dB · pan=0.2
  - ohat (top): `ohat` -25 dB
  - bass (bass): `ebass` -17 dB · alternatives ['sf:slapbass', 'sf:fingerbass', 'moogpluck']
  - chords (chords): `clav` -19 dB · pan=-0.25 · alternatives ['epiano', 'sf:muted', 'wurli', 'organ', 'guitar']
  - horns (chords): `brass` -22 dB · pan=0.15 · rev=0.2
  - pad (pad): `organ` -28 dB · pan=0.25 · rev=0.3 · alternatives ['brass', 'strings', 'synthbrass']
  - arp (arp): `mutedgtr` -26 dB · pan=0.35 · alternatives ['sf:muted', 'guitar', 'clav']
  - lead (lead): `brass`  dB · rev=0.25 · alternatives ['sax', 'sf:tenorsax', 'sf:trumpet', 'organ', 'flute', 'trumpet', 'synthbrass']
- **Mix** {'lufs': -10.0, 'air': 1.5, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.5, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'no_rotation': True}

### Disco Funk (70s) (`disco_funk`)

70s disco-funk: punchy dry four-on-the-floor, a syncopated electric-bass hook, chicken-scratch guitar, tight horn-section riffs, claps, congas and tambourine - bright, catchy party music

- **Tempo** 112-122 BPM · **scales** major, mixolydian, dorian · swing 0.53 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 3, 0, 3], [0, 3, 4, 3], [0, 5, 1, 4], [0, 0, 3, 4]], 'mixolydian': [[0, 6, 3, 0], [0, 3, 0, 6]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 4]]} · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `....X.......X...`; **clap** `....X.......X...`; **ohat** `..x...x...x...x.`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `..x...x...x...x.` / `x.xxx.xxx.xxx.xx`; **conga** `...x..x....x.x..` / `......x..x....x.`
- **Drum kit** seventies · preset `acoustic`
- **Bass** `R..O.R.OR.R..O.A` / `R.R..O.RR..O.RA.` / `R...R.OR..R.O.R.` / `R.OR..R.R.OR..A.` · mode `pattern` · lowest note 31
- **Chord rhythm** `.x.x.x.x.x.x.x.x` / `x.xx.x.xx.xx.x.x` / `..x...x...x...x.`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x-..........` / `..x.x.x-..x.x-..` / `x-x-x---........` / `x.x-..x.x-......`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `groove_locked` · density `dense` · feel `live_drums` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -18 dB · rev=0.15
  - clap (snare): `clap` -22 dB · rev=0.12
  - ohat (top): `ohat` -28 dB · pan=0.2
  - chat (top): `chat` -30 dB · pan=-0.2
  - tamb (top): `tamb` -29 dB · pan=0.35
  - conga (top): `conga` -27 dB · pan=-0.3
  - bass (bass): `ebass` -14 dB · alternatives ['sf:fingerbass', 'sf:slapbass', 'moogpluck']
  - chords (chords): `mutedgtr` -23 dB · pan=-0.25 · rev=0.12 · alternatives ['guitar', 'clav', 'epiano', 'organ']
  - pad (pad): `strings` -29 dB · pan=0.2 · rev=0.35 · alternatives ['organ', 'synthbrass', 'solina']
  - arp (arp): `clav` -26 dB · pan=0.25 · rev=0.15 · alternatives ['epiano', 'mutedgtr', 'piano']
  - lead (lead): `brass` -18 dB · rev=0.2 · alternatives ['trumpet', 'sax', 'synthbrass', 'flute']
- **Mix** {'lufs': -10.0, 'air': 2.0, 'low': 1.0} · reverb 1.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.5, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.7}
- **Sound brief** Horn section (trumpet, sax, trombone); chicken-scratch guitar; electric bass; clavinet / Rhodes; strings for gloss

### Smooth Jazz-Funk (`smooth_funk`)

Smooth jazz-funk: a funky slap-and-pop bass groove, crisp 16th hats, jazz-guitar octave melodies, sax answers, bright electric piano and stabby brass

- **Tempo** 96-116 BPM · **scales** dorian, minor, major · swing 0.54 (unit 16) · humanise 0.006
- **Progressions** {'dorian': [[0, 3, 0, 3], [0, 6, 3, 2], [1, 4, 0, 0]], 'minor': [[0, 3, 6, 5], [5, 1, 4, 0]], 'major': [[1, 4, 0, 5], [3, 4, 2, 5]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X..X..` / `X..X..X...X.....`; **snare** `....X.......X...`; **chat** `xxxxxxxxxxxxxxxx` / `x.xxx.xxx.xxx.xx`; **ohat** `......x.......x.`
- **Drum kit** studio · preset `punchy`
- **Bass** `R.R...O.R..R..A.` / `R..R.O..R.R..O..` / `R.....R.O.R...F.` · mode `pattern` · lowest note 28
- **Chord rhythm** `..x...x...x..x..` / `x..x..x...x.....`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 4, 'prob': 0.3}
- **Lead rhythm** `x.x.x...x.x.....` / `x-x-..x-x-x-....` / `..x.x.x.x---....` / `x..x..x.x.......`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `groove_locked` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `modal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -18 dB · rev=0.2
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -30 dB · pan=-0.2
  - bass (bass): `sf:slapbass` -13 dB · alternatives ['fmbass', 'moogpluck', 'sf:fingerbass']
  - chords (chords): `epiano` -21 dB · pan=-0.15 · rev=0.25 · alternatives ['clav', 'wurli', 'piano']
  - pad (pad): `brass` -26 dB · rev=0.3 · alternatives ['synthbrass', 'strings', 'horn']
  - lead (lead): `acguitar` -17 dB · rev=0.3 · dly=0.12 · alternatives ['sax', 'twang', 'flute', 'trumpet']
  - lead_oct (lead): `acguitar` -21 dB · rev=0.3
  - arp (arp): `sax` -23 dB · pan=0.25 · rev=0.35 · alternatives ['brass', 'vibes', 'epiano']
- **Mix** {'lufs': -10.5, 'air': 1.6, 'low': 1.4} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.25, 'own_progs': True}
- **Sound brief** Slap bass; jazz guitar in octaves; tenor sax; Rhodes / DX e-piano; horn section stabs; tight funk kit

### 80s electro-funk / boogie (`electro_funk`)

80s electro-funk / boogie slow jam: a slow, heavy drum-machine groove with big claps, a rubbery Minimoog bass, poly-synth chord stabs and Rhodes, a sparkly bell arp and the gliding talk-box style synth lead

- **Tempo** 84-100 BPM · **scales** minor, dorian · swing 0.55 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 3, 0, 3], [0, 5, 3, 4], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 1, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X......X..X.....` / `X.....X...X..X..` / `X......XX.X.....`; **clap** `....X.......X...`; **snare** `....X.......X...`; **chat** `x.xxx.xxx.xxx.xx` / `x.x.x.x.x.x.x.x.`; **ohat** `......x.......x.`; **cowbell808** `..x.....x.x.....`
- **Drum kit** dmx · preset `dmx`
- **Bass** `R--.R-.O..R-.R..` / `R--..R.O..R-..RA` / `R-.R..O...R-.R.O` · mode `pattern` · lowest note 31
- **Chord rhythm** `x-..x-....x-....` / `..x-..x-..x-..x-` / `X---..x-..x-....`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 6, 'prob': 0.6}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x---x---` / `..x-x-x-x-------` / `x-------x-x-x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `groove_locked` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `progressive` · culture `underground_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `flat_hypnotic`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -17 dB · rev=0.45
  - snare (snare): `snare` -21 dB · rev=0.3
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - cowbell808 (top): `cowbell808` -32 dB · pan=0.3
  - bass (bass): `moogpluck` -12 dB · alternatives ['fmbass', 'sawbass', 'sf:fingerbass']
  - chords (chords): `polysynth` -23 dB · rev=0.3 · alternatives ['synthbrass', 'epiano', 'clav']
  - pad (pad): `epiano` -26 dB · rev=0.3 · alternatives ['strings', 'solina', 'polysynth']
  - arp (arp): `bell` -29 dB · pan=0.3 · rev=0.45 · dly=0.3 · alternatives ['vibes', 'celesta', 'pluck']
  - lead (lead): `talkbox` -17 dB · rev=0.3 · dly=0.2 · alternatives ['whine', 'softlead']
- **Mix** {'lufs': -11.0, 'air': 1.3, 'low': 1.3} · reverb 2.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap'], 'bass_gate': 0.75, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'lead_glide': True, 'no_rotation': True}
- **Sound brief** DMX / LinnDrum, big claps; Minimoog bass; Prophet-5 / Oberheim stabs; Rhodes; bell arp; talk box

## Soul, R&B & Gospel

### Soul Ballad (12/8) (`soul_ballad`)

Soul / doo-wop ballad (12/8): triplet piano, slow backbeat, organ and strings, a big vocal-style lead

- **Tempo** 48-66 BPM · meter 12/8 · **scales** major · swing 0.5 (unit 16) · humanise 0.01
- **Progressions** [[0, 5, 3, 4], [0, 5, 1, 4], [0, 3, 4, 0], [0, 2, 3, 4]] · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 0.5
- **Drums** **kick** `X.....X..X..` / `X.....X.....`; **snare** `...X.....X..`; **chat** `xxxxxxxxxxxx`; **ride** `x..x..x..x..`
- **Drum kit** brushes · preset `soft`
- **Bass** `R.....R..F..` / `R..R..F..A..` / `R.....F.....` · mode `pattern` · lowest note 31
- **Chord rhythm** `xxxxxxxxxxxx` / `x..x..x..x..` / `x.xx.xx.xx.x`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x--x--x--...` / `x-xx-xx-x...` / `x-----x-xx..` / `x--x-xx-....`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `emotional_swell` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -19 dB
  - snare (snare): `snare` -19 dB · rev=0.35
  - chat (top): `chat` -30 dB
  - ride (top): `ride` -31 dB
  - bass (bass): `ebass` -16 dB · alternatives ['sf:fingerbass', 'sf:acbass', 'sf:pickbass']
  - chords (chords): `piano` -21 dB · rev=0.3 · alternatives ['epiano', 'organ', 'guitar', 'wurli']
  - pad (pad): `organ` -27 dB · rev=0.3 · alternatives ['strings', 'choir', 'warmpad']
  - lead (lead): `sax` -18 dB · rev=0.35 · alternatives ['sf:tenorsax', 'guitar', 'organ', 'strings', 'trumpet']
- **Mix** {'lufs': -12.0, 'air': 1.2, 'low': 1.0} · reverb 2.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Piano (triplets); Hammond organ; Strings; Saxophone or vocal lead; Bass guitar

### Gospel (`gospel`)

Gospel: Hammond organ and piano, choir, hand claps, swinging backbeat and a preaching lead

- **Tempo** 70-120 BPM · **scales** major · swing 0.6 (unit 16) · humanise 0.008
- **Progressions** [[0, 3, 0, 4], [3, 4, 2, 5], [0, 5, 1, 4], [3, 3, 0, 5], [0, 2, 3, 4]] · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.....X.X.......` / `X.......X.x.....`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `....x.......x...`
- **Drum kit** seventies · preset `acoustic`
- **Bass** `R...R.F.R...A...` / `R..R..F.R..R.A..` / `R-..F-..R-..A...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x--.x--.x--.x---` / `..x...x...x...x.` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `..x-x-x-x---x---` / `x-.x-.x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `gospel_church` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - snare (snare): `snare`  dB · rev=0.3
  - clap (snare): `clap` -20 dB · rev=0.35
  - chat (top): `chat` -28 dB
  - tamb (top): `tamb` -29 dB · pan=0.3
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'fmbass', 'sf:pickbass']
  - chords (chords): `organ`  dB · pan=-0.2 · rev=0.25 · alternatives ['piano', 'epiano', 'wurli']
  - pad (pad): `choir` -24 dB · rev=0.4 · alternatives ['organ', 'strings', 'warmpad']
  - arp (arp): `piano` -24 dB · pan=0.25 · rev=0.25 · alternatives ['organ', 'epiano']
  - lead (lead): `piano` -18 dB · rev=0.3 · alternatives ['organ', 'choir', 'sax', 'guitar']
- **Mix** {'lufs': -11.0, 'air': 1.4, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Hammond B3 organ (Leslie); Piano; Choir; Bass; Hand claps

### Motown / 60s Soul (`motown`)

Motown / 60s soul: tambourine on every backbeat, melodic bass, piano and guitar chops, strings and horns

- **Tempo** 100-126 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 5, 3, 4], [0, 3, 1, 4], [0, 2, 3, 4], [3, 4, 0, 5]], 'minor': [[0, 3, 6, 4], [0, 6, 5, 4]]} · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X...X...X...X...`; **snare** `....X.......X...`; **tamb** `....x.......x...` / `x.x.x.x.x.x.x.x.`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** seventies · preset `acoustic`
- **Bass** `R..R.R..F..A....` / `R...R..RF...A.R.` / `R.R...R.F.F.A...` · mode `pattern` · lowest note 28
- **Chord rhythm** `....x.......x...` / `x---x---x---x---` / `..x...x...x...x.`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `..x-x-x-x---x---` / `x-x-x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - snare (snare): `snare`  dB · rev=0.3
  - tamb (top): `tamb` -25 dB · pan=0.3
  - chat (top): `chat` -29 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'sf:pickbass', 'moogbass']
  - chords (chords): `piano` -22 dB · rev=0.25 · alternatives ['guitar', 'sf:cleanguitar', 'organ', 'epiano', 'wurli']
  - pad (pad): `strings` -25 dB · rev=0.4 · alternatives ['sf:slowstrings', 'organ', 'brass']
  - arp (arp): `guitar` -26 dB · pan=-0.3 · alternatives ['sf:cleanguitar', 'piano', 'mutedgtr']
  - lead (lead): `brass` -19 dB · rev=0.3 · alternatives ['sax', 'sf:tenorsax', 'strings', 'flute', 'sf:trumpet', 'trumpet']
- **Mix** {'lufs': -11.0, 'air': 1.3, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Bass guitar (melodic, Jamerson-style); Piano; Rhythm guitar; Strings; Horn section; Tambourine

### R&B / Neo-soul (`rnb`)

R&B: lazy swung drums, Rhodes 9th chords, deep sub bass, finger snaps and clean guitar licks

- **Tempo** 66-98 BPM · **scales** minor, dorian, major · swing 0.58 (unit 16) · humanise 0.012
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 3, 6, 5], [0, 6, 5, 3]], 'dorian': [[0, 3, 0, 3], [0, 3, 6, 2]], 'major': [[1, 4, 0, 5], [3, 2, 1, 4], [3, 4, 2, 5]]} · chord_bars 1 · chord size 5
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 0.75
- **Drums** **kick** `X......X..X.....` / `X.....X...X..x..`; **snare** `....X.......X...`; **snap** `....X.......X...`; **chat** `x.xxx.x.x.xxx.x.` / `x.x.x.x.x.x.x.xx`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R-----..R---F...` / `R---..R-..F-A...` / `R-....R...R-....` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------x-----` / `x-------..x-----` / `x--.....x--.....`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-..x-x---....` / `..x-x-x-x-x-....` / `x-.x-.x-x-------` / `x---x-x---......`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `sub_only` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare` -18 dB · rev=0.3
  - snap (snare): `snap` -22 dB
  - chat (top): `chat` -28 dB
  - bass (bass): `sinebass` -13 dB · alternatives ['sf:fingerbass', 'fmbass', '808', 'moogbass']
  - chords (chords): `epiano`  dB · rev=0.3 · dly=0.15 · alternatives ['piano', 'guitar', 'sf:cleanguitar', 'organ', 'wurli', 'polysynth']
  - pad (pad): `warmpad` -28 dB · rev=0.4 · alternatives ['strings', 'glasspad', 'solina']
  - lead (lead): `sf:cleanguitar` -20 dB · rev=0.35 · dly=0.2 · alternatives ['guitar', 'softlead', 'epiano', 'sax', 'flute']
- **Mix** {'lufs': -11.0, 'air': 1.4, 'low': 1.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'snap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Rhodes / Wurlitzer; Sub or finger bass; Snaps; Pads; Vocal-style lead or guitar

### Quiet Storm (`quiet_storm`)

Quiet storm / late-night smooth (late-night radio): slow and intimate - soft Rhodes, a breathy sax, warm fretless bass, brushed snare and long string pads, all candle-light and velvet

- **Tempo** 62-80 BPM · **scales** minor, dorian, major · swing 0.56 (unit 16) · humanise 0.012
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 3, 6, 2], [5, 3, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 2]], 'major': [[3, 2, 1, 0], [1, 4, 0, 5]]} · chord_bars 1 · chord size 5
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X......X..X.....`; **rim** `....x.......x...`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** brushes · preset `soft`
- **Bass** `R-------R---F---` / `R-----..R-F-....` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-------x---....` / `..x-x---x-------` / `x---x-----x-....` / `x-------x-x-----`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `emotional_swell` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `swung_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -18 dB
  - rim (snare): `rim` -23 dB · rev=0.35
  - chat (top): `chat` -31 dB
  - bass (bass): `sf:fingerbass` -14 dB · alternatives ['moogbass', 'ebass', 'upright']
  - chords (chords): `epiano` -19 dB · rev=0.45 · dly=0.15 · alternatives ['wurli', 'piano', 'clav']
  - pad (pad): `strings` -26 dB · rev=0.55 · alternatives ['warmpad', 'glasspad', 'solina']
  - lead (lead): `sax` -16 dB · rev=0.5 · dly=0.2 · alternatives ['acguitar', 'flute', 'softlead']
- **Mix** {'lufs': -13.0, 'air': 1.0, 'low': 1.3} · reverb 2.8 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['rim'], 'bass_gate': 0.92, 'chord_center': 61, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.35, 'own_progs': True}
- **Sound brief** Breathy tenor / alto sax; Rhodes; fretless bass; brushed kit; string pad; nylon or clean guitar

### Neo-Soul (`neo_soul`)

Neo-soul: drunk, behind-the-beat drums, lush Rhodes 9th and 11th chords, warm finger bass, soft guitar and flute answers

- **Tempo** 72-92 BPM · **scales** dorian, minor, major · swing 0.6 (unit 16) · humanise 0.014
- **Progressions** {'dorian': [[0, 3, 0, 3], [0, 3, 6, 2], [1, 4, 0, 0]], 'minor': [[0, 5, 3, 4], [3, 6, 2, 5]], 'major': [[1, 4, 0, 5], [3, 2, 1, 4], [5, 1, 4, 0]]} · chord_bars 1 · chord size 5
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X......X..X..x..` / `X.....x...X.....` / `X..x......X.x...`; **snare** `....X.......X...`; **rim** `......o.......o.`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`
- **Drum kit** funky_drummer · preset `soft`
- **Bass** `R-----..R-F-....` / `R---..R...F-A...` / `R-..R-....R-F-..` · mode `pattern` · lowest note 28
- **Chord rhythm** `x-------..x-----` / `x---------x-....` / `x--.....x--.....`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `..x-x-x-x---....` / `x-.x-.x-x-------` / `....x-x-x-x-....` / `x---..x-x-x-....`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -15 dB
  - snare (snare): `snare` -18 dB · rev=0.25
  - rim (top): `rim` -29 dB
  - chat (top): `chat` -29 dB · pan=-0.15
  - bass (bass): `moogpluck` -14 dB · alternatives ['sf:fingerbass', 'upright', 'sinebass']
  - chords (chords): `epiano` -19 dB · rev=0.3 · dly=0.1 · alternatives ['wurli', 'piano', 'organ']
  - pad (pad): `warmpad` -29 dB · rev=0.4 · alternatives ['organ', 'strings', 'glasspad']
  - lead (lead): `sf:cleanguitar` -21 dB · pan=0.2 · rev=0.3 · dly=0.15 · alternatives ['flute', 'epiano', 'sax', 'vibes', 'guitar']
- **Mix** {'lufs': -11.5, 'air': 0.8, 'low': 1.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Rhodes / Wurlitzer; finger bass; brushed / dusty kit with ghost notes; clean jazz guitar; flute

### New Jack Swing / 90s R&B (`new_jack_swing`)

New jack swing / 90s R&B: hard swung 16th drums, big snare + clap backbeat, punchy synth-brass and stab chords, FM bass, bright electric piano

- **Tempo** 100-114 BPM · **scales** minor, dorian · swing 0.62 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 3, 4, 3], [0, 6, 5, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `njs`: intro 4 [bass, chords, kick, snare, top] -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, kick, pad, snare, top] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [bass, chords, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X..X..X...X..X..` / `X.X...X...X.X...`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `xxxxxxxxxxxxxxxx`; **ohat** `......x.......x.`
- **Drum kit** linn · preset `punchy`
- **Bass** `R..R..R...R..R..` / `R.R...R.R...R...` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x...x...x..x..` / `x..x..x...x.....`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x...x.x.....` / `x..x..x.x.......` / `x-x-..x-x-x-....`
- **Build-ups** default `claps` · choices ['pickup', 'stops', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -16 dB · rev=0.25
  - clap (snare): `clap` -19 dB · rev=0.2
  - chat (top): `chat` -28 dB · pan=0.2
  - ohat (top): `ohat` -29 dB · pan=-0.2
  - bass (bass): `fmbass` -14 dB · alternatives ['moogbass', 'sawbass', 'reese']
  - chords (chords): `stab` -21 dB · rev=0.2 · alternatives ['epiano', 'synthbrass', 'polysynth']
  - pad (pad): `epiano` -26 dB · rev=0.3 · alternatives ['polysynth', 'synthbrass', 'warmpad']
  - lead (lead): `synthbrass` -20 dB · rev=0.25 · dly=0.1 · alternatives ['brass', 'epiano', 'leadsaw']
- **Mix** {'lufs': -9.5, 'air': 1.6, 'low': 1.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Synth brass (Prophet / DX7 brass); stab chords; FM bass; DX7 e-piano; LinnDrum / SP-1200 swing

### 90s R&B Slow Jam (`slow_jam`)

90s R&B slow jam: candle-lit and swung - DX electric piano 9ths, finger snaps on 2 and 4, a deep sub bass, soft 16th hats, lush strings and a smooth clean-guitar line

- **Tempo** 58-72 BPM · **scales** major, minor, dorian · swing 0.6 (unit 16) · humanise 0.008
- **Progressions** {'major': [[3, 2, 1, 4], [1, 4, 0, 5], [0, 5, 3, 4], [3, 4, 2, 5]], 'minor': [[0, 5, 3, 4], [5, 3, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 2]]} · chord_bars 1 · chord size 5
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X......X..X.....` / `X.....X...X..x..`; **snare** `....X.......X...`; **snap** `....X.......X...`; **chat** `x.xxx.xxx.xxx.xx` / `x.x.x.x.x.x.x.xx`
- **Drum kit** 808 · preset `soft`
- **Bass** `R-----..R---F...` / `R---..R-..F-A...` / `R-------R-F-....` · mode `pattern` · lowest note 26
- **Chord rhythm** `x---------x-----` / `x-------..x-----`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-..x-x---....` / `..x-x-x-x-x-....` / `x---x-x---......` / `x-.x-.x-x-------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `sub_only` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -19 dB · rev=0.35
  - snap (snare): `snap` -21 dB · rev=0.3
  - chat (top): `chat` -29 dB · pan=0.2
  - bass (bass): `sinebass` -12 dB · alternatives ['moogbass', '808', 'reese']
  - chords (chords): `epiano` -18 dB · rev=0.35 · dly=0.12 · alternatives ['wurli', 'piano', 'clav']
  - pad (pad): `strings` -25 dB · rev=0.5 · alternatives ['warmpad', 'solina', 'sf:slowstrings']
  - lead (lead): `sf:cleanguitar` -20 dB · rev=0.35 · dly=0.2 · alternatives ['epiano', 'sax', 'softlead']
- **Mix** {'lufs': -11.0, 'air': 1.4, 'low': 1.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'snap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True}
- **Sound brief** DX7 e-piano; sub / Moog bass; finger snaps; strings; clean guitar; 808 kick, soft hats; wind chimes

### Modern Gospel (`modern_gospel`)

Modern gospel: a big choir pad, Hammond organ and piano over modern drums and a deep 808, uplifting major and mixolydian changes with passing chords, a bridge that drops down and a last chorus that lifts

- **Tempo** 70-110 BPM · **scales** major, mixolydian · swing 0.55 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 4, 5, 3], [0, 5, 3, 4], [3, 0, 4, 5], [0, 3, 4, 0], [3, 4, 2, 5]], 'mixolydian': [[0, 6, 0, 6], [0, 3, 6, 0]]} · chord_bars 1 · chord size 4
- **Song form** `modern_gospel`: intro 4 [chords, pad] (filter_in) -> verse 8 [bass, chords, kick, pad, top] -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> verse 8 [bass, chords, kick, pad, snare, top] -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 4 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X.....X.X.......` / `X...X...X...X...`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`
- **Drum kit** (synth preset) · preset `acoustic`
- **Bass** `R-------R-------` / `R-----R-R---A...` / `R...R...R...R...` · mode `808` · lowest note 28
- **Chord rhythm** `x-------x-------` / `x---x---x---x---` / `x--.x--.x---x---`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x---x---` / `x-----x-x-------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `808_slide` · drop `emotional_swell` · variation `sectional` · culture `gospel_church` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `jazz_extensions` · energy `continuous_climb`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -16 dB · rev=0.35
  - clap (snare): `clap` -21 dB · rev=0.3
  - chat (top): `chat` -28 dB
  - bass (bass): `808` -14 dB · sc=0.5 · alternatives ['sinebass', 'moogbass', 'ebass']
  - chords (chords): `organ` -20 dB · pan=-0.2 · rev=0.35 · alternatives ['piano', 'epiano', 'warmpad']
  - pad (pad): `choir` -23 dB · rev=0.5 · alternatives ['strings', 'warmpad', 'solina']
  - arp (arp): `piano` -25 dB · pan=0.2 · rev=0.3 · alternatives ['organ', 'epiano', 'pluck']
  - lead (lead): `piano` -18 dB · rev=0.35 · alternatives ['organ', 'synthbrass', 'softlead']
- **Mix** {'lufs': -10.0, 'air': 1.8, 'low': 1.5} · reverb 2.4 · sc_depth 0.3
- **Other rules** {'sc_release': 0.5, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': True, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Choir pad; Hammond organ (Leslie) and piano; modern drums + claps; deep 808; organ or keys answering lines

## Hip-Hop

### Boom Bap (`boombap`)

Boom bap hip hop: dusty swung drums, chopped piano loops, jazzy horn lines, deep bass doubled by upright

- **Tempo** 84-96 BPM · **scales** minor, dorian · swing 0.58 (unit 16) · humanise 0.008
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 0, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.....x.X.....x.` / `X......XX.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **rim** `..............o.`
- **Drum kit** funky_drummer · preset `soft` · break chops 0.08
- **Bass** `R.....R.R.......` / `R-----..R-....A.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x--x--..x---....` / `x---..x-..x-....`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-x-..x-x-......` / `....x-x-x-x-....` / `x---x---........` / `x-------x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `sub_only` · drop `groove_drop` · variation `sectional` · culture `street` · texture `tape_degraded` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare`  dB · rev=0.15
  - chat (top): `chat` -28 dB
  - rim (top): `rim` -30 dB
  - bass (bass): `sinebass` -15 dB · alternatives ['sf:acbass', 'upright', 'moogbass']
  - bass_up (bass): `upright` -22 dB
  - chords (chords): `piano`  dB · rev=0.2 · sc=0.8 · alternatives ['epiano', 'wurli', 'organ']
  - lead (lead): `sax` -23 dB · rev=0.3 · dly=0.1 · alternatives ['flute', 'brass', 'piano']
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -10.0, 'air': -1.5, 'low': 1.5, 'lofi': True} · reverb 2.0 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True}

### G-Funk (West Coast) (`g_funk`)

G-funk (West Coast, early 90s): laid-back swung 16ths, fat Moog bass, Rhodes and string-pad chords, and the whiny high portamento synth lead floating over everything

- **Tempo** 88-100 BPM · **scales** minor, dorian · swing 0.57 (unit 16) · humanise 0.008
- **Progressions** {'minor': [[0, 3, 0, 3], [0, 5, 3, 4], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 1, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X......X..X.....` / `X.....X...X..X..` / `X......XX.X.....`; **snare** `....X.......X...`; **clap** `....X.......X...`; **chat** `x.xxx.xxx.xxx.xx` / `xxxxxxxxxxxxxxxx`; **shaker** `..x...x...x...x.`
- **Drum kit** 808 · preset `punchy`
- **Bass** `R-----..R-.R....` / `R---..R-..R-F...` / `R-----R-..R-A...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x-------x-------` / `x-----..x-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-----x-x-------` / `x-------x-x-x---`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `minimal_motivic` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `street` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -13 dB
  - snare (snare): `snare` -18 dB · rev=0.2
  - clap (snare): `clap` -21 dB · rev=0.2
  - chat (top): `chat` -29 dB · pan=0.15
  - shaker (top): `shaker` -31 dB · pan=-0.25
  - bass (bass): `moogpluck` -13 dB · alternatives ['fmbass', 'sinebass', 'sf:fingerbass']
  - chords (chords): `epiano` -22 dB · rev=0.3 · alternatives ['wurli', 'polysynth', 'organ']
  - pad (pad): `solina` -27 dB · rev=0.4 · alternatives ['strings', 'warmpad', 'glasspad']
  - lead (lead): `whine` -20 dB · pan=0.1 · rev=0.35 · dly=0.25 · alternatives ['softlead', 'polysynth', 'synthbrass', 'leadsaw']
- **Mix** {'lufs': -10.0, 'air': 1.0, 'low': 2.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 6, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.85, 'lead_glide': True}
- **Sound brief** Minimoog bass; Rhodes; string pad; high sine/saw portamento lead ("G-funk whistle"); talkbox; claps + 16th hats

### Jazz Rap (`jazz_rap`)

Jazz rap: a dusty swung break, upright bass walking under jazzy 9th-chord Rhodes and piano loops, vibraphone and muted-horn phrases - all crunched through an SP-1200

- **Tempo** 84-96 BPM · **scales** dorian, minor, major · swing 0.58 (unit 16) · humanise 0.01
- **Progressions** {'dorian': [[0, 3, 0, 3], [0, 3, 6, 2], [1, 4, 0, 0]], 'minor': [[0, 3, 6, 2], [5, 1, 4, 0]], 'major': [[1, 4, 0, 5], [3, 2, 1, 4]]} · chord_bars 1 · chord size 5
- **Song form** `lofi`: intro 4 [chords, fx] (filter_in) -> A 16 [bass, chords, fx, kick, snare, top] -> B 16 [bass, chords, fx, kick, lead, snare, top] -> C 8 [bass, chords, fx, lead] (alt) -> A 16 [bass, chords, fx, kick, lead, snare, top] -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X......X..X.....` / `X.....x...X..x..`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **rim** `..............o.`
- **Drum kit** skull_snaps · preset `soft`
- **Bass** `R...F...A...O...` / `R...A...F...R...` / `R.....R.F...A...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x--x--..x---....` / `x---..x-..x-....` / `x-------..x-----`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x-x-..x-........` / `....x-x-x-......` / `x---....x-x-....` / `........x-x-x---`
- **Build-ups** default `pause` · choices ['pause', 'drumless', 'halftime', 'tapestop', 'pickup', 'stops', 'wash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `live_drums` · melody `long_lyrical` · bass `rolling_groove` · drop `sudden` · variation `sectional` · culture `street` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `jazz_extensions` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.15
  - chat (top): `chat` -28 dB
  - rim (top): `rim` -30 dB
  - bass (bass): `upright` -14 dB · alternatives ['sf:acbass', 'sinebass', 'sf:fingerbass']
  - chords (chords): `epiano` -19 dB · rev=0.2 · alternatives ['piano', 'wurli', 'vibes']
  - arp (arp): `vibes` -25 dB · pan=0.25 · rev=0.3 · alternatives ['piano', 'epiano', 'marimba']
  - lead (lead): `trumpet` -21 dB · pan=-0.15 · rev=0.3 · dly=0.1 · alternatives ['sax', 'flute', 'vibes', 'piano']
  - vinyl (fx): `vinyl` -40 dB
- **Mix** {'lufs': -10.5, 'air': -1.0, 'low': 1.6} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'sampler': True}
- **Sound brief** Sampled jazz loop (Rhodes / piano), upright bass, vibraphone, muted trumpet or sax, dusty break, SP-1200 / MPC grit

### Mid-90s smooth rap (`smooth_90s_rap`)

Mid-90s smooth rap: a slow, laid-back bounce around 74 with a fat kick and a crisp snare, a deep round synth / bass-guitar line, sunny Rhodes and soft string-synth chords, a whistle-sine or flute melody on the hook - melodic, relaxed, made for fast melodic flows

- **Tempo** 70-80 BPM · **scales** minor, dorian, major · swing 0.56 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 3, 0, 3], [0, 6, 5, 6]], 'dorian': [[0, 3, 0, 3], [0, 1, 0, 3]], 'major': [[1, 4, 0, 5]]} · chord_bars 1 · chord size 4
- **Song form** `smooth_90s_rap`: intro 4 [chords, pad, top] -> verse 16 [bass, chords, kick, snare, top] -> hook 8 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [bass, chords, kick, snare, top] -> hook 8 [bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 4 [chords, pad, top] (alt) -> verse 16 [arp, bass, chords, kick, snare, top] -> hook 8 [bass, chords, kick, lead, pad, snare, top] (crash) -> outro 4 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X...X.X.X...X.X.` / `X.......X.....X.` / `X..X....X.X.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`; **shaker** `..x...x...x...x.`
- **Drum kit** 808 · preset `808`
- **Bass** `R--.R-.O..R-.R..` / `R---..R.R---..A.` · mode `pattern` · lowest note 29
- **Chord rhythm** `x---..x-x---....` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x---x-x-x-------` / `x-------x-x-x---`
- **Build-ups** default `(category default)` · choices ['none', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `street` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.2
  - chat (top): `chat` -27 dB · pan=0.15
  - shaker (top): `shaker` -32 dB · pan=-0.3
  - bass (bass): `moogpluck` -12 dB · alternatives ['sf:fingerbass', 'fmbass', 'sawbass']
  - chords (chords): `epiano` -22 dB · rev=0.3 · alternatives ['piano', 'wurli', 'clav']
  - pad (pad): `solina` -27 dB · rev=0.4 · alternatives ['strings', 'warmpad', 'glasspad']
  - arp (arp): `vibes` -29 dB · pan=0.25 · dly=0.2 · alternatives ['epiano', 'marimba', 'piano']
  - lead (lead): `whine` -20 dB · rev=0.3 · dly=0.25 · alternatives ['flute', 'softlead', 'talkbox']
- **Mix** {'lufs': -10.0, 'air': 0.8, 'low': 1.8} · reverb 2.0 · sc_depth 0.1
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 61, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'lead_glide': True, 'repetition': 0.8}
- **Sound brief** Slow 808 / drum-machine bounce, crisp snare; Minimoog-style bass; Rhodes; string machine; sine whistle lead

### West-coast slap rap (`bay_rap`)

West-coast slap rap (Bay Area / Sacramento): a bouncy, mid-tempo slap around 104-116 with snappy claps and snaps, a knocking kick, a rubbery, sliding 808 that bounces between two notes, plucky synths and a whistle-like lead - hard, playful and party-ready

- **Tempo** 104-116 BPM · **scales** minor, dorian, harmonic_minor · swing 0.54 (unit 16) · humanise 0.004
- **Progressions** {'minor': [[0, 0, 5, 5], [0, 5, 0, 3]], 'dorian': [[0, 3, 0, 3]], 'harmonic_minor': [[0, 0, 4, 4]]} · chord_bars 1 · chord size 3
- **Song form** `bay_rap`: intro 4 [chords, pad] -> intro 4 [bass, chords, kick] -> hook 12 [bass, chords, kick, lead, snare, top] (crash) -> break 4 [bass, kick, top] -> verse 24 [bass, chords, kick, snare, top] -> hook 12 [bass, chords, kick, lead, snare, top] (crash) -> verse 24 [arp, bass, chords, kick, snare, top] -> hook 12 [bass, chords, kick, lead, snare, top] (crash) -> outro 4 [chords] (fade) · form_scale 1
- **Drums** **kick** `X..X......X..X..` / `X.....X...X.....` / `X..X..X...X..X..`; **clap** `....X.......X...`; **snap** `....x.......x...`; **chat** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.`
- **Drum kit** 808 · preset `808`
- **Bass** `R.......R.......` · mode `808` · lowest note 28
- **Chord rhythm** `x.x...x.x...x...` / `x-x-....x-x-....`
- **Arp** {'rate': 4, 'mode': 'up', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x.x.x...x.x.....` / `x---x-x-x-------` / `x.x...x.x.x.....`
- **Build-ups** default `(category default)` · choices ['pause', 'none', 'stops'] · transitions ['gap', 'none', 'crash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `808_slide` · drop `groove_drop` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `swung_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - clap (snare): `clap` -15 dB · rev=0.15
  - snap (snare): `snap` -21 dB
  - chat (top): `chat` -26 dB · pan=0.15
  - bass (bass): `808` -10 dB · sc=0.4
  - chords (chords): `pluck` -21 dB · rev=0.2 · alternatives ['epiano', 'polysynth', 'wurli']
  - arp (arp): `pluck_saw` -28 dB · dly=0.2 · alternatives ['chip', 'pluck', 'stab']
  - lead (lead): `whine` -19 dB · rev=0.25 · dly=0.2 · alternatives ['leadsaw', 'softlead', 'talkbox']
- **Mix** {'lufs': -8.5, 'air': 1.8, 'low': 2.4, 'width': 0.6} · reverb 1.6 · sc_depth 0.2
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['clap', 'snap'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'lead_glide': True}
- **Sound brief** Slap kit: knocking kick, claps + finger snaps, 8th hats; bouncing sliding 808; plucky synth riff; whistle lead

### Futuristic hip-hop bounce (early 2000s) (`futuristic_bounce`)

Early-2000s futuristic hip-hop bounce: an off-kilter, stuttering beat around 100 with syncopated kicks, odd percussion (tabla, beatbox-like clicks and claps), a stabbing synth-bass, quirky synth riffs and reversed bits - minimal, playful and space-age

- **Tempo** 96-106 BPM · **scales** minor, phrygian, dorian · swing 0.56 (unit 16) · humanise 0.003
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 5, 6]], 'phrygian': [[0, 1, 0, 0]], 'dorian': [[0, 3, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `futuristic_bounce`: intro 8 [fx, top] -> intro 8 [bass, fx, top] -> verse 20 [bass, chords, kick, snare, top] -> hook 16 [arp, bass, chords, kick, lead, snare, top] (crash) -> verse 8 [bass, kick, snare, top] -> hook 12 [arp, bass, chords, kick, lead, snare, top] (crash) -> break 4 [bass, top] (alt) -> verse 32 [bass, chords, kick, pad, snare, top] -> break 4 [bass, top] -> hook 20 [arp, bass, chords, kick, lead, snare, top] (crash) · form_scale 1
- **Drums** **kick** `X..X.....X.X..X.` / `X...X..X..X...X.` / `X.X.....X..X.X..`; **snare** `....X.......X...` / `....X..x....X...`; **clap** `....X.......X...`; **tabla** `..x..x....x.x..x` / `x...x.x...x..x..`; **chat** `x.x.xxx.x.x.xx.x`
- **Drum kit** 808 · preset `808`
- **Bass** `R..R....R.R...R.` / `R...R..R..R...R.` · mode `pattern` · lowest note 28
- **Chord rhythm** `x..x....x.x.....` / `..x...x...x..x..`
- **Arp** {'rate': 4, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x.x..x.x..x.....` / `x..x..x.x.......`
- **Build-ups** default `(category default)` · choices ['pause', 'stops', 'none'] · transitions ['gap', 'none', 'tapestop']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `street` · texture `club_punchy` · rhythm `swung_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -15 dB · rev=0.15
  - clap (snare): `clap` -20 dB
  - tabla (top): `tabla` -24 dB · pan=0.3
  - chat (top): `chat` -28 dB · pan=-0.2
  - bass (bass): `fmbass` -11 dB · alternatives ['808', 'sawbass', 'moogbass']
  - chords (chords): `stab` -21 dB · rev=0.2 · alternatives ['pluck', 'organ', 'polysynth']
  - pad (pad): `warmpad` -29 dB · rev=0.4 · alternatives ['strings', 'glasspad', 'solina']
  - arp (arp): `chip` -27 dB · dly=0.2 · alternatives ['pluck', 'pluck_saw', 'acid']
  - lead (lead): `sitar` -20 dB · rev=0.25 · dly=0.2 · alternatives ['koto', 'whine', 'chip']
- **Mix** {'lufs': -9.0, 'air': 1.4, 'low': 2.2, 'width': 0.8} · reverb 1.4 · sc_depth 0.15
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare', 'clap'], 'bass_gate': 0.5, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True}
- **Sound brief** Stuttering 808 kit with syncopated kicks, tabla / beatbox-like percussion; stabbing synth bass; quirky riffs

### Soul-sample hip-hop (`soul_sample_rap`)

Soul-sample hip-hop (mid-2000s): a slow, heavy, swung beat around 70-90 under a looped, sped-up soul sample - warm piano / Rhodes and strings chopped into a 2- or 4-bar loop with a pitched-up vocal-like line, a thick kick, a cracking snare, a deep simple bass - one loop all the way through, verses and hooks set apart by a part or two

- **Tempo** 70-90 BPM · **scales** major, minor, dorian · swing 0.57 (unit 16) · humanise 0.007
- **Progressions** {'major': [[0, 5, 3, 4], [3, 4, 0, 0], [1, 4, 0, 5]], 'minor': [[0, 6, 5, 6], [0, 3, 6, 5]], 'dorian': [[0, 3, 0, 3]]} · chord_bars 1 · chord size 4
- **Song form** `soul_sample_rap`: intro 4 [chords, fx] -> verse 16 [bass, chords, fx, kick, snare, top] -> hook 8 [bass, chords, fx, kick, lead, pad, snare, top] -> verse 16 [bass, chords, fx, kick, snare, top] -> hook 8 [bass, chords, fx, kick, lead, pad, snare, top] -> verse 8 [arp, bass, chords, fx, kick, snare, top] (alt) -> outro 4 [chords, fx] (fade) · form_scale 1
- **Drums** **kick** `X.....x.X.......` / `X......XX.....x.`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `....x.......x...`
- **Drum kit** vintage · preset `soft`
- **Bass** `R.....R.R-......` / `R-----..R-....O.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x--x--..x---....` / `x---..x-..x-x-..`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x-x-x---x-x-....` / `..x-x-x-x-------` / `x---x---x-x-x---`
- **Build-ups** default `(category default)` · choices ['none', 'pickup'] · transitions ['none', 'none', 'crash']
- **Traits** arrangement `atmospheric_drift` · density `medium` · feel `loose_human` · melody `minimal_motivic` · bass `sub_only` · drop `groove_drop` · variation `low` · culture `street` · texture `tape_degraded` · rhythm `swung_16ths` · harmony `functional_tonal` · energy `slow_build`
- **Instruments**
  - kick (kick): `kick` -11 dB
  - snare (snare): `snare` -14 dB · rev=0.2
  - chat (top): `chat` -28 dB
  - tamb (top): `tamb` -30 dB · pan=0.3
  - bass (bass): `sinebass` -13 dB · alternatives ['moogbass', '808', 'reese']
  - chords (chords): `piano` -17 dB · rev=0.25 · alternatives ['epiano', 'wurli', 'm1piano']
  - pad (pad): `strings` -24 dB · rev=0.35 · alternatives ['choir', 'solina', 'warmpad']
  - arp (arp): `epiano` -26 dB · alternatives ['vibes', 'piano', 'pluck']
  - lead (lead): `sopsax` -19 dB · rev=0.3 · dly=0.15 · alternatives ['violin', 'sax', 'flute']
  - vinyl (fx): `vinyl` -38 dB
- **Mix** {'lufs': -9.5, 'air': -0.5, 'low': 1.8, 'width': 0.5, 'lofi': True} · reverb 1.6 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'sampler': True, 'no_rotation': True, 'repetition': 0.9}
- **Sound brief** Heavy swung boom-bap drums; a chopped soul loop (piano / Rhodes + strings, pitched up); pitched vocal-like lead; deep simple bass; vinyl

## Jazz

### Jazz (`jazz`)

Jazz / swing: walking bass, ride-cymbal swing, piano comping with extended chords

- **Tempo** 100-160 BPM · **scales** major, dorian · swing 0.66 (unit 8) · humanise 0.01
- **Progressions** {'major': [[1, 4, 0, 0], [1, 4, 0, 5], [0, 5, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 4, 0, 3]]} · chord_bars 1 · chord size 5
- **Song form** `jazz`: intro 4 [bass, chords, top] -> head 16 [bass, chords, kick, lead, snare, top] -> solo 16 [bass, chords, kick, lead, snare, top] (alt) -> solo 16 [arp, bass, chords, kick, snare, top] -> head 16 [bass, chords, kick, lead, snare, top] -> outro 4 [bass, chords, top] (fade) · form_scale 1.75
- **Drums** **ride** `x...x.x.x...x.x.`; **chat** `....x.......x...`; **kick** `o...o...o...o...`; **snare** `................`
- **Drum kit** brushes · preset `acoustic`
- **Bass** `R.......R.......` · mode `walk` · lowest note 28
- **Chord rhythm** `x-....x-........` / `...x-.....x-....` / `x-.....x-.......`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x.x.x.x.x---....` / `..x.x-x.x.x-....` / `x-.xx-x.x---x...` / `x---x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `walking` · drop `groove_drop` · variation `theme_and_variations` · culture `jazz_club` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - ride (top): `ride` -27 dB · pan=0.3
  - chat (top): `chat` -29 dB · pan=-0.2
  - kick (kick): `kick` -29 dB
  - snare (snare): `snare` -26 dB
  - bass (bass): `upright` -20 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `piano` -18 dB · rev=0.2 · alternatives ['epiano', 'guitar', 'organ', 'vibes', 'wurli']
  - arp (arp): `piano` -22 dB · rev=0.2 · alternatives ['guitar', 'epiano', 'vibes']
  - lead (lead): `brass` -16 dB · rev=0.25 · alternatives ['sax', 'sf:tenorsax', 'sf:mutedtrumpet', 'piano', 'guitar', 'flute', 'clarinet', 'trumpet', 'vibes']
- **Mix** {'lufs': -14.0, 'air': 1.0, 'low': 0.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'comp_snare': True}

### Bebop (`bebop`)

Bebop: fast swing, dense 8th-note lines built from chord tones, tensions and chromatic approach notes over rapid ii-V changes; ride and walking bass drive, piano comps rootless voicings

- **Tempo** 180-260 BPM · **scales** major, minor · swing 0.62 (unit 8) · humanise 0.007
- **Progressions** {'major': [[1, 4, 0, 0], [2, 5, 1, 4], [1, 4, 2, 5], [0, 5, 1, 4]], 'minor': [[1, 4, 0, 0], [0, 3, 1, 4]]} · chord_bars 1 · chord size 4
- **Song form** `jazz`: intro 4 [bass, chords, top] -> head 16 [bass, chords, kick, lead, snare, top] -> solo 16 [bass, chords, kick, lead, snare, top] (alt) -> solo 16 [arp, bass, chords, kick, snare, top] -> head 16 [bass, chords, kick, lead, snare, top] -> outro 4 [bass, chords, top] (fade) · form_scale 1
- **Drums** **ride** `x...x.x.x...x.x.`; **chat** `....x.......x...`; **kick** `o...o...o...o...`; **snare** `................`
- **Drum kit** brushes · preset `default`
- **Bass** `R.......R.......` · mode `walk` · lowest note 36
- **Chord rhythm** `...x-.....x-....` / `.x-.....x-..x-..` / `......x-..x-....`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x.x.x.x.` / `x.x.x.x.x.x.x-..` / `..x.x.x.x.x.x.x.` / `x.x.x.x.x-..x.x.`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `sparse` · feel `loose_human` · melody `virtuosic` · bass `walking` · drop `groove_drop` · variation `theme_and_variations` · culture `jazz_club` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - ride (top): `ride` -26 dB · pan=0.3
  - chat (top): `chat` -30 dB · pan=-0.2
  - kick (kick): `kick` -24 dB
  - snare (snare): `snare` -24 dB · rev=0.2
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `piano` -23 dB · pan=-0.15 · rev=0.2 · alternatives ['guitar', 'epiano', 'wurli']
  - lead (lead): `sax` -17 dB · rev=0.25 · alternatives ['sf:tenorsax', 'trumpet', 'sf:trumpet']
- **Mix** {'lufs': -14.0, 'air': 1.2, 'low': 0.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'rootless', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'comp_snare': True}

### Cool / Modal Jazz (`modal_jazz`)

Cool / modal jazz (late-50s): long stretches on one mode, medium tempo, lots of space, quartal-ish piano voicings, muted trumpet and tenor sax, brushes and ride, walking bass

- **Tempo** 110-150 BPM · **scales** dorian, mixolydian, lydian · swing 0.6 (unit 8) · humanise 0.008
- **Progressions** {'dorian': [[0, 0, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]], 'mixolydian': [[0, 0, 0, 0], [0, 0, 6, 6]], 'lydian': [[0, 0, 1, 1]]} · chord_bars 2 · chord size 4
- **Song form** `jazz`: intro 4 [bass, chords, top] -> head 16 [bass, chords, kick, lead, snare, top] -> solo 16 [bass, chords, kick, lead, snare, top] (alt) -> solo 16 [arp, bass, chords, kick, snare, top] -> head 16 [bass, chords, kick, lead, snare, top] -> outro 4 [bass, chords, top] (fade) · form_scale 1
- **Drums** **ride** `x...x.x.x...x.x.`; **chat** `....x.......x...`; **kick** `o.......o.......`; **snare** `................`
- **Drum kit** brushes · preset `default`
- **Bass** `R.......R.......` · mode `walk` · lowest note 36
- **Chord rhythm** `x-......x-......` / `...x-.......x-..` / `x-..........x-..`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---....x---` / `....x-x-x---x---` / `x-------x-x-x---`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `sparse` · feel `loose_human` · melody `call_and_response` · bass `walking` · drop `groove_drop` · variation `theme_and_variations` · culture `jazz_club` · texture `intimate_close` · rhythm `swung_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - ride (top): `ride` -27 dB · pan=0.3
  - chat (top): `chat` -31 dB · pan=-0.2
  - kick (kick): `kick` -26 dB
  - snare (snare): `snare` -26 dB · rev=0.2
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `piano` -24 dB · pan=-0.15 · rev=0.25 · alternatives ['epiano', 'wurli', 'm1piano']
  - lead (lead): `trumpet` -18 dB · rev=0.3 · alternatives ['sax', 'sf:tenorsax', 'flute']
- **Mix** {'lufs': -15.0, 'air': 1.0, 'low': 0.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'comp_snare': True, 'repetition': 0.6}

### Soul Jazz / Hard Bop (`soul_jazz`)

Hard bop / soul jazz: organ trio grooves - Hammond B3 comping and bass, bluesy guitar and tenor sax, gospel-tinged harmony, hard swing or straight-8th backbeat

- **Tempo** 100-140 BPM · **scales** dorian, mixolydian, minor · swing 0.6 (unit 8) · humanise 0.007
- **Progressions** {'dorian': [[0, 3, 0, 3], [0, 0, 3, 3]], 'mixolydian': [[0, 3, 0, 4], [0, 0, 3, 0]], 'minor': [[0, 3, 0, 4]]} · chord_bars 1 · chord size 4
- **Song form** `jazz`: intro 4 [bass, chords, top] -> head 16 [bass, chords, kick, lead, snare, top] -> solo 16 [bass, chords, kick, lead, snare, top] (alt) -> solo 16 [arp, bass, chords, kick, snare, top] -> head 16 [bass, chords, kick, lead, snare, top] -> outro 4 [bass, chords, top] (fade) · form_scale 1
- **Drums** **kick** `X.....X...X.....`; **snare** `....X.......X...`; **ride** `x...x.x.x...x.x.`; **chat** `....x.......x...`
- **Drum kit** seventies · preset `default`
- **Bass** `R.......R.......` · mode `walk` · lowest note 33
- **Chord rhythm** `.x-...x-.x-...x-` / `x-..x-..x-..x-..` / `...x-..x-..x-...`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x-..x.x.x---` / `x-x-x.x.x-......` / `..x.x.x-x.x.x---`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `call_and_response` · bass `walking` · drop `groove_drop` · variation `theme_and_variations` · culture `jazz_club` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -20 dB
  - snare (snare): `snare` -20 dB · rev=0.15
  - ride (top): `ride` -27 dB · pan=0.3
  - chat (top): `chat` -30 dB · pan=-0.2
  - bass (bass): `organ` -16 dB · alternatives ['organbass', 'upright', 'sf:acbass']
  - chords (chords): `organ` -22 dB · pan=-0.2 · rev=0.2 · alternatives ['epiano', 'piano', 'wurli']
  - arp (arp): `guitar` -26 dB · pan=0.3 · alternatives ['mutedgtr', 'piano', 'sf:cleanguitar']
  - lead (lead): `sax` -17 dB · rev=0.25 · alternatives ['sf:tenorsax', 'guitar', 'organ']
- **Mix** {'lufs': -13.0, 'air': 1.2, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'melody_style': 'blues'}

### Jazz Fusion (`fusion`)

Jazz fusion / jazz-rock: straight 16th-note grooves, electric bass, Rhodes and synth leads, overdriven guitar, extended chords and virtuosic unison lines over a rock / funk rhythm section

- **Tempo** 96-140 BPM · **scales** dorian, mixolydian, lydian, minor · swing 0.5 (unit 16) · humanise 0.005
- **Progressions** {'dorian': [[0, 3, 6, 2], [0, 6, 3, 4]], 'mixolydian': [[0, 6, 3, 0], [0, 3, 6, 6]], 'lydian': [[0, 1, 0, 1], [0, 1, 4, 5]], 'minor': [[0, 5, 3, 4], [0, 3, 6, 4]]} · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X..x..X...X..x..` / `X.x...X..x..X...`; **snare** `....X..o....X..o`; **chat** `xxxxxxxxxxxxxxxx`; **ohat** `......x.......x.`; **ride** `x.x.x.x.x.x.x.x.`
- **Drum kit** studio · preset `default`
- **Bass** `R.RO.R.OR.R.O.RA` / `R..R.O.RR.R..O.R` / `R.R.O.R.R.R.O.RA` · mode `pattern` · lowest note 31
- **Chord rhythm** `x--.x--.x--.x--.` / `.x-..x-..x-..x-.` / `x-..x-..x-..x---`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x.x.x.x.` / `x.xxx.x.x.xxx.x.` / `x-x-x-x-x.x.x---`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `virtuosic` · bass `rolling_groove` · drop `groove_drop` · variation `theme_and_variations` · culture `jazz_club` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - snare (snare): `snare` -18 dB · rev=0.15
  - chat (top): `chat` -29 dB · pan=0.2
  - ohat (top): `ohat` -30 dB
  - ride (top): `ride` -31 dB · pan=0.3
  - bass (bass): `ebass` -14 dB · alternatives ['sf:fingerbass', 'sf:pickbass', 'moogbass']
  - chords (chords): `epiano` -22 dB · pan=-0.2 · rev=0.25 · alternatives ['wurli', 'polysynth', 'piano']
  - pad (pad): `polysynth` -30 dB · rev=0.4 · alternatives ['warmpad', 'solina', 'synthbrass']
  - arp (arp): `guitar` -27 dB · pan=0.3 · alternatives ['sf:odguitar', 'mutedgtr', 'piano']
  - lead (lead): `leadsaw` -18 dB · rev=0.3 · dly=0.2 · alternatives ['guitar', 'sax', 'softlead']
- **Mix** {'lufs': -12.0, 'air': 1.6, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'drop2', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Smooth Jazz (soprano sax) (`smooth_jazz`)

Smooth jazz, soprano-sax ballad style: a soprano sax soaring up high in long held notes with wide vibrato, scooping into every phrase, over lush 80s DX electric piano and pads, a warm fretless bass and soft, reverb-washed drums - romantic, slow and polished, with a key change for the last chorus

- **Tempo** 64-92 BPM · **scales** major · swing 0.52 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 3, 1, 4], [0, 5, 3, 4], [3, 4, 2, 5], [0, 2, 3, 4], [5, 3, 0, 4], [1, 4, 0, 0]]} · chord_bars 1 · chord size 5
- **Song form** `song_b`: intro 8 [chords, pad] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> pre 4 [bass, chords, pad, snare, top] (build) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [arp, chords, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad] (fade) · form_scale 1
- **Drums** **kick** `X.........X.....` / `X......X..X.....`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **shaker** `x.x.x.x.x.x.x.x.`
- **Drum kit** studio · preset `soft`
- **Bass** `R-------R---F---` / `R-----..R-F-....` / `R---..R-R---A---` · mode `pattern` · lowest note 28
- **Chord rhythm** `x---------------` / `x-------x-------` / `x-----..x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4, 'prob': 0.3}
- **Lead rhythm** `x---------x-x-x-` / `x-------x---x---` / `....x-x-x-------` / `x-----x-x-------` / `x---------------`
- **Build-ups** default `lift` · choices ['lift', 'pickup', 'toms', 'ride', 'stops', 'tomgroove', 'march', 'claps']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `theme_and_variations` · culture `jazz_club` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -18 dB
  - snare (snare): `snare` -22 dB · rev=0.6
  - chat (top): `chat` -31 dB · pan=0.2
  - shaker (top): `shaker` -31 dB · pan=-0.3
  - bass (bass): `sf:fingerbass` -15 dB · alternatives ['moogbass', 'ebass', 'upright']
  - chords (chords): `epiano` -19 dB · pan=-0.1 · rev=0.45 · dly=0.12 · alternatives ['piano', 'polysynth', 'wurli']
  - pad (pad): `glasspad` -26 dB · rev=0.6 · alternatives ['warmpad', 'strings', 'solina']
  - arp (arp): `acguitar` -27 dB · pan=0.3 · rev=0.4 · alternatives ['vibes', 'piano', 'epiano']
  - lead (lead): `sopsax` -15 dB · rev=0.55 · dly=0.18 · alternatives ['sax', 'flute', 'acguitar']
- **Mix** {'lufs': -12.5, 'air': 1.8, 'low': 1.0} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.55, 'own_progs': True, 'solo_lead': True, 'repetition': 0.8}
- **Sound brief** Soprano sax (lots of vibrato); DX7 "E.Piano 1"; lush poly pads / strings; fretless bass; soft drum machine + big reverb snare

## Swing & Big Band

### Big Band Swing (`swing`)

Big-band swing: walking bass, ride and hi-hat on 2 & 4, brass section shouts, a sax solo

- **Tempo** 110-160 BPM · **scales** major, minor · swing 0.66 (unit 8) · humanise 0.01
- **Progressions** {'major': [[0, 5, 1, 4], [1, 4, 0, 0], [0, 3, 1, 4], [2, 5, 1, 4]], 'minor': [[0, 3, 4, 0], [0, 5, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `jazz`: intro 4 [bass, chords, top] -> head 16 [bass, chords, kick, lead, snare, top] -> solo 16 [bass, chords, kick, lead, snare, top] (alt) -> solo 16 [arp, bass, chords, kick, snare, top] -> head 16 [bass, chords, kick, lead, snare, top] -> outro 4 [bass, chords, top] (fade) · form_scale 1.5
- **Drums** **ride** `x...x.x.x...x.x.`; **chat** `....x.......x...`; **kick** `o...o...o...o...`; **snare** `................` / `.......x......x.`
- **Drum kit** brushes · preset `acoustic`
- **Bass** `R.......R.......` · mode `walk` · lowest note 28
- **Chord rhythm** `x-....x-........` / `...x-.....x-....` / `x-..x-..x-..x-..` / `....x-.....x-...`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x.x.x.x.x---....` / `..x.x-x.x.x-....` / `x-.xx-x.x---x...` / `x---x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `long_lyrical` · bass `walking` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - ride (top): `ride` -23 dB · pan=0.3
  - chat (top): `chat` -29 dB · pan=-0.2
  - kick (kick): `kick` -24 dB
  - snare (snare): `snare` -25 dB
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `brass` -21 dB · rev=0.25 · alternatives ['sf:trumpetsection', 'piano', 'sax']
  - arp (arp): `piano` -26 dB · pan=0.25 · rev=0.2 · alternatives ['guitar', 'vibes', 'epiano']
  - lead (lead): `sax` -18 dB · rev=0.25 · alternatives ['sf:tenorsax', 'brass', 'sf:trumpet', 'sf:mutedtrumpet', 'clarinet', 'sf:trombone', 'trumpet', 'vibes']
- **Mix** {'lufs': -13.0, 'air': 1.2, 'low': 0.6} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'comp_snare': True}
- **Sound brief** Brass section (trumpets + trombones); Saxophones; Piano; Upright bass (walking); Ride cymbal

### Western Swing (`western_swing`)

Western swing / Texas swing: swung country dance band - twin fiddles, pedal steel, sixth-chord piano and guitar comping, walking upright bass, brushed swing drums

- **Tempo** 110-160 BPM · **scales** major, mixolydian · swing 0.66 (unit 8) · humanise 0.008
- **Progressions** {'major': [[0, 5, 1, 4], [0, 3, 0, 4], [0, 0, 1, 4], [2, 5, 1, 4]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......`; **snare** `....X.......X...`; **ride** `x..xx..xx..xx..x`
- **Drum kit** brushes · preset `soft`
- **Bass** `R...F...A...O...` / `R...A...F...O...` · mode `pattern` · lowest note 31
- **Chord rhythm** `....x.......x...` / `..x...x...x...x.`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.45}
- **Lead rhythm** `x-x-x-x-x---....` / `x.x.x.x.x-x-x---` / `x---x-x-x-x-x---` / `x-x-x---x-x-x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -20 dB
  - snare (snare): `snare` -22 dB · rev=0.25
  - ride (top): `ride` -27 dB
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `piano` -22 dB · pan=0.2 · rev=0.2 · alternatives ['guitar', 'sf:cleanguitar', 'epiano']
  - pad (pad): `pedalsteel` -25 dB · pan=-0.25 · rev=0.4 · alternatives ['organ', 'strings', 'accordion']
  - lead (lead): `violin` -17 dB · pan=-0.1 · rev=0.3 · alternatives ['sf:fiddle', 'pedalsteel', 'twang', 'sax', 'clarinet']
  - lead2 (lead): `violin` -21 dB · pan=0.15 · rev=0.3
- **Mix** {'lufs': -12.0, 'air': 1.2, 'low': 0.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.35}
- **Sound brief** Twin fiddles (harmony); pedal steel; piano; rhythm guitar; upright bass; brushes / ride

### Swing-era big band (hot, tom-tom) (`swing_tomtom`)

Swing-era big band (hot, tom-tom drive): a fast 1930s flag-waver in a minor key driven by the floor-tom groove, riffing trumpets and trombones, the sax section answering, a hot clarinet lead, a drum break and a roaring shout chorus

- **Tempo** 100-120 BPM · **scales** minor, dorian, harmonic_minor · swing 0.64 (unit 8) · humanise 0.008
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 3, 3], [0, 3, 4, 0]], 'dorian': [[0, 0, 3, 0]], 'harmonic_minor': [[0, 0, 4, 0], [0, 3, 4, 0]]} · chord_bars 1 · chord size 4
- **Song form** `hotswing`: intro 4 [kick, snare, top] -> head 16 [bass, chords, kick, lead, snare, top] (crash) -> solo 16 [bass, chords, kick, lead, snare, top] -> break 8 [kick, snare, top] -> solo 16 [bass, chords, kick, lead, pad, snare, top] (alt) -> head 16 [bass, chords, kick, lead, pad, snare, top] (crash, var=oct) -> outro 4 [bass, chords, kick, snare, top] (cad, chord_rh=X.......X-------) · form_scale 1
- **Drums** **tom** `X.x.X.x.X.x.X.x.` / `X.x.X.xxX.x.X.x.` / `X.xxX.x.X.xxX.x.`; **kick** `o...o...o...o...`; **chat** `....x.......x...`; **ride** `x...x.x.x...x.x.`; **crash** `X...............` / `................`
- **Drum kit** studio · preset `acoustic`
- **Bass** `R...R...F...R...` / `R...F...R...A...` · mode `walk` · lowest note 31
- **Chord rhythm** `X.x...X.x...X...` / `..X.x...X.x.....` / `X-x-X-x-X-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x-x.x---` / `x-x.x.x-x.x.x.x.` / `xxx.x.x-x---x.x.` / `x.x-x.x.x.x-x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `loose_human` · melody `rhythmic_stabs` · bass `walking` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - tom (kick role - the genre's low drum): `tom` -15 dB · rev=0.3
  - kick (kick): `kick` -24 dB
  - chat (top): `chat` -30 dB
  - ride (top): `ride` -30 dB · pan=0.3
  - crash (top): `crash` -27 dB · rev=0.3
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `brass` -20 dB · rev=0.3 · alternatives ['sf:trumpetsection', 'synthbrass', 'horn']
  - saxes (chords): `sax` -24 dB · pan=-0.25 · rev=0.3
  - pad (pad): `sax` -26 dB · pan=0.2 · rev=0.35 · alternatives ['brass', 'sf:tenorsax', 'clarinet']
  - arp (arp): `piano` -27 dB · pan=-0.3 · rev=0.3 · alternatives ['epiano', 'vibes', 'harp']
  - lead (lead): `clarinet` -17 dB · rev=0.35 · alternatives ['trumpet', 'sax', 'trombone']
  - solo_tpt (lead): `trumpet` -17 dB · rev=0.35
- **Mix** {'lufs': -13.0, 'air': 0.6, 'low': 0.8} · reverb 1.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['tom'], 'bass_gate': 0.8, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'tom', 'suggest': '', 'no_rotation': True, 'repetition': 0.75, 'solos': ['solo_tpt', 'lead'], 'drum_voice': {'tom': {'pitch': 92}}}
- **Sound brief** Floor tom groove; upright walking bass; trumpet & trombone riffs; sax section; clarinet lead; piano

### 50s big band (brassy, smooth) (`big_band_50s`)

50s big band (brassy and smooth): a medium-up swinging chart in a major key - walking bass, ride cymbal and hi-hat on 2 and 4, piano comping, a warm sax section, punchy trumpet and trombone hits that build to a shout chorus and a big final chord

- **Tempo** 120-150 BPM · **scales** major · swing 0.64 (unit 8) · humanise 0.006
- **Progressions** {'major': [[0, 5, 1, 4], [1, 4, 0, 5], [0, 3, 1, 4], [2, 5, 1, 4]]} · chord_bars 1 · chord size 4
- **Song form** `chart`: intro 4 [bass, chords, kick, pad, snare, top] -> head 16 [arp, bass, chords, kick, lead, pad, snare, top] -> head 16 [arp, bass, chords, kick, lead, pad, snare, top] -> solo 16 [arp, bass, chords, kick, lead, snare, top] (alt) -> shout 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash, var=oct, drop) -> head 8 [arp, bass, chords, kick, lead, pad, snare, top] (cad) -> outro 4 [bass, chords, kick, pad, snare, top] (cad, chord_rh=X-------X-------) · form_scale 1
- **Drums** **ride** `x...x.x.x...x.x.`; **chat** `....x.......x...`; **kick** `o...o...o...o...`; **snare** `................` / `.......x......x.` / `......x.......x.`; **crash** `X...............` / `................`
- **Drum kit** studio · preset `acoustic`
- **Bass** `R...R...F...R...` / `R...F...R...A...` · mode `walk` · lowest note 31
- **Chord rhythm** `..X.......X.....` / `X.....X...X.....` / `......X.X.......` / `X-------........`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 5, 'prob': 0.35}
- **Lead rhythm** `x-x.x.x-x---....` / `x---x-x-x-x-x---` / `..x-x.x-x-x-....` / `x-x-x---x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `loose_human` · melody `long_lyrical` · bass `walking` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - ride (top): `ride` -27 dB · pan=0.3
  - chat (top): `chat` -30 dB · pan=-0.2
  - kick (kick): `kick` -24 dB
  - snare (snare): `snare` -22 dB · rev=0.2
  - crash (top): `crash` -27 dB · rev=0.3
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `brass` -20 dB · rev=0.3 · alternatives ['sf:trumpetsection', 'synthbrass', 'horn']
  - bones (chords): `trombone` -23 dB · pan=0.25 · rev=0.3
  - pad (pad): `sax` -24 dB · pan=-0.2 · rev=0.35 · alternatives ['strings', 'brass', 'sf:tenorsax']
  - arp (arp): `piano` -26 dB · pan=0.3 · rev=0.25 · alternatives ['vibes', 'epiano', 'harp']
  - lead (lead): `trumpet` -17 dB · rev=0.35 · alternatives ['sax', 'sf:trumpet', 'clarinet']
  - solo_sax (lead): `sax` -17 dB · rev=0.35
- **Mix** {'lufs': -12.0, 'air': 1.0, 'low': 0.6} · reverb 1.8 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.85, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'no_rotation': True, 'comp_snare': True, 'repetition': 0.7, 'solos': ['solo_sax']}
- **Sound brief** Ride + hi-hat on 2 & 4; walking upright bass; piano comping; sax section pads; trumpets & trombones punches and shouts; trumpet / sax leads

## Country, Folk & Blues

### Blues (`blues`)

Blues shuffle: 12-bar form, swung grooves, piano, organ and expressive lead guitar

- **Tempo** 80-120 BPM · **scales** mixolydian · swing 0.66 (unit 8) · humanise 0.008
- **Progressions** [[0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4], [0, 3, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4]] · chord_bars 1 · chord size 4
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......`; **snare** `....X.......X...`; **ride** `x...x.x.x...x.x.`; **chat** `....x.......x...`
- **Drum kit** seventies · preset `acoustic`
- **Bass** `R.......R.......` · mode `walk` · lowest note 28
- **Chord rhythm** `x-.x-.x-.x-.x-.x` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 4, 'prob': 0.6}
- **Lead rhythm** `x.x.x-....x.x---` / `..x-x-x-x-------` / `x-.xx-x.x---....` / `x---x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `live_drums` · melody `long_lyrical` · bass `walking` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `triplet_feel` · harmony `modal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - snare (snare): `snare`  dB · rev=0.2
  - ride (top): `ride` -25 dB
  - chat (top): `chat` -29 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'sf:acbass', 'sf:pickbass']
  - chords (chords): `piano`  dB · rev=0.2 · alternatives ['organ', 'guitar', 'wurli']
  - pad (pad): `organ` -26 dB · rev=0.25 · alternatives ['brass', 'strings', 'warmpad']
  - arp (arp): `guitar` -26 dB · pan=0.3 · alternatives ['piano', 'mutedgtr', 'sf:cleanguitar']
  - lead (lead): `guitar`  dB · rev=0.3 · alternatives ['sf:odguitar', 'sax', 'sf:tenorsax', 'organ', 'piano', 'brass', 'harmonica']
- **Mix** {'lufs': -12.0, 'air': 1.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': True, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Folk (`folk`)

Folk / acoustic: strummed guitar, warm piano, gentle percussion, flute melody

- **Tempo** 80-116 BPM · **scales** major, mixolydian, minor · swing 0.5 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 0, 4], [0, 5, 3, 4]], 'mixolydian': [[0, 6, 3, 0]], 'minor': [[0, 6, 5, 6], [0, 3, 6, 0]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......`; **tamb** `....X.......X...`; **shaker** `x.x.x.x.x.x.x.x.`
- **Drum kit** studio · preset `soft`
- **Bass** `R.......F.......` / `R...F...R...A...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.x.xxx.x.x.xxx.` / `x--x--x-x--x--x-`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x-x-x---....` / `x-x-x---x-------` / `..x-x-x-x---x---` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -19 dB
  - tamb (snare): `tamb` -23 dB
  - shaker (top): `shaker` -29 dB
  - bass (bass): `upright` -17 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `acguitar`  dB · rev=0.2 · alternatives ['guitar', 'sf:nylon', 'piano', 'harp']
  - pad (pad): `strings` -27 dB · rev=0.4 · alternatives ['sf:slowstrings', 'organ', 'solina']
  - arp (arp): `piano` -26 dB · rev=0.3 · alternatives ['guitar', 'sf:nylon', 'harp']
  - lead (lead): `flute`  dB · rev=0.35 · alternatives ['violin', 'clarinet', 'oboe', 'guitar', 'sf:nylon', 'piano', 'harmonica']
- **Mix** {'lufs': -13.0, 'air': 1.0, 'low': 0.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['tamb'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.012, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Spaghetti Western (`western`)

Spaghetti western: twangy reverb guitar, lonely trumpet, whistled tune, choir and galloping hooves

- **Tempo** 88-120 BPM · **scales** minor, harmonic_minor, dorian · swing 0.5 (unit 16) · humanise 0.01
- **Progressions** {'minor': [[0, 6, 5, 6], [0, 3, 0, 4], [0, 5, 6, 0], [0, 6, 0, 4]], 'harmonic_minor': [[0, 3, 4, 0], [0, 5, 4, 0]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......`; **snare** `....x.......x...`; **woodblock** `x.xxx.xxx.xxx.xx` / `x..xx..xx..xx..x`; **tom** `..............xx`
- **Drum kit** vintage · preset `soft`
- **Bass** `R-------F-------` / `R...F...R...F...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x--x--x-x--x--x-` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4, 'prob': 0.6}
- **Lead rhythm** `x-------x---x---` / `x---x-x-x-------` / `x-----x-x-------` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -19 dB
  - snare (snare): `snare` -23 dB · rev=0.4
  - woodblock (top): `woodblock` -27 dB · pan=0.3
  - tom (top): `tom` -24 dB · rev=0.4
  - bass (bass): `upright` -17 dB · alternatives ['sf:acbass', 'cello', 'sf:fingerbass']
  - chords (chords): `guitar`  dB · pan=-0.2 · rev=0.45 · dly=0.25 · alternatives ['sf:cleanguitar', 'sf:nylon', 'harp']
  - pad (pad): `choir` -25 dB · rev=0.55 · alternatives ['strings', 'tremolo', 'organ', 'pedalsteel']
  - arp (arp): `guitar` -26 dB · pan=0.3 · rev=0.6 · alternatives ['harp', 'sf:nylon', 'pizz']
  - lead (lead): `brass` -18 dB · rev=0.5 · dly=0.25 · alternatives ['trumpet', 'softlead', 'guitar', 'choir']
- **Mix** {'lufs': -12.0, 'air': 1.0, 'low': 0.8} · reverb 3.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 57, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Twangy electric guitar (lots of spring reverb); Trumpet / whistle melody; Choir; Woodblock hooves

### Celtic Jig (6/8) (`celtic_jig`)

Celtic jig (6/8): fiddle and tin whistle in unison on an AABB tune, bodhrán, bouncing guitar, a soft pipe drone

- **Tempo** 104-124 BPM · meter 6/8 · **scales** major, mixolydian, dorian · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 3, 4, 0], [0, 4, 0, 4], [0, 0, 3, 4], [0, 5, 3, 4]], 'mixolydian': [[0, 6, 0, 6], [0, 3, 6, 0]], 'dorian': [[0, 6, 0, 6], [0, 3, 0, 6]]} · chord_bars 1 · chord size 3
- **Song form** `jig`: A 8 [bass, chords, kick, lead, snare, top] -> A 8 [bass, chords, kick, lead, pad, snare, top] (cad) -> B 8 [bass, chords, kick, lead, pad, snare, top] (alt) -> B 8 [arp, bass, chords, kick, lead, pad, snare, top] (alt, cad) -> A 8 [arp, bass, chords, kick, lead, pad, snare, top] -> A 8 [arp, bass, chords, kick, lead, pad, snare, top] (cad) -> B 8 [arp, bass, chords, kick, lead, pad, snare, top] (alt) -> B 8 [arp, bass, chords, kick, lead, pad, snare, top] (alt, cad) · form_scale 1
- **Drums** **bodhran** `X.xX.xX.xX.x` / `X..X.xX..X.x` / `X.xx.xX.xX.x`; **tip** `..x..x..x..x` / `.....x.....x`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R.....F.....` / `R..F..R..F..` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.xx.xx.xx.x` / `x..x..x..x..`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `xxxxxxxxxxxx` / `x-xx-xx-xx-x` / `xxx-xxxxx-x-` / `x-xxxxx-xx-x`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `emotional_swell` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - bodhran (kick role - the genre's low drum): `bodhran` -17 dB · rev=0.2
  - tip (snare): `bodhran` -24 dB · rev=0.2
  - bass (bass): `upright` -18 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `acguitar` -22 dB · pan=-0.25 · rev=0.25 · alternatives ['guitar', 'sf:nylon', 'harp', 'accordion']
  - pad (pad): `drone` -30 dB · rev=0.3 · alternatives ['accordion', 'organ', 'pipes']
  - arp (arp): `harp` -27 dB · pan=0.3 · rev=0.3 · alternatives ['guitar', 'banjo', 'mandolin']
  - lead (lead): `violin` -17 dB · pan=-0.1 · rev=0.3 · alternatives ['tinwhistle', 'pipes', 'sf:fiddle', 'accordion', 'flute']
  - whistle (lead): `tinwhistle` -20 dB · pan=0.15 · rev=0.3
- **Mix** {'lufs': -12.0, 'air': 1.4, 'low': 0.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['tip'], 'bass_gate': 0.7, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'bodhran', 'suggest': '', 'pad_drone': True, 'drum_voice': {'tip': {'pitch': 140, 'decay': 16}}, 'no_rotation': True}
- **Sound brief** Fiddle / tin whistle (tune); Bodhran; Acoustic guitar or bouzouki; Upright bass

### Country (classic / honky-tonk) (`country`)

Classic country / honky-tonk (Nashville, Bakersfield): boom-chick upright bass with walk-ups, strummed acoustic, chicken-pickin' Telecaster, honky-tonk piano fills, fiddle melody and pedal-steel swells and slides

- **Tempo** 92-132 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 3, 4, 0], [0, 4, 3, 0], [0, 0, 3, 4], [0, 5, 3, 4], [3, 0, 4, 0]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X...X...X...X...`; **snare** `....X.......X...` / `oxoxXxoxoxoxXxox`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** studio · preset `soft`
- **Bass** `R...F...R...F...` / `R...F...R.F.A...` / `R...F...R...A.F.` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x...x.x.x...x.x.` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4, 'prob': 0.5}
- **Lead rhythm** `x-x-x---x-x-....` / `x---x-x-x---....` / `x-x-x-x-x---x...` / `..x-x-x-x---....`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - snare (snare): `snare` -19 dB · rev=0.25
  - chat (top): `chat` -28 dB
  - bass (bass): `upright` -16 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `acguitar`  dB · pan=-0.25 · rev=0.2 · alternatives ['piano', 'banjo', 'sf:nylon']
  - arp (arp): `twang` -24 dB · pan=0.3 · rev=0.3 · dly=0.12 · alternatives ['acguitar', 'banjo', 'sf:banjo']
  - keys (chords): `piano` -26 dB · pan=0.15 · rev=0.25
  - pad (pad): `pedalsteel` -25 dB · pan=0.2 · rev=0.4 · alternatives ['organ', 'strings', 'accordion']
  - lead (lead): `violin` -18 dB · rev=0.3 · alternatives ['sf:fiddle', 'twang', 'pedalsteel', 'harmonica', 'piano']
- **Mix** {'lufs': -11.0, 'air': 1.5, 'low': 0.9} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.55, 'chord_center': 57, 'strum': 0.012, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.45}
- **Sound brief** Acoustic steel guitar (strum); Telecaster licks; Fiddle; Pedal steel; Upright / electric bass; Pedal steel swells

### Bluegrass (`bluegrass`)

Bluegrass: Scruggs banjo rolls, the mandolin chop on 2 and 4, boom-chick guitar with G-runs, fiddle and the band taking breaks in turn

- **Tempo** 112-150 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 3, 4, 0], [0, 0, 3, 0], [0, 4, 0, 4], [0, 3, 0, 4]], 'mixolydian': [[0, 6, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `bluegrass`: intro 4 [bass, chords, lead] -> head 16 [arp, bass, chords, lead] -> solo 16 [bass, chords, lead] -> solo 16 [arp, bass, chords, lead] -> head 16 [arp, bass, chords, lead] -> solo 16 [bass, chords, lead] -> head 16 [arp, bass, chords, lead] (cad) -> outro 4 [bass, chords, lead] (cad) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R...F...R...F...` / `R...F...R...A...` · mode `pattern` · lowest note 31
- **Chord rhythm** `....x.......x...` / `....x.......x..x`
- **Arp** {'rate': 1, 'mode': 'roll', 'oct': 4}
- **Lead rhythm** `x.x.x.x.x.x.x.x.` / `x.x.x-x.x.x.x---` / `xx.x.x.xx.x.x.x.` / `x-x-x-x-x.x.x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `sparse` · feel `tight_swing` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `none` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - bass (bass): `upright` -16 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `mandolin` -22 dB · pan=0.3 · rev=0.12 · alternatives ['banjo', 'acguitar', 'sf:steelguitar']
  - gtr (chords): `acguitar` -24 dB · pan=-0.3 · rev=0.15
  - arp (arp): `banjo` -23 dB · pan=-0.15 · rev=0.12 · alternatives ['sf:banjo', 'mandolin', 'acguitar']
  - lead (lead): `violin` -17 dB · rev=0.25 · alternatives ['sf:fiddle', 'harmonica', 'mandolin']
  - solo_banjo (lead): `banjo` -19 dB · pan=-0.15 · rev=0.15
  - solo_mando (lead): `mandolin` -19 dB · pan=0.25 · rev=0.15
  - solo_gtr (lead): `acguitar` -19 dB · pan=-0.2 · rev=0.15
- **Mix** {'lufs': -12.0, 'air': 1.5, 'low': 0.6} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'solos': ['solo_banjo', 'solo_mando', 'lead', 'solo_gtr'], 'g_run': True, 'no_rotation': True}
- **Sound brief** Banjo (rolls); Fiddle (lead); Mandolin chop; Acoustic guitar; Upright bass

### Modern Country (`modern_country`)

Modern country / Nashville pop: big clean drums, driving 16th acoustic strum, electric bass on the root, twangy Telecaster riffs and pedal-steel swells, a big singalong chorus

- **Tempo** 76-108 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 4, 0], [5, 3, 0, 4], [0, 3, 5, 4], [3, 0, 4, 5]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.X.....` / `X.....X.X.......`; **snare** `....X.......X...`; **chat** `x.x.x.x.x.x.x.x.`; **tamb** `....x.......x...`
- **Drum kit** unruly · preset `punchy`
- **Bass** `R.R.R.R.R.R.R.R.` / `R...R...R...F...` / `R.....R.R...F...` · mode `pattern` · lowest note 31
- **Chord rhythm** `x.xxx.xxx.xxx.xx` / `x.x.x.xxx.x.x.xx`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4, 'prob': 0.55}
- **Lead rhythm** `x-x-x---x-x-....` / `x---x-x-x---....` / `..x-x-x-x---x---` / `x---x---x-x-x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -14 dB
  - snare (snare): `snare` -17 dB · rev=0.3
  - chat (top): `chat` -28 dB
  - tamb (top): `tamb` -29 dB · pan=0.3
  - bass (bass): `sf:fingerbass` -15 dB · alternatives ['upright', 'moogbass', 'ebass']
  - chords (chords): `acguitar`  dB · pan=-0.25 · rev=0.2 · alternatives ['piano', 'sf:nylon', 'sf:steelguitar']
  - pad (pad): `pedalsteel` -25 dB · pan=0.25 · rev=0.45 · alternatives ['organ', 'strings', 'accordion']
  - arp (arp): `twang` -24 dB · pan=0.3 · rev=0.3 · dly=0.15 · alternatives ['acguitar', 'banjo', 'piano']
  - lead (lead): `twang` -19 dB · rev=0.3 · dly=0.15 · alternatives ['pedalsteel', 'violin', 'sf:fiddle', 'harmonica']
- **Mix** {'lufs': -10.0, 'air': 1.8, 'low': 1.4} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 57, 'strum': 0.01, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.4}
- **Sound brief** Acoustic steel guitar (16th strum); Telecaster; pedal steel; electric bass; big clean kit; piano / B3 pads

### Country Waltz (3/4) (`country_waltz`)

Country waltz (3/4, 50s honky-tonk ballad): a slow oom-pah-pah of upright bass and strummed guitar, brushed drums, weeping fiddle and pedal steel trading the melody, honky-tonk piano

- **Tempo** 84-112 BPM · meter 3/4 · **scales** major · swing 0.5 (unit 16) · humanise 0.01
- **Progressions** {'major': [[0, 3, 4, 0], [0, 0, 4, 4], [0, 3, 0, 4], [0, 5, 1, 4]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X...........`; **snare** `....x...x...` / `....x...x.x.`
- **Drum kit** brushes · preset `soft`
- **Bass** `R.....F.....` / `R.....F...A.` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x.x...x.x.` / `..x-x---x-x-`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-x-x---` / `x-----x---x-` / `x---------x-` / `x-x-x-x-----`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -20 dB
  - snare (snare): `snare` -24 dB · rev=0.3
  - bass (bass): `upright` -16 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `acguitar`  dB · pan=-0.2 · rev=0.25 · alternatives ['piano', 'sf:nylon', 'sf:steelguitar']
  - keys (chords): `piano` -27 dB · pan=0.2 · rev=0.25
  - pad (pad): `pedalsteel` -24 dB · pan=0.25 · rev=0.45 · alternatives ['organ', 'strings', 'accordion']
  - lead (lead): `violin` -17 dB · rev=0.35 · alternatives ['sf:fiddle', 'pedalsteel', 'harmonica', 'twang']
- **Mix** {'lufs': -13.0, 'air': 1.2, 'low': 0.8} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.6, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.5}
- **Sound brief** Fiddle; pedal steel; acoustic guitar; upright bass; brushes; honky-tonk piano

### Outlaw Country (`outlaw_country`)

Outlaw country: the freight-train boom-chicka-boom - palm-muted guitar on every 8th, slapback twang and a low baritone guitar melody, steady upright bass, brushed snare, harmonica

- **Tempo** 100-140 BPM · **scales** major, mixolydian, minor · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'major': [[0, 3, 4, 0], [0, 0, 3, 4], [0, 4, 0, 4]], 'mixolydian': [[0, 6, 0, 3], [0, 6, 3, 0]], 'minor': [[0, 5, 0, 4], [0, 3, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X...X...X...X...`; **snare** `oxoxXxoxoxoxXxox` / `x.x.X.x.x.x.X.x.`
- **Drum kit** studio · preset `soft`
- **Bass** `R...F...R...F...` / `R...F...R.F.A...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `xxxxxxxxxxxxxxxx`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 4, 'prob': 0.6}
- **Lead rhythm** `x---x-x-x---....` / `x-x-x---x-------` / `x---x---x-x-....`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -18 dB
  - snare (snare): `snare` -21 dB · rev=0.2
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `mutedgtr` -21 dB · pan=-0.2 · rev=0.15 · alternatives ['acguitar', 'sf:cleanguitar', 'clav']
  - pad (pad): `harmonica` -27 dB · pan=0.3 · rev=0.35 · alternatives ['organ', 'pedalsteel', 'strings']
  - lead (lead): `twang` -18 dB · rev=0.25 · dly=0.12 · alternatives ['guitar', 'harmonica', 'violin']
- **Mix** {'lufs': -11.0, 'air': 1.0, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.25, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.5, 'chord_center': 55, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slides': 0.4}
- **Sound brief** Palm-muted acoustic ("boom-chicka"); baritone / Telecaster with slapback; upright bass; brushes; harmonica

### Acoustic folk-rock jam (`folk_jam`)

Laid-back acoustic folk-rock jam (early-70s American style): strummed acoustic guitars and mandolin, a melodic walking bass, brushes-and-tambourine drums, a gentle singing lead and harmonies feel - one long warm groove that slowly fills out, no breakdowns

- **Tempo** 100-116 BPM · **scales** major, mixolydian · swing 0.54 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 3, 0, 4], [0, 3, 4, 0], [0, 4, 3, 0]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `folk_jam`: intro 4 [chords] -> verse 16 [bass, chords, kick, top] -> chorus 8 [bass, chords, kick, lead, snare, top] -> verse 16 [arp, bass, chords, kick, snare, top] -> chorus 8 [bass, chords, kick, lead, pad, snare, top] -> solo 16 [arp, bass, chords, kick, lead, snare, top] (alt) -> verse 16 [arp, bass, chords, kick, pad, snare, top] -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [bass, chords, lead] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X.....X.X.......`; **snare** `....X.......X...`; **tamb** `..x...x...x...x.`; **shaker** `x.x.x.x.x.x.x.x.`
- **Drum kit** brushes · preset `soft`
- **Bass** `R...F...R...F...` / `R...A...F...R.A.` · mode `walk` · lowest note 31
- **Chord rhythm** `x.x.xxx.x.x.xxx.` / `x--x--x-x--x--x-`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x---x-x-x---....` / `x-x-x---x-------`
- **Build-ups** default `(category default)` · choices ['pickup', 'none'] · transitions ['none', 'none', 'crash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `walking` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - snare (snare): `snare` -19 dB · rev=0.2
  - tamb (top): `tamb` -27 dB · pan=0.3
  - shaker (top): `shaker` -31 dB · pan=-0.3
  - bass (bass): `ebass` -16 dB · alternatives ['upright', 'sf:fingerbass', 'sf:pickbass']
  - chords (chords): `acguitar` -17 dB · rev=0.25 · alternatives ['sf:nylon', 'sf:steelguitar', 'piano']
  - pad (pad): `organ` -28 dB · rev=0.3 · alternatives ['strings', 'warmpad', 'solina']
  - arp (arp): `mandolin` -24 dB · pan=0.3 · rev=0.25 · alternatives ['banjo', 'acguitar', 'sf:steelguitar']
  - lead (lead): `guitar` -20 dB · rev=0.3 · alternatives ['organ', 'pedalsteel', 'harmonica']
- **Mix** {'lufs': -12.5, 'air': 1.0, 'low': 0.6, 'width': 1.0, 'gentle': True} · reverb 1.8 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.014, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}
- **Sound brief** Strummed acoustic guitars + mandolin; melodic bass; brushed drums + tambourine; a gentle lead (organ / guitar)

## Latin & Caribbean

### Reggae (`reggae`)

Reggae one-drop: offbeat skank chords, melodic bass, laid-back drums

- **Tempo** 70-90 BPM · **scales** major, minor · swing 0.55 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 3, 0, 4], [0, 4, 3, 3]], 'minor': [[0, 3, 0, 3], [0, 6, 5, 6]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `........X.......`; **rim** `........X.......`; **chat** `x.x.x.x.x.x.x.x.`; **snare** `................`
- **Drum kit** seventies · preset `acoustic`
- **Bass** `R---..R.F-..A...` / `..R-R-..F---R...` / `R-..R...F.R.A...` · mode `pattern` · lowest note 28
- **Chord rhythm** `..x...x...x...x.` / `..x-..x-..x-..x-`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-x-x-------` / `..x-x-x-x---....` / `x-------x---x---` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `sub_only` · drop `groove_drop` · variation `sectional` · culture `carnival` · texture `dry_and_upfront` · rhythm `swung_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick`  dB
  - rim (snare): `rim` -20 dB · rev=0.3
  - chat (top): `chat` -28 dB
  - snare (snare): `snare` -22 dB · rev=0.3
  - bass (bass): `sinebass` -13 dB · alternatives ['sf:fingerbass', 'ebass', 'moogbass']
  - chords (chords): `organ`  dB · pan=-0.2 · rev=0.2 · alternatives ['guitar', 'piano', 'epiano']
  - arp (arp): `guitar` -26 dB · pan=0.3 · dly=0.3 · alternatives ['sf:muted', 'organ', 'mutedgtr']
  - lead (lead): `softlead`  dB · rev=0.3 · dly=0.3 · alternatives ['flute', 'brass', 'sax', 'organ', 'sf:trumpet', 'trumpet', 'harmonica']
- **Mix** {'lufs': -11.0, 'air': 1.0, 'low': 2.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'dub': 0.55, 'dub_beats': 0.75, 'spring': True}

### Bossa Nova (`bossa_nova`)

Bossa nova: gentle syncopated nylon guitar, rim clicks, soft bass and flute

- **Tempo** 116-148 BPM · **scales** major, dorian · swing 0.52 (unit 16) · humanise 0.01
- **Progressions** {'major': [[1, 4, 0, 0], [0, 5, 1, 4], [3, 2, 1, 4]], 'dorian': [[0, 3, 0, 3], [0, 4, 0, 3]]} · chord_bars 1 · chord size 5
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **rim** `x..x..x...x..x..`; **shaker** `xoxoxoxoxoxoxoxo`; **kick** `X.....x.X.....x.`
- **Drum kit** brushes · preset `soft`
- **Bass** `R.....F.R.....F.` / `R-....F-R-....F-` · mode `pattern` · lowest note 31
- **Chord rhythm** `x..x..x...x..x..` / `..x..x....x..x..` / `x..x..x...x..x..`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.5}
- **Lead rhythm** `x---x-x-x---....` / `..x-x-x-x-------` / `x-------x---x---` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `carnival` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `jazz_extensions` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -20 dB
  - rim (snare): `rim` -22 dB
  - shaker (top): `shaker` -29 dB · pan=0.3
  - bass (bass): `upright` -16 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `acguitar`  dB · rev=0.2 · alternatives ['guitar', 'sf:nylon', 'piano', 'epiano', 'vibes', 'wurli']
  - pad (pad): `strings` -28 dB · rev=0.4 · alternatives ['warmpad', 'organ', 'solina']
  - arp (arp): `piano` -27 dB · rev=0.25 · alternatives ['guitar', 'sf:nylon', 'vibes']
  - lead (lead): `flute`  dB · rev=0.35 · dly=0.15 · alternatives ['sax', 'clarinet', 'piano', 'sf:nylon', 'vibes']
- **Mix** {'lufs': -14.0, 'air': 1.0, 'low': 0.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['rim'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': ''}

### Ska (`ska`)

Ska: offbeat guitar & organ skank, fast walking bass, rimshot backbeat, punchy horn lines

- **Tempo** 120-164 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 5, 1, 4], [0, 3, 4, 0], [0, 4, 3, 4]], 'minor': [[0, 3, 0, 4], [0, 5, 6, 4]]} · chord_bars 1 · chord size 3
- **Song form** `song`: intro 4 [chords, top] (filter_in) -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, pad, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> bridge 8 [bass, chords, lead, pad] (alt) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 8 [chords, pad, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......` / `X...X...X...X...`; **snare** `....X.......X...`; **rim** `....x.......x...`; **chat** `x.x.x.x.x.x.x.x.`
- **Drum kit** studio · preset `acoustic`
- **Bass** `R.R.R.R.F.F.A.A.` / `R...R...F...A...` / `R.R.F.F.R.R.A.A.` · mode `pattern` · lowest note 28
- **Chord rhythm** `..x...x...x...x.` / `..x.x.x.x.x.x.x.`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x-x-x---x-x-x---` / `x.x.x-x.x---....` / `x---x-x-x-------` / `x-.x-.x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `carnival` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - snare (snare): `snare`  dB · rev=0.25
  - rim (snare): `rim` -22 dB
  - chat (top): `chat` -28 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'sinebass', 'moogbass']
  - chords (chords): `guitar` -22 dB · pan=-0.25 · alternatives ['sf:cleanguitar', 'organ', 'piano', 'mutedgtr']
  - pad (pad): `organ` -27 dB · pan=0.25 · alternatives ['brass', 'warmpad', 'strings']
  - lead (lead): `brass` -18 dB · rev=0.25 · alternatives ['sf:trumpet', 'sax', 'sf:trombone', 'organ', 'trumpet']
- **Mix** {'lufs': -10.5, 'air': 1.4, 'low': 1.0} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'dub': 0.25, 'dub_beats': 0.5, 'spring': True}
- **Sound brief** Clean guitar skank; Organ (offbeats); Bass guitar; Trumpet + trombone + sax horns

### Salsa (`salsa`)

Salsa: clave and cowbell, conga tumbao, piano montuno, anticipated bass and a blazing trumpet section

- **Tempo** 84-104 BPM · **scales** minor, major, harmonic_minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 3, 4, 0], [0, 3, 6, 4], [0, 5, 3, 4]], 'major': [[0, 3, 4, 3], [0, 4, 0, 4], [1, 4, 0, 0]], 'harmonic_minor': [[0, 3, 4, 0], [0, 4, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `salsa`: intro 8 [arp, bass, kick, lead, top] -> verse 16 [arp, bass, chords, kick, snare, top] -> montuno 16 [arp, bass, chords, kick, lead, snare, top] (crash) -> mambo 16 [arp, bass, chords, kick, lead, snare, top] (crash, alt, var=oct) -> montuno 16 [arp, bass, chords, kick, lead, snare, top] (crash) -> coda 4 [bass, chords, kick, snare, top] (cad, chord_rh=X..X..X...X.....) · form_scale 1
- **Drums** **woodblock** `x..x..x...x.x...`; **cowbell808** `x.x.x.x.x.x.x.x.`; **conga** `..o.x..o..o.x..o` / `x.o.x.ox..o.x.o.`; **kick** `...X.......X....`; **rim** `............x...`; **guiro** `x..xx..xx..xx..x`; **bongo** `x.xxx.xxx.xxx.xx`; **paila** `x.xx.x.xx.x.x.x.`; **timb_hi** `................` / `..............xx`; **timb_lo** `............X...` / `...........xX...`
- **Drum kit** (synth preset) · preset `acoustic`
- **Bass** `......R.....R...` / `......R.....R..R` / `...R..R.....R...` / `......F.....R...` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.....x...x.....` / `..x...x..x..x...` / `x..x..x.........`
- **Arp** {'rate': 1, 'mode': 'montuno', 'oct': 4, 'rh': ['x.xx.x.xx.x.x.x.', '.x.x.xx..x.x.xx.']}
- **Lead rhythm** `x-x-x---x-x-x---` / `x.x.x.x.x---....` / `x-.x-.x-x-------` / `..x.x-x.x.x-....`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `tight_swing` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `carnival` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - woodblock (top): `woodblock` -26 dB · pan=0.25
  - cowbell808 (top): `cowbell808` -30 dB · pan=-0.25
  - conga (top): `conga` -23 dB · pan=0.3
  - kick (kick): `kick` -22 dB
  - rim (snare): `rim` -24 dB
  - bass (bass): `upright` -15 dB · alternatives ['sf:acbass', 'sf:fingerbass']
  - chords (chords): `brass` -23 dB · rev=0.25 · alternatives ['sf:trumpetsection', 'piano', 'synthbrass']
  - arp (arp): `piano` -21 dB · pan=-0.15 · rev=0.2 · alternatives ['epiano', 'vibes', 'marimba']
  - lead (lead): `brass` -17 dB · rev=0.25 · alternatives ['sf:trumpetsection', 'sf:trumpet', 'sf:trombone', 'flute', 'sax', 'violin', 'trumpet']
  - guiro (top): `shaker` -27 dB · pan=0.35
  - bongo (top): `conga` -26 dB · pan=-0.35
  - paila (top): `timbale` -29 dB · pan=0.2
  - timb_hi (snare): `timbale` -22 dB · pan=0.25 · rev=0.15
  - timb_lo (snare): `timbale` -21 dB · pan=0.15 · rev=0.15
- **Mix** {'lufs': -11.0, 'air': 1.5, 'low': 0.9} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['rim'], 'bass_gate': 0.92, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'real_cowbell': True, 'drum_voice': {'paila': {'paila': 1}, 'timb_hi': {'pitch': 560}, 'timb_lo': {'pitch': 410}}, 'no_rotation': True}
- **Sound brief** Piano montuno; Trumpets + trombones; Congas, timbales, cowbell, clave; Baby bass (anticipated)

### Cumbia (`cumbia`)

Cumbia: guira scrape and congas, kick on one and three, offbeat guitar, accordion melodies

- **Tempo** 84-104 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'minor': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 6, 5, 4]], 'major': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 4, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `cumbia`: intro 4 [bass, chords, kick, top] -> A 16 [bass, chords, kick, lead, snare, top] -> B 16 [arp, bass, chords, kick, lead, snare, top] (crash) -> A 16 [bass, chords, kick, lead, snare, top] -> solo 16 [bass, chords, kick, lead, snare, top] (alt) -> B 16 [arp, bass, chords, kick, lead, snare, top] (crash) -> outro 8 [bass, chords, kick, lead, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X.......X.......`; **shaker** `x.xxx.xxx.xxx.xx`; **conga** `..o...ox..o...ox` / `......ox......o.`; **rim** `....x.......x...`; **cowbell808** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R...F...R...F...` / `R..RF...R..RF...` / `R...F..RR...F...` · mode `pattern` · lowest note 28
- **Chord rhythm** `..x...x...x...x.` / `..xx..xx..xx..xx`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x-x-x---x-x-x---` / `x.x.x.x.x-x-x---` / `x---x-x-x-------` / `..x-x-x-x---x---`
- **Build-ups** default `(category default)` · choices ['pickup', 'none'] · transitions ['none', 'none', 'crash']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `carnival` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -17 dB
  - shaker (top): `shaker` -25 dB · pan=0.3
  - conga (top): `conga` -23 dB · pan=-0.25
  - rim (snare): `rim` -24 dB
  - cowbell808 (top): `cowbell808` -32 dB
  - bass (bass): `ebass` -15 dB · alternatives ['sf:fingerbass', 'sinebass', 'sf:pickbass']
  - chords (chords): `guitar` -23 dB · pan=-0.2 · alternatives ['sf:cleanguitar', 'organ', 'accordion', 'mutedgtr']
  - arp (arp): `marimba` -27 dB · pan=0.3 · alternatives ['guitar', 'flute', 'vibes']
  - lead (lead): `accordion` -18 dB · rev=0.25 · alternatives ['sf:accordion', 'flute', 'organ', 'brass', 'guitar', 'trumpet']
- **Mix** {'lufs': -11.0, 'air': 1.3, 'low': 1.2} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['rim'], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'real_cowbell': True}
- **Sound brief** Accordion (melody); Guira / shaker; Congas & timbales; Guitar (offbeats); Bass

### Tango (`tango`)

Tango: the marcato four and the 3-3-2 síncopa, bandoneon, dramatic violin, staccato piano and double bass, A-B-A with the chan-chan ending

- **Tempo** 108-132 BPM · **scales** harmonic_minor, minor · swing 0.5 (unit 16) · humanise 0.01
- **Progressions** {'harmonic_minor': [[0, 3, 4, 0], [0, 5, 3, 4], [0, 4, 0, 4], [3, 4, 0, 0]], 'minor': [[0, 3, 6, 2]]} · chord_bars 1 · chord size 3
- **Song form** `tango`: intro 4 [bass, chords] (level=0.6) -> A 8 [arp, bass, chords, lead] (level=1.0) -> B 8 [chords, lead, pad] (alt, level=0.55, level_to=0.7) -> A 8 [arp, bass, chords, lead, pad] (level=1.0) -> C 8 [bass, lead, pad] (alt, level=0.5) -> A 16 [arp, bass, chords, lead, pad] (cad, level=0.9, level_to=1.0) -> coda 2 [bass, chords] (cad, chord_rh=X.......X.......) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R...R...R...R...` / `R..R..R.R...R...` / `R..R..R.R..R..R.` · mode `pattern` · lowest note 28
- **Chord rhythm** `X...x...X...x...` / `X..X..X.X...x...` / `X..X..X.X..X..X.` / `X...x...X..x.x..`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.4}
- **Lead rhythm** `x---x-x-x---x---` / `x-x-x-x-x-------` / `x-----x-x-x-x---` / `x--x--x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `sparse` · feel `loose_human` · melody `call_and_response` · bass `rolling_groove` · drop `none` · variation `sectional` · culture `carnival` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - bass (bass): `cello` -18 dB · rev=0.25 · alternatives ['sf:contrabass', 'ebass', 'contrabass']
  - chords (chords): `piano` -21 dB · rev=0.25 · alternatives ['accordion', 'strings', 'epiano']
  - pad (pad): `bandoneon` -23 dB · rev=0.3 · alternatives ['accordion', 'strings', 'solina']
  - arp (arp): `pizz` -27 dB · pan=0.3 · rev=0.25 · alternatives ['piano', 'harp', 'spiccato']
  - lead (lead): `violin` -17 dB · rev=0.35 · alternatives ['bandoneon', 'accordion', 'sf:fiddle']
- **Mix** {'lufs': -13.0, 'air': 1.2, 'low': 0.7} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.45, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'no_rotation': True}
- **Sound brief** Bandoneon; Violins; Piano (marcato); Double bass

### Soca / calypso (`soca`)

Soca / calypso (Trinidad carnival): fast four-on-the-floor with the soca snare and iron (brake drum) driving the offbeats, a bouncing syncopated bass, steel pan melodies and chords, brass hits and bright synths - pure jump-up

- **Tempo** 150-162 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'major': [[0, 4, 0, 4], [0, 3, 4, 0], [0, 5, 3, 4], [3, 4, 0, 0]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `soca`: intro 4 [bass, chords, kick, snare, top] -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> chorus 16 [arp, bass, chords, kick, lead, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 4 [bass, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `...x..x....x..x.` / `...x..x...xx..x.`; **cowbell808** `..x...x...x...x.` / `x.x.x.x.x.x.x.x.`; **chat** `x.xxx.xxx.xxx.xx`; **conga** `..o.x..o..o.x..o`; **tamb** `....x.......x...`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R..R..R...R.R...` / `R..R..R.R..R..R.` / `...R..R....R..R.` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x...x...x...x.` / `.x.x.x.x.x.x.x.x`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.8}
- **Lead rhythm** `x-x-x-x-x-x-x---` / `x.x.x.x.x-x-x---` / `x-xxx-x-x-x-----` / `x.x.x---x.x.x---`
- **Build-ups** default `(category default)` · choices ['pickup', 'stops'] · transitions ['crash', 'none']
- **Traits** arrangement `verse_chorus_pop` · density `dense` · feel `tight_swing` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `carnival` · texture `club_punchy` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -18 dB · rev=0.15
  - cowbell808 (top): `cowbell808` -26 dB · pan=0.25
  - chat (top): `chat` -29 dB · pan=-0.2
  - conga (top): `conga` -27 dB · pan=-0.3
  - tamb (top): `tamb` -30 dB · pan=0.3
  - bass (bass): `sawbass` -14 dB · sc=0.6 · alternatives ['fmbass', 'ebass', 'moogbass']
  - chords (chords): `steeldrum` -22 dB · pan=-0.2 · rev=0.25 · alternatives ['brass', 'polysynth', 'pluck_saw']
  - horns (chords): `brass` -23 dB · rev=0.2
  - pad (pad): `synthbrass` -28 dB · rev=0.3 · alternatives ['strings', 'warmpad', 'solina']
  - arp (arp): `steeldrum` -25 dB · pan=0.3 · rev=0.25 · dly=0.2 · alternatives ['marimba', 'pluck_saw', 'vibes']
  - lead (lead): `steeldrum` -17 dB · rev=0.3 · alternatives ['brass', 'trumpet', 'leadsaw']
- **Mix** {'lufs': -9.0, 'air': 1.8, 'low': 1.2} · reverb 1.6 · sc_depth 0.25
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.6, 'chord_center': 64, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'real_cowbell': True, 'no_rotation': True}
- **Sound brief** Steel pan (lead & chords); iron / brake drum; soca kit; syncopated synth bass; brass section; bright synths

### Groovy soca (`groovy_soca`)

Groovy soca (Trinidad carnival, slower lane): a rolling four-on-the-floor around 115-132 with the iron / brake-drum bell on the off-beats, a smooth syncopated bass, warm synth and steel-pan chords, brass hits and a sweet vocal-style hook - made for wining and swaying rather than jumping

- **Tempo** 114-132 BPM · **scales** major, mixolydian, minor · swing 0.52 (unit 16) · humanise 0.004
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 4, 0], [3, 4, 0, 0]], 'mixolydian': [[0, 6, 3, 0]], 'minor': [[0, 5, 6, 0]]} · chord_bars 1 · chord size 4
- **Song form** `soca`: intro 4 [bass, chords, kick, snare, top] -> verse 16 [bass, chords, kick, snare, top] -> chorus 16 [bass, chords, kick, lead, snare, top] (crash) -> verse 16 [arp, bass, chords, kick, snare, top] -> chorus 16 [arp, bass, chords, kick, lead, snare, top] (crash) -> chorus 16 [arp, bass, chords, kick, lead, pad, snare, top] (crash) -> outro 4 [bass, kick, snare, top] (fade) · form_scale 1
- **Drums** **kick** `X...X...X...X...`; **snare** `...x..x....x..x.` / `....x.......x...`; **cowbell808** `..x...x...x...x.`; **chat** `x.xxx.xxx.xxx.xx`; **conga** `..o.x..o..o.x..o`; **shaker** `.x.x.x.x.x.x.x.x`
- **Drum kit** (synth preset) · preset `punchy`
- **Bass** `R..R..R...R.R...` / `R...R..R..R..R..` / `R..R...RR..R....` · mode `pattern` · lowest note 31
- **Chord rhythm** `..x...x...x...x.` / `x..x..x...x..x..`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x-x-x---` / `..x-x-x-x-------`
- **Build-ups** default `(category default)` · choices ['pickup', 'stops', 'pause']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `tight_swing` · melody `call_and_response` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `carnival` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `peaks_and_valleys`
- **Instruments**
  - kick (kick): `kick` -12 dB
  - snare (snare): `snare` -18 dB · rev=0.15
  - cowbell808 (top): `cowbell808` -27 dB · pan=0.25
  - chat (top): `chat` -29 dB · pan=-0.2
  - conga (top): `conga` -27 dB · pan=-0.3
  - shaker (top): `shaker` -31 dB · pan=0.3
  - bass (bass): `moogpluck` -13 dB · sc=0.5 · alternatives ['sawbass', 'fmbass', 'sf:fingerbass']
  - chords (chords): `polysynth` -22 dB · pan=-0.2 · rev=0.3 · alternatives ['steeldrum', 'epiano', 'synthbrass']
  - pad (pad): `warmpad` -28 dB · rev=0.4 · alternatives ['strings', 'synthbrass', 'glasspad']
  - arp (arp): `steeldrum` -24 dB · pan=0.3 · rev=0.25 · dly=0.2 · alternatives ['marimba', 'pluck', 'vibes']
  - lead (lead): `brass` -19 dB · rev=0.3 · alternatives ['steeldrum', 'trumpet', 'softlead']
- **Mix** {'lufs': -9.5, 'air': 1.6, 'low': 1.4} · reverb 1.8 · sc_depth 0.3
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 63, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'real_cowbell': True}
- **Sound brief** Soca kit with iron bell; smooth syncopated synth bass; steel pan + warm synth chords; brass hits; sweet lead

## World

### Raga (sitar, tabla, tanpura) (`raga_fusion`)

Raga (Hindustani-inspired): a tanpura drone the whole way, the sitar alone in a slow free alap with sliding meend, then a pulse, then the tabla enters for the gat in a 16-beat teental and the music speeds into a jhala climax

- **Tempo** 84-112 BPM · **scales** phrygian_dominant, mixolydian, harmonic_minor, dorian · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'phrygian_dominant': [[0, 0, 0, 0], [0, 1, 0, 0]], 'mixolydian': [[0, 0, 0, 0], [0, 0, 6, 0]], 'harmonic_minor': [[0, 0, 0, 0], [0, 0, 4, 0]], 'dorian': [[0, 0, 0, 0], [0, 0, 3, 0]]} · chord_bars 4 · chord size 3
- **Song form** `raga`: alap 8 [lead, pad] (filter_in) -> jor 8 [bass, lead, pad] -> gat 16 [bass, kick, lead, pad, snare, top] -> gat 16 [arp, bass, kick, lead, pad, snare, top] (alt) -> jhala 8 [arp, bass, kick, lead, pad, snare, top] (drop, cad) · form_scale 1
- **Drums** **tabla** `X.x.x.X.X.x.x.X.` / `X.xxx.X.X.x.x.Xx` / `X.x.x.x.X.x.xxX.`; **bayan** `X.....X.X.....X.` / `X.....X.......X.`
- **Drum kit** (synth preset) · preset `soft`
- **Bass** `R-------........` · mode `pattern` · lowest note 36
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x-------x-x-x---` / `x---x---x---x---` / `x-x-x-x-x-x-x-x-` / `x---x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `virtuosic` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `dry_and_upfront` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - bayan (kick role - the genre's low drum): `bayan` -17 dB · rev=0.25
  - tabla (snare): `tabla` -18 dB · rev=0.25
  - bass (bass): `tanpura` -22 dB · alternatives ['drone', 'cello', 'sinebass']
  - pad (pad): `tanpura` -21 dB · rev=0.4 · alternatives ['drone', 'strings', 'warmpad']
  - arp (arp): `sitar` -27 dB · pan=-0.25 · rev=0.4 · alternatives ['harp', 'koto', 'mandolin']
  - lead (lead): `sitar` -17 dB · rev=0.4 · alternatives ['flute', 'violin', 'oboe']
- **Mix** {'lufs': -13.0, 'air': 1.2, 'low': 0.8} · reverb 2.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['tabla'], 'bass_gate': 0.9, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'bayan', 'suggest': '', 'pad_drone': True, 'repetition': 0.6, 'melody_lang': 'diatonic', 'slides': 0.35, 'no_rotation': True}
- **Sound brief** Tanpura drone; sitar (meend, jawari buzz); tabla (dayan + bayan); a low drone bass

### Japanese zen (koto, shakuhachi) (`japanese_zen`)

Japanese zen / traditional-inspired: koto plucks and pressed bends, a breathy shakuhachi-style flute, a soft taiko and wood blocks, lots of space - calm, modal and spacious

- **Tempo** 66-84 BPM · **scales** phrygian, minor · swing 0.5 (unit 16) · humanise 0.01
- **Progressions** {'phrygian': [[0, 1, 0, 0], [0, 0, 5, 1], [0, 6, 1, 0]], 'minor': [[0, 5, 0, 3], [0, 0, 5, 0]]} · chord_bars 2 · chord size 3
- **Song form** `arch`: intro 4 [arp, pad] (filter_in, arp={'rate': 0.5, 'mode': 'updown'}) -> A 8 [bass, chords, lead, pad] -> B 8 [arp, bass, lead, pad] (alt, arp={'rate': 0.5, 'mode': 'updown', 'oct': 5}) -> A 8 [arp, bass, chords, lead, pad] -> outro 4 [arp, pad] (fade, arp={'rate': 1, 'mode': 'updown'}) · form_scale 1
- **Drums** **taiko** `X...............` / `X.......x.......`; **woodblock** `....x.......x...` / `......x.......x.`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` · mode `pattern` · lowest note 36
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x-------x---....` / `x---x-------....` / `x-------........` / `x-x-x---x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `verse_chorus_pop` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `groove_drop` · variation `sectional` · culture `radio_pop` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `static_vamp` · energy `peaks_and_valleys`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -18 dB · rev=0.4
  - woodblock (snare): `woodblock` -27 dB · rev=0.4
  - bass (bass): `koto` -22 dB · alternatives ['harp', 'pizz', 'cello']
  - chords (chords): `koto` -21 dB · pan=-0.2 · rev=0.4 · alternatives ['harp', 'pizz', 'kalimba']
  - pad (pad): `strings` -30 dB · rev=0.6 · alternatives ['warmpad', 'solina', 'sf:slowstrings']
  - arp (arp): `koto` -25 dB · pan=0.25 · rev=0.5 · alternatives ['harp', 'kalimba', 'marimba']
  - lead (lead): `flute` -18 dB · rev=0.5 · alternatives ['koto', 'tinwhistle', 'oboe']
- **Mix** {'lufs': -14.0, 'air': 1.2, 'low': 0.6} · reverb 3.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['woodblock'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': '', 'repetition': 0.7, 'no_rotation': True}
- **Sound brief** Koto; shakuhachi; taiko; wood block; a quiet string pad

# Orchestral

## Film & Trailer

### Cinematic / Epic (`cinematic`)

Epic cinematic / trailer: string ostinatos, taiko & timpani, horns, choir, huge climax

- **Tempo** 80-110 BPM · **scales** minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** [[0, 5, 2, 6], [0, 5, 3, 4], [0, 3, 5, 4], [0, 6, 5, 6]] · chord_bars 1 · chord size 3
- **Song form** `cinematic`: intro 8 [chords, fx, pad] (filter_in) -> rise 8 [arp, bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare] (drop) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, fx, pad] (fade) · form_scale 1
- **Drums** **taiko** `X.....x.X...x.x.` / `X..x..x.X.x.x...`; **snare** `....x.......x...`; **timp** `X.......X.......`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.R.R.R.R.R.R.R.` / `R-------R-------` · mode `pattern` · lowest note 28
- **Chord rhythm** `x-x-x-x-x-x-x-x-` / `xxxxxxxxxxxxxxxx`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-----x-x-------` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `cinematic_score` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -13 dB · rev=0.3
  - snare (snare): `snare` -22 dB · rev=0.4
  - timp (snare): `timp` -19 dB · rev=0.4
  - bass (bass): `strings` -17 dB · rev=0.3 · alternatives ['cello', 'sf:contrabass', 'spiccato']
  - chords (chords): `spiccato` -21 dB · rev=0.35 · alternatives ['strings', 'tremolo', 'pizz']
  - pad (pad): `choir` -22 dB · rev=0.5 · alternatives ['horn', 'strings', 'braam', 'tremolo']
  - arp (arp): `pizz` -24 dB · pan=-0.3 · rev=0.3 · alternatives ['spiccato', 'harp', 'celesta']
  - lead (lead): `horn` -18 dB · rev=0.45 · alternatives ['brass', 'violin', 'choir', 'cello', 'sf:trumpet', 'trumpet']
  - texture (fx): `texture` -38 dB · rev=0.5
- **Mix** {'lufs': -11.0, 'air': 1.5, 'low': 1.5} · reverb 3.5 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': '', 'slow_chords': 0.35}
- **Sound brief** Strings: violins 1/2, violas (ostinato); Celli/Basses; French horns (theme); Choir; Taiko & timpani

### Film Piano (`film_piano`)

Emotional film score: solo piano theme over warm strings, celesta sparkles

- **Tempo** 64-84 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.015
- **Progressions** {'major': [[0, 4, 5, 3], [5, 3, 0, 4], [0, 5, 3, 4]], 'minor': [[0, 5, 2, 6], [0, 3, 5, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4}
- **Lead rhythm** `x---x---x-------` / `x-x-x---x---x---` / `....x---x---x---` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `long_lyrical` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `cinematic_score` · texture `intimate_close` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `strings` -21 dB · rev=0.4 · alternatives ['cello', 'contrabass', 'sf:bassoon']
  - chords (chords): `strings` -22 dB · rev=0.45 · alternatives ['sf:slowstrings', 'tremolo', 'violins']
  - pad (pad): `choir` -29 dB · rev=0.5 · alternatives ['strings', 'horn', 'warmpad']
  - arp (arp): `piano` -22 dB · rev=0.35 · alternatives ['harp', 'celesta', 'epiano']
  - lead (lead): `piano` -17 dB · rev=0.35 · alternatives ['cello', 'violin', 'oboe']
- **Mix** {'lufs': -16.0, 'air': 1.0, 'low': 0.5} · reverb 3.5 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'rubato': 0.4}
- **Sound brief** Piano (melody + arpeggios); String ensemble; Celli/Basses; Celesta

### Adventure / Fantasy (`adventure`)

Adventure / fantasy score: heroic brass theme, galloping strings, snare marches

- **Tempo** 100-128 BPM · **scales** major, mixolydian · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 4, 0], [0, 6, 3, 4]], 'mixolydian': [[0, 6, 3, 0]]} · chord_bars 1 · chord size 3
- **Song form** `cinematic`: intro 8 [chords, fx, pad] (filter_in) -> rise 8 [arp, bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare] (drop) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, fx, pad] (fade) · form_scale 1
- **Drums** **timp** `X.......X.......`; **snare** `x.xxx.x.x.xxx.x.` / `x..xx..xx.x.x...`; **taiko** `X.......X...X...`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.RR.RR.R.RR.RR.` / `R-R-R-R-R-R-R-R-` · mode `pattern` · lowest note 28
- **Chord rhythm** `x.xx.xx.x.xx.xx.` / `x-x-x-x-x-x-x-x-`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x--.x-x-x-------` / `x-x-x---x---x---` / `x-----x-x-------` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `cinematic_score` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -16 dB · rev=0.3
  - snare (snare): `snare` -22 dB · rev=0.35
  - timp (snare): `timp` -20 dB · rev=0.4
  - bass (bass): `strings` -18 dB · rev=0.3 · alternatives ['cello', 'spiccato', 'contrabass']
  - chords (chords): `spiccato` -21 dB · rev=0.35 · alternatives ['strings', 'pizz', 'violins']
  - pad (pad): `horn` -24 dB · rev=0.45 · alternatives ['choir', 'strings', 'brass']
  - arp (arp): `harp` -24 dB · pan=-0.3 · rev=0.35 · alternatives ['pizz', 'spiccato', 'celesta']
  - lead (lead): `brass` -17 dB · rev=0.45 · alternatives ['horn', 'sf:trumpet', 'violin', 'flute', 'trumpet']
- **Mix** {'lufs': -11.0, 'air': 1.5, 'low': 1.0} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': ''}
- **Sound brief** Trumpets/horns (theme); Violins (gallop ostinato); Celli/Basses; Snare drum; Timpani; Harp

### Dark Tension (`tension`)

Dark tension / horror: creeping low strings, eerie celesta, choir swells, timpani hits

- **Tempo** 60-84 BPM · **scales** phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.02
- **Progressions** {'phrygian': [[0, 1, 0, 1], [0, 0, 1, 0], [0, 6, 1, 0]], 'harmonic_minor': [[0, 5, 0, 4], [0, 3, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drums** **timp** `X...............` / `........X.......`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` / `R-------R---R---` · mode `pattern` · lowest note 26
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'random', 'oct': 6, 'prob': 0.35}
- **Lead rhythm** `x-------........` / `....x-------....` / `x---x-----------` / `........x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `static_vamp` · energy `emotional_arc`
- **Instruments**
  - timp (kick role - the genre's low drum): `timp` -20 dB · rev=0.5
  - bass (bass): `strings` -18 dB · rev=0.4 · alternatives ['cello', 'tremolo', 'sf:contrabass']
  - chords (chords): `tremolo` -23 dB · rev=0.5 · alternatives ['strings', 'sf:slowstrings', 'violins']
  - pad (pad): `choir` -23 dB · rev=0.6 · alternatives ['tremolo', 'horn', 'braam']
  - arp (arp): `celesta` -25 dB · rev=0.6 · dly=0.4 · alternatives ['harp', 'pizz', 'bell']
  - lead (lead): `violin` -20 dB · rev=0.55 · alternatives ['cello', 'oboe', 'clarinet', 'choir']
- **Mix** {'lufs': -16.0, 'air': 0.5, 'low': 1.0} · reverb 4.5 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 56, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'timp', 'suggest': ''}
- **Sound brief** Low strings tremolo; Celesta / music box; Choir; Timpani; sustained horns

### Hybrid Trailer (`hybrid_trailer`)

Hybrid trailer: pulsing spiccato ostinatos, braams, taiko, distorted synth bass, huge choir

- **Tempo** 90-120 BPM · **scales** minor, phrygian, harmonic_minor · swing 0.5 (unit 16) · humanise 0.0
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 0, 5, 5], [0, 6, 5, 6], [0, 5, 3, 4]], 'phrygian': [[0, 1, 0, 1], [0, 0, 1, 0]], 'harmonic_minor': [[0, 5, 0, 4], [0, 3, 5, 4]]} · chord_bars 1 · chord size 3
- **Song form** `trailer`: intro 8 [chords, fx, top] (filter_in) -> rise 8 [arp, bass, chords, kick, top] -> build 8 [arp, bass, chords, kick, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> calm 8 [chords, fx, lead] (alt) -> build 8 [arp, bass, chords, kick, snare, top] (build, alt) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 4 [chords, fx, pad] · form_scale 1
- **Drums** **taiko** `X.....x.X...x.x.` / `X..x..x.X.x.x...` / `X.x.X...X.x.X.x.`; **snare** `....x.......x...` / `....X..x....X.x.`; **timp** `X.......X.......`; **tom** `......x.......xx` / `..............xx`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.R.R.R.R.R.R.R.` / `RRRRRRRRRRRRRRRR` / `R-R-R-R-R-R-R-R-` · mode `pattern` · lowest note 28
- **Chord rhythm** `xxxxxxxxxxxxxxxx` / `x.xxx.xxx.xxx.xx` / `xx.xx.xx.xx.xx.x`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-----x-x-------` / `x---------------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `medium` · feel `robotic` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `cinematic_score` · texture `wet_and_spacious` · rhythm `on_the_grid` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -12 dB · rev=0.3
  - snare (snare): `snare` -21 dB · rev=0.4
  - timp (snare): `timp` -19 dB · rev=0.4
  - tom (top): `tom` -22 dB · rev=0.35
  - bass (bass): `sawbass` -19 dB · alternatives ['reese', 'fmbass', 'cello']
  - chords (chords): `spiccato` -21 dB · rev=0.35 · alternatives ['strings', 'pizz', 'violins']
  - pad (pad): `braam` -21 dB · rev=0.45 · alternatives ['choir', 'horn', 'sf:trombone']
  - arp (arp): `spiccato` -27 dB · pan=0.3 · rev=0.3 · alternatives ['pizz', 'bell', 'violins']
  - lead (lead): `horn` -17 dB · rev=0.45 · alternatives ['choir', 'brass', 'violin', 'cello']
  - texture (fx): `texture` -36 dB · rev=0.5
- **Mix** {'lufs': -11.0, 'air': 1.5, 'low': 1.5} · reverb 3.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.6, 'chord_center': 57, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': ''}
- **Sound brief** Strings spiccato (ostinato); Low brass braams; Horns (theme); Choir; Taiko + timpani; distorted synth bass

### Cinematic Journey (ultimate orchestral) (`cinematic_journey`)

The ultimate orchestral generator - an epic cinematic journey for full symphony orchestra: shadowy tension (creeping low strings, timpani rolls, icy low piano) > aching solo-piano sorrow > heroic resolve (soaring violins, spiccato runs, noble horns, marcato low brass) > overwhelming tutti glory > fragile reflection > a long, luminous final chord. Rubato and dramatic tempo shifts, near-silence to fortissimo

- **Tempo** 78-92 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.006
- **Song form** `epic`: intro 8 [bass, fx, pad] (filter_in) -> rise 8 [bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop, crash) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> climax 8 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 4 [bass, fx, kick, pad] · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.......R.......` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - piano (lead): `piano` -15 dB · pan=-0.08 · rev=0.42
  - vn1 (lead): `violins` -16 dB · pan=-0.35 · rev=0.5
  - vn_hi (pad): `violins` -27 dB · pan=-0.2 · rev=0.65
  - va (chords): `violas` -20 dB · pan=0.12 · rev=0.5
  - vc (bass): `cello` -19 dB · pan=0.3 · rev=0.45
  - cb (bass): `contrabass` -19 dB · pan=0.38 · rev=0.45
  - pad (pad): `strings` -20 dB · rev=0.55
  - trem (pad): `tremolo` -26 dB · pan=0.1 · rev=0.55
  - spicc_lo (chords): `spiccato` -21 dB · pan=0.2 · rev=0.4
  - spicc_hi (arp): `spiccato` -23 dB · pan=-0.25 · rev=0.45
  - horns (pad): `horn` -19 dB · pan=-0.18 · rev=0.6
  - tpt (lead): `trumpet` -20 dB · pan=0.08 · rev=0.55
  - tbn (bass): `trombone` -19 dB · pan=0.22 · rev=0.55
  - tuba (bass): `tuba` -21 dB · pan=0.3 · rev=0.5
  - flute (arp): `flute` -24 dB · pan=-0.12 · rev=0.55
  - oboe (lead): `oboe` -25 dB · pan=0.04 · rev=0.5
  - clar (chords): `clarinet` -26 dB · pan=0.1 · rev=0.5
  - timp (bass): `timpani` -18 dB · pan=0.08 · rev=0.5
  - bdrum (kick role - the genre's low drum): `taiko` -17 dB · rev=0.5
  - cym (top): `crash` -24 dB · pan=0.15 · rev=0.6
  - tbn_marc (bass): `trombone` -19 dB · pan=0.22 · rev=0.5
  - cbsn (bass): `bassoon` -24 dB · pan=0.15 · rev=0.45
  - cbtbn (bass): `trombone` -21 dB · pan=0.28 · rev=0.5
  - choir (pad): `choir` -21 dB · rev=0.65
  - choir_oo (pad): `choir` -23 dB · rev=0.65
  - harp (arp): `harp` -22 dB · pan=-0.3 · rev=0.55
  - sub (bass): `sinebass` -18 dB
  - taiko (kick role - the genre's low drum): `taiko` -15 dB · pan=-0.1 · rev=0.4
  - snare (snare): `snare` -22 dB · pan=0.1 · rev=0.45
  - anvil (top): `anvil` -27 dB · pan=0.3 · rev=0.45
  - vc_mel (lead): `cello` -16 dB · pan=0.25 · rev=0.45
  - bsn (chords): `bassoon` -24 dB · pan=0.12 · rev=0.45
- **Mix** {'lufs': -16.0, 'air': 1.2, 'low': 1.6, 'gentle': True} · reverb 4.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'bdrum', 'suggest': '', 'composer': 'journey', 'rubato': 0.55}
- **Sound brief** Solo piano; violins I (legato + high harmonics), violas, celli, basses; strings sustain / tremolo / spiccato; 4 horns, 3 trumpets, 3 trombones, tuba; flute, oboe, clarinet; timpani, gran cassa, clash cymbals

### Cinematic Journey - Dark & Low (`cinematic_journey_low`)

Cinematic Journey - Dark & Low: the same story told from the bottom of the orchestra. Celli, horns and trombones carry the theme, double basses, tuba, contrabass trombone and contrabassoon underneath, deep resonant piano, thundering timpani and bass drum, a male choir - classic dramatic, super-low orchestral weight

- **Tempo** 72-86 BPM · **scales** minor · swing 0.5 (unit 16) · humanise 0.006
- **Song form** `epic`: intro 8 [bass, fx, pad] (filter_in) -> rise 8 [bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop, crash) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> climax 8 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 4 [bass, fx, kick, pad] · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.......R.......` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5}
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - piano (lead): `piano` -16 dB · pan=-0.08 · rev=0.42
  - vn1 (lead): `violins` -22 dB · pan=-0.35 · rev=0.5
  - vn_hi (pad): `violins` -27 dB · pan=-0.2 · rev=0.65
  - va (chords): `violas` -20 dB · pan=0.12 · rev=0.5
  - vc (bass): `cello` -18 dB · pan=0.3 · rev=0.45
  - cb (bass): `contrabass` -17 dB · pan=0.38 · rev=0.45
  - pad (pad): `strings` -21 dB · rev=0.55
  - trem (pad): `tremolo` -26 dB · pan=0.1 · rev=0.55
  - spicc_lo (chords): `spiccato` -21 dB · pan=0.2 · rev=0.4
  - spicc_hi (arp): `spiccato` -26 dB · pan=-0.25 · rev=0.45
  - horns (pad): `horn` -18 dB · pan=-0.18 · rev=0.6
  - tpt (lead): `trumpet` -23 dB · pan=0.08 · rev=0.55
  - tbn (bass): `trombone` -17 dB · pan=0.22 · rev=0.55
  - tuba (bass): `tuba` -18 dB · pan=0.3 · rev=0.5
  - flute (arp): `flute` -24 dB · pan=-0.12 · rev=0.55
  - oboe (lead): `oboe` -25 dB · pan=0.04 · rev=0.5
  - clar (chords): `clarinet` -26 dB · pan=0.1 · rev=0.5
  - timp (bass): `timpani` -16 dB · pan=0.08 · rev=0.5
  - bdrum (kick role - the genre's low drum): `taiko` -15 dB · rev=0.5
  - cym (top): `crash` -24 dB · pan=0.15 · rev=0.6
  - tbn_marc (bass): `trombone` -17 dB · pan=0.22 · rev=0.5
  - cbsn (bass): `bassoon` -21 dB · pan=0.15 · rev=0.45
  - cbtbn (bass): `trombone` -18 dB · pan=0.28 · rev=0.5
  - choir (pad): `choir` -22 dB · rev=0.65
  - choir_oo (pad): `choir` -22 dB · rev=0.65
  - harp (arp): `harp` -25 dB · pan=-0.3 · rev=0.55
  - sub (bass): `sinebass` -18 dB
  - taiko (kick role - the genre's low drum): `taiko` -15 dB · pan=-0.1 · rev=0.4
  - snare (snare): `snare` -22 dB · pan=0.1 · rev=0.45
  - anvil (top): `anvil` -27 dB · pan=0.3 · rev=0.45
  - vc_mel (lead): `cello` -15 dB · pan=0.25 · rev=0.45
  - bsn (chords): `bassoon` -24 dB · pan=0.12 · rev=0.45
- **Mix** {'lufs': -15.0, 'air': -1.5, 'low': 3.4, 'gentle': True} · reverb 4.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'bdrum', 'suggest': '', 'composer': 'journey', 'low': True, 'rubato': 0.55}
- **Sound brief** Solo piano; violins I (legato + high harmonics), violas, celli, basses; strings sustain / tremolo / spiccato; 4 horns, 3 trumpets, 3 trombones, tuba; flute, oboe, clarinet; timpani, gran cassa, clash cymbals

## Epic

### Epic Orchestral (`epic_orchestral`)

Epic orchestral (movie-trailer scale): driving string ostinatos over double basses and celli, horns and trombones carrying a huge theme, tuba and low brass underneath, choir, taiko and timpani - SUPER EPIC

- **Tempo** 84-112 BPM · **scales** minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 5, 3, 4], [0, 6, 5, 6], [0, 3, 6, 4]], 'harmonic_minor': [[0, 5, 3, 4], [0, 5, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `epic`: intro 8 [bass, fx, pad] (filter_in) -> rise 8 [bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop, crash) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> climax 8 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 4 [bass, fx, kick, pad] · form_scale 1
- **Drums** **taiko** `X.....x.X...x.x.` / `X..x..x.X.x.x...` / `X.x.X...X.x.X.x.`; **timp** `X.......X.......` / `X.....X.X.......`; **snare** `....x.......x...` / `..x.x..x..x.x.xx`; **crash** `X...............` / `................`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.R.R.R.R.R.R.R.` / `RRRRRRRRRRRRRRRR` / `R.RRR.RRR.RRR.RR` · mode `pattern` · lowest note 24
- **Chord rhythm** `xxxxxxxxxxxxxxxx` / `x.xxx.xxx.xxx.xx`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-----x-x-------` / `x-------x-------`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `dense` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -11 dB · rev=0.35
  - timp (snare): `timp` -16 dB · rev=0.45
  - snare (snare): `snare` -22 dB · rev=0.45
  - crash (top): `crash` -24 dB · rev=0.5
  - bass (bass): `contrabass` -15 dB · rev=0.35 · alternatives ['cello', 'tuba', 'sf:bassoon']
  - celli (bass): `cello` -19 dB · rev=0.35
  - lowbrass (pad): `brass` -19 dB · rev=0.4
  - choir (pad): `choir` -22 dB · rev=0.55
  - chords (chords): `spiccato` -20 dB · rev=0.4 · alternatives ['strings', 'pizz', 'violins']
  - pad (pad): `horn` -19 dB · rev=0.5 · alternatives ['brass', 'choir', 'strings']
  - arp (arp): `violins` -25 dB · pan=0.25 · rev=0.4 · alternatives ['spiccato', 'harp', 'pizz']
  - lead (lead): `brass` -16 dB · rev=0.5 · alternatives ['horn', 'violins', 'choir']
  - lead_hi (lead): `violins` -21 dB · rev=0.5
  - texture (fx): `texture` -38 dB · rev=0.5
- **Mix** {'lufs': -10.0, 'air': 1.4, 'low': 2.2} · reverb 3.8 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.7, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': '', 'slow_chords': 0.35, 'repetition': 0.8}
- **Sound brief** Double basses + celli (ostinato); violins & violas spiccato; 6 horns + trombones (theme); tuba; choir; taiko, timpani

### Epic Battle (`epic_battle`)

Epic battle music: war drums in driving 16ths, relentless low-string and spiccato ostinatos, staccato low-brass hits, chanting choir and screaming horns - phrygian darkness at full force

- **Tempo** 128-150 BPM · **scales** phrygian, harmonic_minor, minor · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'phrygian': [[0, 1, 0, 1], [0, 0, 1, 6], [0, 1, 6, 5]], 'harmonic_minor': [[0, 5, 0, 4], [0, 1, 0, 4]], 'minor': [[0, 5, 6, 4], [0, 0, 5, 6]]} · chord_bars 1 · chord size 3
- **Song form** `epic`: intro 8 [bass, fx, pad] (filter_in) -> rise 8 [bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop, crash) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> climax 8 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 4 [bass, fx, kick, pad] · form_scale 1
- **Drums** **taiko** `X.x.X.x.X.xxX.x.` / `X.xxX.x.X.xxX.xx` / `XxX.XxX.XxX.Xxxx`; **timp** `X...X...X...X...` / `X.X.X...X.X.X...`; **snare** `x.x.x.x.x.xxx.x.` / `..x...x...x.xxxx`; **tom** `......x.......xx` / `..x.....x.x...xx`; **crash** `X...............` / `................`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `RRRRRRRRRRRRRRRR` / `R.RRR.RRR.RRR.RR` · mode `pattern` · lowest note 24
- **Chord rhythm** `xxxxxxxxxxxxxxxx` / `xx.xx.xx.xx.xx.x`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5}
- **Lead rhythm** `x-x-x---x-x-x---` / `x---x-x-x-------` / `x.x.x---x.x.x---` / `x-------x-x-x---`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `dense` · feel `tight_swing` · melody `minimal_motivic` · bass `rolling_groove` · drop `long_build` · variation `theme_and_variations` · culture `cinematic_score` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `modal` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -11 dB · rev=0.35
  - timp (snare): `timp` -16 dB · rev=0.45
  - snare (snare): `snare` -22 dB · rev=0.45
  - crash (top): `crash` -24 dB · rev=0.5
  - tom (top): `tom` -21 dB · rev=0.35
  - bass (bass): `contrabass` -15 dB · rev=0.35 · alternatives ['cello', 'tuba', 'sf:bassoon']
  - celli (bass): `cello` -19 dB · rev=0.35
  - lowbrass (pad): `brass` -19 dB · rev=0.4
  - choir (pad): `choir` -22 dB · rev=0.55
  - chords (chords): `spiccato` -19 dB · rev=0.35 · alternatives ['strings', 'pizz', 'violins']
  - pad (pad): `brass` -19 dB · rev=0.4 · alternatives ['horn', 'strings', 'choir']
  - arp (arp): `spiccato` -25 dB · pan=0.3 · rev=0.3 · alternatives ['violins', 'pizz', 'harp']
  - lead (lead): `horn` -16 dB · rev=0.45 · alternatives ['brass', 'choir', 'cello']
  - lead_choir (lead): `choir` -21 dB · rev=0.5
  - texture (fx): `texture` -36 dB · rev=0.5
- **Mix** {'lufs': -9.5, 'air': 1.3, 'low': 2.4, 'drive': 0.15} · reverb 3.4 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.6, 'chord_center': 57, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': '', 'repetition': 0.85}

### Dark Choral Epic (`epic_choir`)

Dark choral epic ("Dies Irae" / sacred horror): a massive choir over pipe organ, droning double basses and tuba, tolling tubular bells, timpani and orchestral bass drum - slow, monumental, apocalyptic

- **Tempo** 60-84 BPM · **scales** minor, harmonic_minor, phrygian · swing 0.5 (unit 16) · humanise 0.008
- **Progressions** {'minor': [[0, 5, 6, 4], [0, 3, 5, 4], [0, 6, 5, 4]], 'harmonic_minor': [[0, 5, 1, 4], [0, 3, 4, 4]], 'phrygian': [[0, 1, 0, 1], [0, 1, 6, 0]]} · chord_bars 2 · chord size 3
- **Song form** `epic`: intro 8 [bass, fx, pad] (filter_in) -> rise 8 [bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop, crash) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> climax 8 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 4 [bass, fx, kick, pad] · form_scale 1
- **Drums** **taiko** `X...............` / `X.......X.......`; **timp** `X.......X.......` / `X...........X.x.`; **crash** `X...............` / `................`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` / `R-------R-------` · mode `pattern` · lowest note 24
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 4, 'mode': 'up', 'oct': 4, 'prob': 0.6}
- **Lead rhythm** `x---x---x-------` / `x-------x---x---` / `x---x---x---x---`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `medium` · feel `loose_human` · melody `minimal_motivic` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -14 dB · rev=0.5
  - timp (snare): `timp` -16 dB · rev=0.5
  - crash (top): `crash` -24 dB · rev=0.6
  - bass (bass): `contrabass` -15 dB · rev=0.35 · alternatives ['cello', 'tuba', 'sf:bassoon']
  - celli (bass): `cello` -19 dB · rev=0.35
  - lowbrass (pad): `brass` -19 dB · rev=0.4
  - chords (chords): `organ` -21 dB · rev=0.55 · alternatives ['strings', 'epiano', 'piano']
  - pad (pad): `choir` -17 dB · rev=0.6 · alternatives ['brass', 'strings', 'warmpad']
  - arp (arp): `tubular` -22 dB · rev=0.6 · alternatives ['harp', 'celesta', 'pizz']
  - lead (lead): `choir` -16 dB · rev=0.6 · alternatives ['horn', 'brass', 'strings']
  - lead_brass (lead): `brass` -22 dB · rev=0.5
- **Mix** {'lufs': -11.0, 'air': 1.0, 'low': 2.4} · reverb 4.5 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['timp'], 'bass_gate': 0.92, 'chord_center': 57, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': '', 'repetition': 0.85}

### Heroic Anthem (`heroic_anthem`)

Heroic anthem: a soaring major-key fanfare on horns and trumpets, sweeping violins, marching snare, cymbals and timpani over trombones, tuba and a rock-solid string bass - triumphant and huge

- **Tempo** 92-124 BPM · **scales** major, lydian, mixolydian · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 0, 4], [5, 3, 0, 4], [0, 6, 3, 4]], 'lydian': [[0, 1, 0, 1], [0, 1, 4, 0]], 'mixolydian': [[0, 6, 3, 0], [0, 6, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `epic`: intro 8 [bass, fx, pad] (filter_in) -> rise 8 [bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop, crash) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> climax 8 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 4 [bass, fx, kick, pad] · form_scale 1
- **Drums** **taiko** `X.......X.......` / `X.....x.X.......`; **timp** `X.......X.......` / `X...X...X.x.x.x.`; **snare** `x.xxx.x.x.xxx.x.` / `x.x.x.x.xxx.xxxx`; **crash** `X...............` / `................`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.R.R.R.R.R.R.R.` / `R-R-R-R-R-R-R-R-` / `R---R---R---R---` · mode `pattern` · lowest note 26
- **Chord rhythm** `x.xx.xx.x.xx.xx.` / `xxxxxxxxxxxxxxxx`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x--x-xx---x-x---` / `x-----x-x-x-----` / `x---x-x-x---x---` / `x-x-x-----x-----`
- **Build-ups** default `roll` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `dense` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `long_build` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -11 dB · rev=0.35
  - timp (snare): `timp` -16 dB · rev=0.45
  - snare (snare): `snare` -22 dB · rev=0.45
  - crash (top): `crash` -24 dB · rev=0.5
  - bass (bass): `contrabass` -15 dB · rev=0.35 · alternatives ['cello', 'tuba', 'sf:bassoon']
  - celli (bass): `cello` -19 dB · rev=0.35
  - lowbrass (pad): `brass` -19 dB · rev=0.4
  - choir (pad): `choir` -22 dB · rev=0.55
  - chords (chords): `spiccato` -21 dB · rev=0.4 · alternatives ['strings', 'pizz', 'violins']
  - pad (pad): `horn` -19 dB · rev=0.45 · alternatives ['brass', 'strings', 'sf:slowstrings']
  - arp (arp): `violins` -25 dB · pan=0.25 · rev=0.4 · alternatives ['harp', 'spiccato', 'pizz']
  - lead (lead): `trumpet` -16 dB · rev=0.45 · alternatives ['horn', 'brass', 'violins']
  - lead_horns (lead): `horn` -20 dB · rev=0.45
  - lead_hi (lead): `violins` -22 dB · rev=0.5
- **Mix** {'lufs': -10.5, 'air': 1.6, 'low': 2.0} · reverb 3.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['snare'], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': True, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': '', 'repetition': 0.8}

### Grand Symphonic Finale (`symphonic_finale`)

Grand symphonic finale (Tchaikovsky / Mahler scale): full brass chorale over tremolo strings, thundering timpani rolls, cymbal crashes, double basses and tuba - the last, enormous page of a symphony

- **Tempo** 96-132 BPM · **scales** major, minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.01
- **Progressions** {'major': [[0, 3, 4, 0], [0, 5, 3, 4], [0, 1, 4, 0]], 'minor': [[0, 5, 3, 4], [0, 3, 4, 0]], 'harmonic_minor': [[0, 3, 4, 0], [0, 5, 1, 4]]} · chord_bars 1 · chord size 4
- **Song form** `epic`: intro 8 [bass, fx, pad] (filter_in) -> rise 8 [bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare, top] (drop, crash) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad, snare] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> climax 8 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop, crash) -> outro 4 [bass, fx, kick, pad] · form_scale 1
- **Drums** **timp** `X.X.X.X.X.X.X.X.` / `XXXXXXXXXXXXXXXX` / `X.......X.......`; **crash** `X...............` / `................`; **taiko** `X...............`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---R---R---R---` / `R-------R-------` / `R.R.R.R.R.R.R.R.` · mode `pattern` · lowest note 24
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-------x---x---` / `x---x---x-x-x---` / `x-----x-x-------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `dense` · feel `drifting` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - taiko (kick role - the genre's low drum): `taiko` -16 dB · rev=0.45
  - timp (snare): `timp` -15 dB · rev=0.45
  - crash (top): `crash` -23 dB · rev=0.55
  - bass (bass): `contrabass` -15 dB · rev=0.35 · alternatives ['cello', 'tuba', 'sf:bassoon']
  - celli (bass): `cello` -19 dB · rev=0.35
  - lowbrass (pad): `brass` -19 dB · rev=0.4
  - choir (pad): `choir` -22 dB · rev=0.55
  - chords (chords): `tremolo` -20 dB · rev=0.45 · alternatives ['strings', 'sf:slowstrings', 'violins']
  - pad (pad): `brass` -18 dB · rev=0.5 · alternatives ['horn', 'choir', 'strings']
  - arp (arp): `harp` -25 dB · rev=0.45 · alternatives ['spiccato', 'pizz', 'celesta']
  - lead (lead): `violins` -16 dB · rev=0.5 · alternatives ['horn', 'trumpet', 'sax']
  - lead_horns (lead): `horn` -20 dB · rev=0.5
- **Mix** {'lufs': -11.5, 'air': 1.2, 'low': 1.8} · reverb 3.8 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['timp'], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'taiko', 'suggest': '', 'rubato': 0.3}

## Solo Piano

### Solo Piano Miniature (`piano_miniature`)

Solo piano miniature: a short, tender piece for one softly played, felt-muffled upright, close-miked in wide stereo - an unbroken rocking 8th-note left hand swaying between two chords, a plain, singing right-hand tune on top, a middle part that lifts to new chords and a gentle swell before it simply stops; no other instruments

- **Tempo** 74-84 BPM · **scales** major · swing 0.5 (unit 16) · humanise 0.004
- **Progressions** {'major': [[0, 3, 0, 3], [0, 3, 0, 3], [3, 4, 3, 4], [0, 3, 0, 4], [0, 3, 5, 3]]} · chord_bars 1 · chord size 3
- **Song form** `piano_miniature`: A 8 [arp, bass, lead] -> A2 8 [arp, bass, lead] (var=dim) -> bridge 8 [arp, bass, lead] (alt) -> A3 8 [arp, bass, lead] (level=0.95, level_to=1.0) -> end 2 [arp, bass] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` / `R-------O-------` · mode `pattern` · lowest note 40
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 3}
- **Lead rhythm** `x-------x---x---` / `x---x---x-------` / `x-----x-x-------` / `x---x---x---x-xx`
- **Build-ups** default `none` · choices []
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `nostalgic_simple` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `static_vamp` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `piano` -17 dB · pan=-0.45 · rev=0.08
  - arp (arp): `piano` -20 dB · pan=-0.15 · rev=0.08
  - lead (lead): `piano` -18 dB · pan=0.35 · rev=0.08
- **Mix** {'lufs': -19.0, 'air': -9.0, 'low': 4.0, 'width': 1.25, 'gentle': True} · reverb 0.9 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 51, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 4, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'own_progs': True, 'no_transition_fx': True, 'repetition': 0.8, 'melody_range': 0.35, 'rubato': 0.08}
- **Sound brief** One acoustic piano only (left-hand 8th-note broken chords + right-hand melody), very soft and even, muffled felt tone, close wide stereo mic, dry room; ~78 BPM; two-chord sway (I-IV), middle part IV-V

## Ambient & Experimental

### Experimental field ambient (`field_ambient`)

Experimental field-recording ambient (Japanese style): no steady beat - knocks of wood, bells, plucked koto, breathy flute, low drones and the sound of the room and outdoors, each appearing for a few bars and leaving again; very wide, quiet and patient

- **Tempo** 96-108 BPM · **scales** minor, phrygian · swing 0.5 (unit 16) · humanise 0.03
- **Progressions** {'minor': [[0, 0, 0, 0], [0, 0, 6, 0]], 'phrygian': [[0, 1, 0, 0]]} · chord_bars 1 · chord size 3
- **Song form** `field_ambient`: A 8 [fx, pad] -> B 8 [arp, fx, pad, top] -> C 8 [bass, fx, lead, top] -> B 8 [arp, fx, kick, pad, top] (alt) -> D 8 [bass, fx, kick, lead, pad, top] -> A 4 [fx] -> C 8 [arp, bass, fx, lead, top] (alt) -> outro 8 [fx, lead, pad] (fade) · form_scale 1
- **Drums** **kick** `X...............` / `........x.......`; **woodblock** `x.....x....x....` / `...x......x..x..` / `x..x...........x`; **rim** `....x.........x.` / `..........x.....`; **shaker** `..x.....x..x....`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` / `........R-------` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 1, 'mode': 'random', 'oct': 5, 'prob': 0.45}
- **Lead rhythm** `x-------........` / `........x---....` / `x---....x-......`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `atmospheric_drift` · density `sparse` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `cinematic_score` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `static_vamp` · energy `emotional_arc`
- **Instruments**
  - kick (kick): `kick` -20 dB
  - woodblock (top): `woodblock` -26 dB · pan=0.4 · rev=0.4
  - rim (top): `rim` -28 dB · pan=-0.4 · rev=0.4
  - shaker (top): `shaker` -32 dB · pan=0.6 · rev=0.4
  - bass (bass): `drone` -22 dB · alternatives ['sinebass', 'cello', 'tanpura']
  - chords (chords): `koto` -26 dB · rev=0.5 · alternatives ['harp', 'pizz', 'kalimba']
  - pad (pad): `glasspad` -30 dB · pan=-0.2 · rev=0.7 · alternatives ['warmpad', 'solina']
  - arp (arp): `koto` -26 dB · pan=0.5 · rev=0.6 · dly=0.3 · alternatives ['kalimba', 'marimba', 'harp']
  - lead (lead): `flute` -22 dB · pan=-0.4 · rev=0.6 · dly=0.3 · alternatives ['tinwhistle', 'koto', 'oboe']
  - texture (fx): `texture` -30 dB
- **Mix** {'lufs': -17.0, 'air': 0.4, 'low': 0.6, 'width': 1.8, 'gentle': True} · reverb 3.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': ['rim'], 'bass_gate': 0.92, 'chord_center': 55, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'slow_chords': 0.35, 'own_progs': True, 'no_transition_fx': True}
- **Sound brief** Wood blocks / knocks, temple bells, koto, shakuhachi-like flute, low drone, field recordings (birds, room, water); sparse, very wide

## Fantasy & Games

### Fantasy RPG (`fantasy_rpg`)

Fantasy RPG / video-game score: harp arpeggios, flute & oboe melody, warm strings, horn swells

- **Tempo** 84-116 BPM · **scales** major, lydian, dorian · swing 0.5 (unit 16) · humanise 0.01
- **Progressions** {'major': [[0, 4, 5, 3], [0, 3, 0, 4], [3, 4, 2, 5], [0, 2, 3, 4], [0, 5, 3, 4]], 'lydian': [[0, 1, 0, 1], [0, 1, 4, 0], [0, 1, 5, 4]], 'dorian': [[0, 3, 0, 3], [0, 6, 3, 0], [0, 3, 6, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drums** **timp** `X...............` / `X.......X.......`; **shaker** `..x...x...x...x.`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R-------R-------` / `R---R---R---R---` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---------------` / `x-------x-------` / `x---x---x---x---`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x---x---` / `x-----x-x-------` / `..x-x-x-x---x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `cinematic_score` · texture `wet_and_spacious` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - timp (kick role - the genre's low drum): `timp` -24 dB · rev=0.4
  - shaker (top): `shaker` -34 dB · pan=0.3 · rev=0.3
  - bass (bass): `cello` -20 dB · rev=0.35 · alternatives ['strings', 'pizz', 'harp']
  - chords (chords): `strings` -22 dB · rev=0.4 · alternatives ['harp', 'piano', 'sf:slowstrings']
  - pad (pad): `horn` -27 dB · rev=0.45 · alternatives ['choir', 'strings', 'brass']
  - arp (arp): `harp` -22 dB · pan=-0.3 · rev=0.4 · alternatives ['celesta', 'pizz', 'marimba', 'kalimba']
  - lead (lead): `flute` -18 dB · pan=0.15 · rev=0.4 · alternatives ['oboe', 'violin', 'clarinet', 'sf:piccolo', 'horn', 'celesta']
- **Mix** {'lufs': -14.0, 'air': 1.2, 'low': 0.5} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'timp', 'suggest': ''}
- **Sound brief** Flute / oboe (melody); Harp (arpeggios); Strings; French horns; Timpani

## Classical Eras

### Orchestral (`orchestral`)

Classical / romantic orchestra: lyrical violin melody, string harmony, harp, horns

- **Tempo** 66-96 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 3, 4, 0], [0, 5, 3, 4], [0, 4, 5, 3]], 'minor': [[0, 3, 4, 0], [0, 5, 3, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drums** **timp** `X...............`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R-------R-------` / `R---R---R---R---` · mode `pattern` · lowest note 31
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x---x-x-x-------` / `x-----x-x---x---` / `x-x-x---x-------` / `x---------------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - timp (kick role - the genre's low drum): `timp` -22 dB · rev=0.4
  - bass (bass): `strings` -19 dB · rev=0.35 · alternatives ['cello', 'sf:contrabass', 'pizz']
  - chords (chords): `strings` -21 dB · rev=0.4 · alternatives ['sf:slowstrings', 'harp', 'tremolo']
  - pad (pad): `horn` -25 dB · rev=0.45 · alternatives ['choir', 'strings', 'clarinet']
  - arp (arp): `harp` -23 dB · pan=-0.3 · rev=0.4 · alternatives ['pizz', 'celesta', 'flute']
  - lead (lead): `violin` -17 dB · rev=0.45 · alternatives ['flute', 'oboe', 'clarinet', 'cello', 'horn']
- **Mix** {'lufs': -16.0, 'air': 1.0, 'low': 0.5} · reverb 3.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'timp', 'suggest': ''}
- **Sound brief** Violin solo (melody); String ensemble; Cellos & basses; Harp arpeggios; French horns pad; Timpani

### Neoclassical (`neoclassical`)

Neoclassical / modern classical: intimate piano figures, slow string swells, solo cello

- **Tempo** 60-82 BPM · **scales** minor, major · swing 0.5 (unit 16) · humanise 0.018
- **Progressions** {'minor': [[0, 5, 2, 6], [0, 3, 5, 4], [5, 3, 0, 4], [0, 6, 5, 3], [0, 5, 3, 3]], 'major': [[0, 4, 5, 3], [3, 0, 4, 5], [0, 2, 3, 0], [5, 3, 0, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` / `R-------R-------` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---------------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 4}
- **Lead rhythm** `x---x---x-------` / `x-----x-x-------` / `....x---x---x---` / `x-------x---x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `long_lyrical` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `concert_hall` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `cello` -21 dB · rev=0.4 · alternatives ['strings', 'contrabass', 'sf:bassoon']
  - chords (chords): `strings` -23 dB · rev=0.45 · alternatives ['sf:slowstrings', 'tremolo', 'violins']
  - arp (arp): `piano` -22 dB · pan=-0.15 · rev=0.35 · alternatives ['harp', 'celesta', 'epiano']
  - lead (lead): `piano` -18 dB · pan=0.1 · rev=0.4 · alternatives ['cello', 'violin', 'epiano']
- **Mix** {'lufs': -16.0, 'air': 0.8, 'low': 0.5} · reverb 3.8 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 57, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'rubato': 0.3}
- **Sound brief** Felt / soft piano (figures + melody); String ensemble legato (swells); Solo cello

### Chamber / String Quartet (`chamber`)

Chamber / string quartet: violin melody, viola harmony, cello line, pizzicato colour

- **Tempo** 72-112 BPM · **scales** major, minor, harmonic_minor · swing 0.5 (unit 16) · humanise 0.014
- **Progressions** {'major': [[0, 3, 4, 0], [0, 5, 1, 4], [0, 4, 5, 3], [0, 3, 1, 4]], 'minor': [[0, 3, 4, 0], [0, 5, 3, 4], [0, 6, 5, 4]], 'harmonic_minor': [[0, 3, 4, 0], [0, 5, 3, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R-------R-------` / `R---R---R---R---` / `R-----R-R-------` · mode `pattern` · lowest note 36
- **Chord rhythm** `x-------x-------` / `x---x---x---x---` / `x-----x-x-------`
- **Arp** {'rate': 2, 'mode': 'up', 'oct': 5, 'prob': 0.6}
- **Lead rhythm** `x---x-x-x-------` / `x-x-x---x---x---` / `x-----x-x-x-x---` / `..x-x-x-x-------`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `long_lyrical` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `cello` -19 dB · rev=0.3 · alternatives ['pizz', 'contrabass', 'sf:bassoon']
  - chords (chords): `strings` -23 dB · rev=0.3 · alternatives ['sf:viola', 'sf:slowstrings', 'tremolo']
  - arp (arp): `pizz` -25 dB · pan=-0.3 · rev=0.3 · alternatives ['harp', 'spiccato', 'piano']
  - lead (lead): `violin` -17 dB · pan=0.2 · rev=0.35 · alternatives ['cello', 'flute', 'oboe', 'clarinet']
- **Mix** {'lufs': -16.0, 'air': 1.0, 'low': 0.5} · reverb 2.6 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'rubato': 0.25}
- **Sound brief** Violin I (melody); Viola (harmony); Cello (bass line); Violin II pizzicato

### Baroque (`baroque`)

Baroque: harpsichord continuo, running string lines, cello octave bass, circle-of-fifths harmony

- **Tempo** 96-128 BPM · **scales** major, harmonic_minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 3, 1, 4], [0, 5, 1, 4], [0, 3, 4, 0], [5, 1, 4, 0], [0, 4, 5, 2, 3, 0, 1, 4]], 'harmonic_minor': [[0, 3, 4, 0], [0, 5, 3, 4], [5, 3, 4, 0]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.R.R.R.R.R.R.R.` / `R.O.R.O.R.O.R.O.` / `R...F...R...F...` · mode `pattern` · lowest note 36
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `x...x...x...x...` / `x.xxx.x.x.xxx.x.`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x-x-x---` / `x-x-x-x-x.x.x---` / `x.x.x.x.x.x.x.x.` / `x---x.x.x---x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `sparse` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `cello` -19 dB · rev=0.25 · alternatives ['sf:bassoon', 'contrabass', 'tuba']
  - chords (chords): `harpsichord` -22 dB · pan=-0.2 · rev=0.25 · alternatives ['strings', 'organ', 'sf:slowstrings']
  - pad (pad): `strings` -30 dB · rev=0.3 · alternatives ['organ', 'solina', 'warmpad']
  - arp (arp): `spiccato` -26 dB · pan=0.25 · rev=0.25 · alternatives ['harpsichord', 'harp', 'pizz']
  - lead (lead): `violin` -18 dB · pan=0.1 · rev=0.3 · alternatives ['oboe', 'flute', 'harpsichord', 'sf:trumpet', 'trumpet']
- **Mix** {'lufs': -15.0, 'air': 1.2, 'low': 0.5} · reverb 2.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.7, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'forms': ['binary', 'prelude', 'binary']}
- **Sound brief** Harpsichord (continuo); Violins (running 16ths); Cello + bass (octaves); Oboe / violin solo

### Waltz (3/4) (`waltz`)

Viennese waltz (3/4): oom-pah-pah strings, lilting violin melody, harp and woodwind colours

- **Tempo** 96-124 BPM · meter 3/4 · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.012
- **Progressions** {'major': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 1, 4, 0], [0, 5, 1, 4]], 'minor': [[0, 4, 4, 0], [0, 3, 4, 0], [0, 5, 3, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1.5
- **Drums** **timp** `X...........` / `X.....X.....`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R.....F.....` / `R.....R.....` / `R.....O.....` · mode `pattern` · lowest note 33
- **Chord rhythm** `..x.x...x.x.` / `..x.x...x.x-`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x---x-x-x---` / `x-----x---x-` / `x-x-x-x-----` / `x---------x-` / `x-xx-xx-----`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `medium` · feel `loose_human` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - timp (kick role - the genre's low drum): `timp` -26 dB · rev=0.4
  - bass (bass): `cello` -19 dB · rev=0.35 · alternatives ['pizz', 'sf:contrabass', 'contrabass']
  - chords (chords): `spiccato` -22 dB · rev=0.35 · alternatives ['strings', 'harp', 'pizz']
  - arp (arp): `harp` -26 dB · pan=-0.3 · rev=0.4 · alternatives ['celesta', 'flute', 'pizz']
  - lead (lead): `violin` -17 dB · pan=0.15 · rev=0.4 · alternatives ['flute', 'clarinet', 'oboe', 'cello']
- **Mix** {'lufs': -15.0, 'air': 1.2, 'low': 0.6} · reverb 3.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.5, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'timp', 'suggest': ''}
- **Sound brief** Violins (melody); String section short (pah-pah); Celli + basses (oom); Harp; Flute / clarinet

### Classical (Mozart era) (`classical_period`)

Classical period (Mozart / Haydn): elegant homophony - a clear singing melody over Alberti-bass and string accompaniment, 4+4-bar phrases, functional cadences, pairs of winds, horns and timpani

- **Tempo** 100-140 BPM · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 3, 4, 0], [0, 4, 0, 4], [0, 1, 4, 0], [0, 5, 1, 4], [0, 3, 1, 4]], 'minor': [[0, 3, 4, 0], [0, 5, 3, 4]]} · chord_bars 1 · chord size 3
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drums** **timp** `X...............` / `................`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R...R...R...R...` / `R.......R.......` · mode `pattern` · lowest note 36
- **Chord rhythm** `x...x...x...x...` / `x.......x.......`
- **Arp** {'rate': 1, 'mode': 'alberti', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x-------` / `x---x.x.x.x.x---` / `x-x-x-x-x-x-x---` / `x.x.x-x-x-------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - timp (kick role - the genre's low drum): `timp` -28 dB · rev=0.4
  - bass (bass): `cello` -20 dB · rev=0.3 · alternatives ['contrabass', 'sf:bassoon', 'tuba']
  - chords (chords): `strings` -26 dB · rev=0.3 · alternatives ['spiccato', 'sf:slowstrings', 'tremolo']
  - pad (pad): `horn` -31 dB · rev=0.4 · alternatives ['strings', 'brass', 'sf:slowstrings']
  - arp (arp): `piano` -23 dB · pan=-0.15 · rev=0.25 · alternatives ['harpsichord', 'strings', 'epiano']
  - lead (lead): `violin` -18 dB · rev=0.3 · alternatives ['flute', 'oboe', 'clarinet']
- **Mix** {'lufs': -16.0, 'air': 1.0, 'low': 0.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'timp', 'suggest': '', 'repetition': 0.65, 'forms': ['theme_var', 'sonata']}
- **Sound brief** Violins (melody); piano / strings Alberti bass; cellos & basses; pairs of flutes, oboes, horns; timpani

### Romantic Orchestra (`romantic`)

Romantic orchestra (Tchaikovsky / Brahms): expansive lyrical themes with rubato, rich chromatic harmony, full strings with continuous vibrato, horns and woodwinds, swelling ppp-to-fff dynamics

- **Tempo** 60-92 BPM · **scales** minor, major, harmonic_minor · swing 0.5 (unit 16) · humanise 0.012
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 3, 6, 4], [0, 6, 5, 4]], 'major': [[0, 5, 3, 4], [0, 2, 3, 4], [0, 4, 5, 2]], 'harmonic_minor': [[0, 3, 4, 5], [0, 5, 1, 4]]} · chord_bars 1 · chord size 4
- **Song form** `cinematic`: intro 8 [chords, fx, pad] (filter_in) -> rise 8 [arp, bass, chords, kick, pad] -> theme 16 [arp, bass, chords, kick, lead, pad, snare] (drop) -> calm 8 [chords, lead, pad] (alt) -> build 8 [arp, bass, chords, kick, pad] (build) -> climax 16 [arp, bass, chords, fx, kick, lead, pad, snare, top] (drop) -> outro 8 [chords, fx, pad] (fade) · form_scale 1
- **Drums** **timp** `X...............` / `X.......X.......`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R-------R-------` / `R---------------` · mode `pattern` · lowest note 33
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 2, 'mode': 'updown', 'oct': 5, 'prob': 0.7}
- **Lead rhythm** `x-----x-x-------` / `x---x-x-x-------` / `x-------x---x---` / `x-x-x---x-------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `medium` · feel `drifting` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - timp (kick role - the genre's low drum): `timp` -26 dB · rev=0.5
  - bass (bass): `cello` -19 dB · rev=0.4 · alternatives ['contrabass', 'sf:bassoon', 'tuba']
  - chords (chords): `strings` -21 dB · rev=0.45 · alternatives ['tremolo', 'sf:slowstrings', 'violins']
  - pad (pad): `horn` -27 dB · rev=0.5 · alternatives ['choir', 'strings', 'brass']
  - arp (arp): `harp` -27 dB · rev=0.45 · alternatives ['pizz', 'piano']
  - lead (lead): `violin` -17 dB · rev=0.45 · alternatives ['cello', 'horn', 'clarinet', 'oboe']
- **Mix** {'lufs': -15.0, 'air': 1.0, 'low': 0.6} · reverb 3.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'timp', 'suggest': '', 'rubato': 0.8, 'forms': ['lyric', 'cinematic']}

### Impressionism (`impressionism`)

Impressionism (Debussy / Ravel): modal and lydian colours, parallel gliding chords, blurred harmony, harp and flute over muted strings and piano washes, flexible pulse - atmosphere over function

- **Tempo** 56-80 BPM · **scales** lydian, dorian, mixolydian · swing 0.5 (unit 16) · humanise 0.012
- **Progressions** {'lydian': [[0, 1, 0, 1], [0, 1, 2, 1], [0, 6, 1, 0]], 'dorian': [[0, 3, 0, 6], [0, 1, 0, 3]], 'mixolydian': [[0, 6, 0, 6]]} · chord_bars 2 · chord size 4
- **Song form** `orchestral`: intro 4 [chords, pad] (filter_in) -> A 16 [bass, chords, lead, pad] -> B 16 [arp, bass, chords, lead, pad] (alt) -> A 16 [arp, bass, chords, kick, lead, pad] -> outro 8 [bass, chords, pad] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` · mode `pattern` · lowest note 36
- **Chord rhythm** `x---------------` / `x-------x-------`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x-----x-x-x-----` / `x---x---x-------` / `..x-x-x-x-------` / `x-x-x-x---------`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `long_lyrical` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `modal` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `cello` -22 dB · rev=0.5 · alternatives ['contrabass', 'sf:bassoon', 'tuba']
  - chords (chords): `piano` -22 dB · rev=0.5 · alternatives ['harp', 'strings', 'epiano']
  - pad (pad): `strings` -27 dB · rev=0.6 · alternatives ['choir', 'solina', 'warmpad']
  - arp (arp): `harp` -24 dB · pan=0.2 · rev=0.5 · alternatives ['celesta', 'piano', 'pizz']
  - lead (lead): `flute` -19 dB · rev=0.5 · alternatives ['oboe', 'clarinet', 'violin']
- **Mix** {'lufs': -17.0, 'air': 1.0, 'low': 0.4} · reverb 3.5 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 62, 'strum': 0.0, 'voicing': 'open', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'rubato': 0.5, 'forms': ['arch', 'orchestral']}

### Minimalism (`minimalism`)

Minimalism (Reich / Glass / Adams): a steady pulse of repeating cells on marimba, piano and strings, shifting by gradual additive / phasing processes over slow diatonic harmony

- **Tempo** 120-160 BPM · **scales** minor, major, dorian · swing 0.5 (unit 16) · humanise 0.002
- **Progressions** {'minor': [[0, 5, 3, 4], [0, 6, 5, 6]], 'major': [[0, 4, 5, 3], [0, 3, 0, 4]], 'dorian': [[0, 3, 0, 3]]} · chord_bars 4 · chord size 3
- **Song form** `groove`: intro 16 [kick, top] (filter_in) -> verse 16 [bass, kick, snare, top] -> verse 16 [arp, bass, kick, snare, top] (crash) -> break 16 [arp, chords, pad, top] (build) -> drop 32 [arp, bass, chords, kick, lead, snare, top] (drop) -> outro 16 [bass, kick, top] (fade) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R-------R-------` / `R.......R.......` · mode `pattern` · lowest note 36
- **Chord rhythm** `x.x.x.x.x.x.x.x.` / `xx.xx.xx.xx.xx.x`
- **Arp** {'rate': 1, 'mode': 'updown', 'oct': 5}
- **Lead rhythm** `x.x.x.x.x.x.x.x.` / `x.xx.x.xx.x.xx.x` / `xx.x.xx.x.xx.x.x`
- **Build-ups** default `swell` · choices ['swell', 'cymbal', 'tomgroove', 'march', 'pickup', 'drumless', 'ride']
- **Traits** arrangement `narrative` · density `sparse` · feel `tight_swing` · melody `minimal_motivic` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `static_vamp` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `cello` -21 dB · rev=0.3 · alternatives ['contrabass', 'sf:bassoon', 'tuba']
  - chords (chords): `piano` -23 dB · pan=-0.2 · rev=0.3 · alternatives ['organ', 'strings', 'epiano']
  - pad (pad): `strings` -28 dB · rev=0.4 · alternatives ['organ', 'solina', 'warmpad']
  - arp (arp): `marimba` -23 dB · pan=0.25 · rev=0.3 · alternatives ['piano', 'vibes', 'kalimba']
  - lead (lead): `marimba` -21 dB · pan=-0.25 · rev=0.3 · alternatives ['piano', 'vibes', 'clarinet', 'violin']
- **Mix** {'lufs': -15.0, 'air': 1.2, 'low': 0.5} · reverb 2.0 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 60, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'repetition': 0.95, 'simplicity': 0.2}

### Baroque organ toccata (`baroque_organ`)

Baroque organ toccata (Bach style): a big church pipe organ playing free, dramatic flourishes - fast 16th-note runs and broken chords over long pedal notes, sudden full-organ chords, pauses where the church rings out, harmonic minor and rubato throughout

- **Tempo** 66-84 BPM · **scales** harmonic_minor, minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'harmonic_minor': [[0, 4, 0, 4], [0, 3, 4, 0], [0, 6, 4, 0]], 'minor': [[0, 5, 3, 4]]} · chord_bars 1 · chord size 4
- **Song form** `toccata`: flourish 4 [bass, lead] (level=0.9) -> chords 4 [bass, chords] (level=1.0) -> runs 8 [arp, bass, lead] (alt) -> chords 4 [bass, chords, pad] (level=1.0) -> fugato 12 [arp, bass, chords, lead] -> coda 4 [bass, chords, pad] (cad, level=1.0) · form_scale 1
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R---------------` / `R-------R-------` · mode `pattern` · lowest note 26
- **Chord rhythm** `X-------........` / `X---....X-------`
- **Arp** {'rate': 4, 'mode': 'updown', 'oct': 4}
- **Lead rhythm** `xxxxxxxxxxxxxxxx` / `xxxxxxxx........` / `x.x.xxxxxxxx....` / `xxxxxxxxxxxx----`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `sparse` · feel `drifting` · melody `rhythmic_stabs` · bass `rolling_groove` · drop `none` · variation `theme_and_variations` · culture `concert_hall` · texture `massive_reverb` · rhythm `straight_16ths` · harmony `functional_tonal` · energy `emotional_arc`
- **Instruments**
  - bass (bass): `organ` -14 dB · alternatives ['organbass', 'upright', 'sf:acbass']
  - chords (chords): `organ` -17 dB · rev=0.6 · alternatives ['harpsichord', 'epiano', 'piano']
  - pad (pad): `organ` -24 dB · rev=0.6 · alternatives ['strings', 'warmpad', 'solina']
  - arp (arp): `organ` -22 dB · rev=0.6 · alternatives ['harpsichord', 'twang', 'guitar']
  - lead (lead): `organ` -17 dB · rev=0.55 · alternatives ['harpsichord', 'epiano', 'synthbrass']
- **Mix** {'lufs': -13.0, 'air': 0.8, 'low': 1.6, 'width': 1.3, 'gentle': True} · reverb 4.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.92, 'chord_center': 58, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'kick', 'suggest': '', 'rubato': 0.5, 'own_progs': True, 'no_transition_fx': True, 'melody_range': 0.9}
- **Sound brief** Church pipe organ only: pedal bass, full-organ chords, fast manual runs; very long reverb; rubato

### Minuet & trio (`minuet`)

Minuet & trio (3/4, Mozart / Haydn / Bach): an elegant courtly dance in binary phrases with ornamented repeats, a quieter contrasting trio, then the minuet da capo - strings, harpsichord or fortepiano, a pair of horns

- **Tempo** 104-132 BPM · meter 3/4 · **scales** major, minor · swing 0.5 (unit 16) · humanise 0.006
- **Progressions** {'major': [[0, 4, 0, 4], [0, 3, 4, 0], [0, 1, 4, 0], [0, 5, 1, 4]], 'minor': [[0, 4, 0, 4], [0, 3, 4, 0]]} · chord_bars 1 · chord size 3
- **Song form** `minuet`: A 4 [bass, chords, lead] -> A 4 [bass, chords, lead, pad] (var=dim, cad) -> B 4 [bass, chords, lead] (alt) -> A 4 [bass, chords, lead, pad] (cad) -> trio 8 [arp, bass, lead, pad] (alt, cad) -> A 4 [bass, chords, kick, lead, pad] (cad) · form_scale 1
- **Drums** **timp** `X...........` / `............`
- **Drum kit** (synth preset) · preset `default`
- **Bass** `R...R...R...` / `R.......F...` / `R...F...R...` · mode `pattern` · lowest note 36
- **Chord rhythm** `....x...x...` / `....x...x-..`
- **Arp** {'rate': 1, 'mode': 'alberti', 'oct': 5}
- **Lead rhythm** `x---x-x-x---` / `x-x-x-x-x---` / `x---x---x-x-` / `x-xxx-x-x---`
- **Build-ups** default `(category default)` · choices ['roll', 'triplet', 'hats', 'drumless', 'halftime', 'wash', 'pulse', 'tapestop', 'stops', 'pickup']
- **Traits** arrangement `narrative` · density `medium` · feel `tight_swing` · melody `long_lyrical` · bass `rolling_groove` · drop `emotional_swell` · variation `theme_and_variations` · culture `concert_hall` · texture `intimate_close` · rhythm `straight_16ths` · harmony `simple_pop_harmony` · energy `emotional_arc`
- **Instruments**
  - timp (kick role - the genre's low drum): `timp` -30 dB · rev=0.4
  - bass (bass): `cello` -20 dB · rev=0.3 · alternatives ['contrabass', 'sf:bassoon', 'tuba']
  - chords (chords): `harpsichord` -23 dB · pan=-0.2 · rev=0.3 · alternatives ['piano', 'strings', 'pizz']
  - pad (pad): `horn` -31 dB · rev=0.4 · alternatives ['strings', 'brass', 'sf:slowstrings']
  - arp (arp): `harpsichord` -25 dB · pan=0.2 · rev=0.3 · alternatives ['piano', 'harp', 'epiano']
  - lead (lead): `violin` -18 dB · pan=0.1 · rev=0.3 · alternatives ['flute', 'oboe', 'piano']
- **Mix** {'lufs': -16.0, 'air': 1.0, 'low': 0.5} · reverb 2.2 · sc_depth 0.0
- **Other rules** {'sc_release': 0.45, 'delay_beats': 0.75, 'kit_override': {}, 'snare_tracks': [], 'bass_gate': 0.6, 'chord_center': 62, 'strum': 0.0, 'voicing': 'close', 'lead_oct': 5, 'fill': False, 'ghosts': False, 'trap_hats': False, 'kick_track': 'timp', 'suggest': '', 'repetition': 0.65}
- **Sound brief** Violins (melody); harpsichord / fortepiano; violas & celli (pah-pah); basses; a pair of horns
