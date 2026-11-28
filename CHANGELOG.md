# Changelog

## 2.30.0
Better songs from every new seed, a tone match for 95 more genres, A/B picks that teach the app, and exports for releasing music.

- **Best of 6 for every new song.**
  - **What happens:** when you press Preview, Variations or Full song with a fresh seed, the app writes 6 candidate songs in about a second, without rendering them. It scores each one on genre fit, how singable and shapely the tune is, and how much the sections differ in energy, the same score the batch queue already used. The best one is rendered.
  - **What you see:** the seed box changes to the chosen seed, so Full song after a preview is still the same song and a shared song replays exactly.
  - **When it stays off:** a locked 🔒 seed, a loaded or shared song, or a tweak of the last result. You can also untick **best of 6** next to *quick preview first*.
  - **Why:** the score varies a lot between seeds of one genre (58 to 94 for trance), so keeping the best of 6 lifts the typical song.
- **Tone matched to the family's records, for 95 more genres.**
  - **Before:** 52 genres have a tone target measured from reference records. The rest had none.
  - **Now:** genres in a family with at least 3 measured genres get a gentle nudge toward their family's average balance: 40% of the way, at most 2 dB per band. This covers house and disco, techno and trance, drum & bass and breaks, dubstep and bass, chill and lo-fi, and hauntology.
  - **Checked first:** each measured genre's own target was hidden and its family's average used instead. In 83 of 90 test renders the song came out closer to the hidden target (3.6 dB to 3.0 dB average band error).
- **A/B picks teach the app.**
  - **In the A/B bar:** new **A is better** and **B is better** buttons. Each pick saves both songs' settings and sounds to `ab_picks.jsonl` (kept when you update), and the winner counts as a 👍.
  - **Report:** `python tools/ab_report.py` (or `--style trance`) shows which knobs and sounds the winners had compared with the losers.
- **Release exports** (new chips under *Full song exports*):
  - **Cutdowns (60 / 30 / 15 s):** for stock-music sites. Each one has the opening bars, then the hook (the first drop or chorus), then the song's own last bars and ring-out. The parts are joined on bar lines with short crossfades. Each edit fits just under its length.
  - **Seamless loop:** the whole song cut on its last bar, with the reverb and last notes folded back onto the start, so it repeats with no gap or click (for long loop videos).
  - **📦 Release folder:** one folder per song with the master, the cutdowns, the loop, the settings and a `release.json` (title, genre, tempo, key, length, loudness, instruments, files) for an uploader to read.
- **Faster test feedback:** a new few-minute check (`python -m tests.quick`) runs first on every push. The 16 long test jobs start only once it passes.
- **Changelog:** the two 2.23.0 entries are joined into one, and the 1.x history moved to `docs/CHANGELOG-1.x.md`.

## 2.29.0
Two new genres and two reworked ones from your three new reference sets: nine 2022 trance radio edits, five rally phonk tracks and fifteen melodic deep house tracks from one producer.

Every track was measured: tempo, key, chord loop, kick / bass / clap / hat patterns, section lengths, tone, loudness, punch, stereo width per band and how much the music pumps against the kick. Generated songs were then measured the same way and tuned until they landed near the records.

- **New genre: Modern trance (2020s main stage).**
  - **What the records do:**
    - 132–140 BPM;
    - short intros and one big breakdown in the middle (26–47 bars), carried by piano, pads and the lead;
    - a rolling bass: off-beat 8ths, a 16th gallop or straight 16ths;
    - +5 dB of pump per beat;
    - very wide upper mids from stacked saws, with a mono sub;
    - loud, about -7.6 LUFS;
    - much brighter than the older trance in the app.
  - **What the genre does now:**
    - it follows those numbers;
    - it adds a radio-edit and an extended layout;
    - it picks the references' keys;
    - each song chooses its bass style.
- **New genre: Rally phonk.**
  - **What the records do:**
    - 124–128 BPM, with an occasional 150 sprint;
    - 2–3 minutes long;
    - a hard kick on every beat plus extra 16ths;
    - a driven 808 bouncing between two notes;
    - busy clipped claps and hats;
    - squashed on purpose: about 8.6 dB crest, -7 LUFS;
    - narrow, with a mono low end.
  - **What the genre does now:** it follows those numbers. The existing drift phonk stays as it is; it sits much faster, at 145–165.
- **Melodic deep house (emotive and sunny), checked against fifteen more of that producer's tracks:**
  - **Breakdowns:**
    - **On the records:** the main breakdown runs 24–36 bars.
    - **Now:** emotive deep house's breakdown is 24 bars (was 16) and sunny melodic house's is 24 (was 12, with an 8-bar build).
  - **Intro:** emotive deep house now opens with 8 bars of percussion and pads before the kick, like the records.
  - **Pump:** it is deeper, closer to the records' +6.7 dB.
  - **Loudness:** both master about 1 dB louder, closer to the records' -7.4 LUFS.
- **New sounds:**
  - **Stack lead:** 9 wide saws, a sub octave and a pluck on the attack, the modern trance lead.
  - **Gallop bass:** a tight rolling trance bass whose filter snaps shut, so 16ths stay punchy.
  - **Rally saw:** a folded, clipped, crushed phonk lead.
  - **Growl 808:** a driven 808 that growls in the low mids.
  - **Pure pluck:** a bright, round melodic-house pluck made for dotted-8th delays. It is now in the emotive and sunny melodic house rotations.
- **Mastering for genres that are loud on purpose:**
  - A genre can now set how much punch it keeps (rally phonk, modern trance and melodic deep house sit at 5.6–6.8 dB, like their records).
  - The production pass no longer turns those songs down 1 dB for being "squashed".
  - The mix check only calls a song squashed below its genre's own floor.
- **Bass phrasing on "Genre decides"** no longer adds pickups and fills in four-on-the-floor genres (house, trance, techno), whose basslines roll rather than fill. "Always" still adds them.

## 2.28.0
- **Sunlit electronica and dive electronica re-measured against 18 more references from the same artist**: 8 from the live-band album and 10 from the dreamy, programmed one.
  - **Two-chord sways:** most of these songs rock between just two chords, a bar or two each, for the whole track. Five new harmony choices:
    - IV–I sway (the most common: 4 of the 10 dreamy songs);
    - I–IV;
    - I–vi;
    - iii–V;
    - vi–V.
  - **Faster live-band songs:** half of the live-band album runs 127–140 BPM, not just 112–122. Sunlit electronica can now also land around 128 or 136.
  - **Keys like the records:** both genres now pick from the references' keys, A and E♭ most, then F♯, A♭, C and B.
  - **Tone per album:**
    - The live-band sound sits lighter in the deep sub and fuller at 120–250 Hz.
    - The dreamy sound is fuller in the low mids.
    - Both are darker at 1–2 kHz than the earlier, mixed measurement.
  - **Loudness:** both master closer to the records, about -9 LUFS for the live band and -10 for the dreamy one. They were about 1 dB quieter.

## 2.27.0
- **A theme you can follow through the whole song.** The hook (the lead's first two bars in the first drop or chorus) now comes back where you expect it:
  - **Foreshadow:** its opening notes play softly at the end of a long intro, before it really arrives.
  - **Breakdown:** the first breakdown or bridge restates it at half speed, every note twice as long, over the open pads.
  - **Farewell:** its first bar plays once more, softly, near the end of the outro.
  - **Final lift:** the last big section is bigger than the first. The lead gets a second voice a third above it for the second half.
  - All of it stays in key. It's skipped for through-composed scores, exact forms, ornamented / quarter-tone melodies, and Development: off. Each song lists what it did.
- **Extra instruments can play their own parts** (Parts panel > + Add instrument > "Own line: ..."), instead of only doubling a part:
  - **Fanfare calls:** a short brass-style call on the chord at the top of each big section and every 8 bars inside it.
  - **Runs into sections:** a quick rising scale run into each new section, like a woodwind or string flourish.
  - **Ostinato:** a busy 8th-note figure on the chord tones under the fuller sections, like pizzicato, mallets or guitar.
  - **Answers the melody:** echoes the lead's last notes in its gaps, an octave away.
  - **Held notes:** long notes on the chords' top voice, moving by step, like a string or choir pedal.

  Every line follows the song's chords and key, and the octave setting moves it.
- **The other classic drum machines are modelled too.** The old sounds stay in the drum menu as "classic sound, before 2.27".
  - **808:** a pure, barely swept boom with the long smooth tail, a two-tone snare with its own snappy noise, the analog clap and six-oscillator hats.
  - **606:** the analog kick, snare, clap and hats, smaller and brighter.
  - **707, LinnDrum, DMX:** these machines played recordings of real drums. Their kick and snare are now modelled as acoustic hits (beater slap, skin and shell, stick and wires), then crunched by each machine's own bit depth.
- **🎹 Play any sound** (transport bar):
  - Open it to play any instrument on your computer keyboard (A W S E D F T G Y H U J K O L P ;, with Z / X for octave), by clicking the on-screen keys, or from a plugged-in MIDI keyboard.
  - The notes are prepared as soon as you pick a sound, so they play straight away.
- **Genre DNA slider:** when you blend exactly two styles, a slider sets how much of each (0-100 %).
  - As you slide, the second style takes over the mix and space first, then the lead and arps, the chords, the bass, the arrangement and last the drums.
  - The tempo and swing glide between the two styles, unless they're a half / double-time pair.
  - Picking a source for a part yourself still works as before.

## 2.26.0
- **Melodic deep house learned from 18 more reference tracks** (one producer's melodic deep house). The emotive deep house, sunny melodic house and melodic house genres changed in four ways:
  - **Two-chord vamps:**
    - **What the records do:** almost every track loops two chords a bar each (ii-V, vi-IV, IV-I, V-iii, vi-I) for the whole song. Before, these genres played four-chord pop progressions.
    - **Now:** those vamps are what these genres mostly pick. Emotive deep house plays only them, plus two of its old progressions.
  - **Keys:** the references sit mostly in F♯ minor / A major and G major, then E, C, F, B♭ and E♭. Emotive deep house now picks from those keys.
  - **Arrangement:** the extended mix is 120 bars (was 152), matching the references (104-144 bars), with a 16-bar breakdown in the middle.
  - **A beach in the background:** a new built-in texture of waves rolling in every 7-12 s, with birds chirping now and then. Field recordings like this are part of the style. These genres pick it, waves, air or nothing, per song.
- **Christmas genres play real instruments only.**
  - Every part in the orchestral and band Christmas genres now plays an instrument that has a recording.
  - Synth stand-ins are replaced by the nearest real one: a sine or Moog bass becomes a double bass or upright, a warm synth pad becomes strings, a music box becomes celesta, a children's choir becomes the recorded choir.
  - Your own picks stay. Christmas house and Christmas lo-fi keep their electronic sounds.
- **✂ Chop a break into a kit** (Sound panel > Drum voices):
  - Load any drum break or beat (WAV, MP3, FLAC, AIFF ...). Studio Lab finds its hits and keeps the best kick, snare, closed hat and open hat.
  - They go into your drum library (pick them for any drum voice). With "play it on this song" ticked, they play this song's kick, snare and hats straight away.
  - **RX2 / REX files can't be read.** They are a closed ReCycle format only its own library opens. Export the loop as a WAV from ReCycle, Reason, FL Studio's Slicer or most DAWs, and chop that.
- **DnB drum sounds now really change the kick and snare.**
  - **The problem:** in the break-based DnB genres (anthemic, rollers, liquid ...), the kick and snare you hear are a two-step layered on top of the break. That layer always came from the genre's preset, so picking a drum machine or a Drum voice only changed the quiet, filtered break underneath.
  - **Now:** your drum machine and your kick / snare Drum voices play the layer, as themselves. When you pick one, the break's own kick / snare drop further back. Each song also rolls its own layered kick and snare from machines that suit the style.

## 2.25.0
- **Trance pumps like the records.** The pads, chords, arp and now the lead duck under every kick and swell back
  across the beat, the classic trance sidechain. Measured against the trance reference set, the music swelled back up
  by about +1.7 dB per beat on the records and not at all in ours (-0.8 dB); club, anthem and classic vocal trance now
  swell about +2.3 dB, progressive about +3 dB. 90s trance pop's pads and lead are sidechained for the first time.
- **Melodic deep house tuned against 21 reference tracks** (one producer's melodic deep house). Emotive deep house
  and sunny melodic house now:
  - pump much harder (+3 to +4 dB of swell per beat, was 0 to +1; the records swell about +5);
  - are much wider (shakers, congas, hats, rims and plucks panned out, pads and chords wide; they were nearly mono);
  - sit darker on top with the sub leading the low end, like the records;
  - master about 1 dB louder in the main sections, and swing a little more (0.55, the records' median).

## 2.24.3
- **Trance tuned against real records.** Eight trance genres were measured against a set of ten trance tracks
  (2000s club and anthem trance, a progressive set, a 90s dream-trance single) and their mastering targets now
  follow them: the low end sits in the kick and bass (60-120 Hz) instead of the deep sub, and the mids carry more
  of the mix. Club, anthem and classic vocal trance match the references to within about 1 dB per band on average
  (they were 3-4 dB too heavy in the sub and too thin in the mids before).
- **Learn from audio reads tempo more reliably.** It now trusts the analysed tempo and only checks it for half- or
  double-time mistakes, instead of trying 3:2 and 4:3 re-readings of the grid. All ten trance references came back
  at the right tempo (before: several at 1.5× or 3/4 speed).

## 2.24.2
- **No more Mac installers.** Releases now build only the Windows installer. GitHub kept failing to find a Mac machine
  to build the Apple Silicon one on, and that held releases up. Studio Lab still runs on a Mac from the zip with your
  own Python (`Start Studio Lab (Mac).command`).

## 2.24.1
- **🎼 Learn from audio.** The Learn button now also takes a recording (MP3, WAV, FLAC, OGG ...) as well as a MIDI
  file. From the audio it learns:
  - **Tempo:** tried against the usual confusions and kept where the grid catches the most onsets.
  - **Key:** from sustained, harmonic energy. It got the right scale notes in 37 of 40 test songs; the older reference
    analysis got 29.
  - **Swing.**
  - **Drum grooves:** kick, snare/clap and hats per 16th step, as the consensus groove plus the bars that repeat.
  - **Chord loops.**

  Like MIDI, the result can be added to the current genre or saved as a ★ My genre. On test songs, house, drum &
  bass, trap and rock came back with the right tempo and kick and snare/clap patterns (drum & bass and rock's kicks
  only roughly). Swung grooves (boom-bap, Afrobeats) can read at double or 1.5× tempo, and the result says so. Sounds
  aren't learned.

## 2.24.0
- **👍 / 👎 now steer the sounds.** Rating a song used to steer only which genre "🎲 Surprise me" picks. Now:
  - New songs in that genre pick the sounds it played more often (after a 👍) or less often (after a 👎). Ratings in
    other genres count at half weight.
  - In a test, parts matching a liked song's sounds went from 24 to 41 out of 40 songs, and from 24 to 9 after a 👎.
  - Nothing becomes certain or impossible: weights stay between a tenth and 3×.
  - A song's preview and its full version keep the same sounds.
  - The ♡ on a single part now records that part's actual sound, not its display name, so it counts too.
- **Own drum machines for 92 more genres.** 69 genres shared the same "soft" drum preset and 33 the same "punchy" one.
  The genres on those generic presets now each get a machine or kit that fits their family (909s and Linns for house,
  real kits for Celtic and Latin, 808s and phonk kits for trap and dubstep, vintage and brushes for lo-fi ...). The
  machines rotate within each family so neighbouring genres differ, and none shares its parent genre's machine.
  Genres whose preset was a deliberate choice keep it.

## 2.23.1
- Toy soldier march: the piccolo tune sat under the horns. It's balanced now (this stopped 2.23.0's release).
- **Fix: real orchestral recordings played an octave too high.** The sample libraries name their notes an octave below
  the pitch they actually sound. I measured every instrument and articulation, low and high, with pitch tracking and
  autocorrelation. Studio Lab took the names at face value, so every recorded note came out an octave above the
  written one. That made trumpets shrill and "off", and a melody jumped octaves wherever it moved between a recorded
  note and the built-in sound.
  - Octave high (now fixed): all brass and woodwinds; the violin, viola, cello and bass sections; glockenspiel,
    vibes, marimba, xylophone, tubular bells, kalimba, sax, harmonica and ocarina; harpsichord and the upright piano.
  - Octave low (now fixed): the twangy electric guitar, which was named at written guitar pitch.
  - Already right: the grand pianos, FM piano, harp, solo violin, acoustic guitar, electric bass and double bass.
  - Installed libraries are fixed by the update itself, with nothing to download again.
- **Fix: Dexed never played its sounds.** Dexed starts on a bank of synth patches with no bass, electric piano,
  marimba or bells, so selecting those by name failed and every Dexed part fell back to the built-in sound. Studio
  Lab now sets the whole FM voice itself. There are nine of its own patches: electric piano, clav, marimba, vibes,
  tubular bells, steel drum, a round bass, organ and koto.

## 2.23.0
Brassier, bassier orchestral Christmas music.

- **Three new orchestral Christmas genres**:
  - **Christmas brass fanfare**: trumpets on the tune, horns and trombones on the chords, a tuba with the celli and
    basses, and a string ostinato.
  - **Christmas overture**: the strings carry the whole piece, and the brass swells in for each big statement.
  - **Toy soldier march**: tuba and low strings on the oom, horns and trombones on the pah, piccolo and snare.

  Their balance was calibrated on a reference set of orchestral Christmas film-score cues:
  - The low strings sound almost all the time (about 90%).
  - The cello, horn and trombone range holds about half the energy, and there's very little top end.
  - The brass carries most of the loud passages.
- **String backbone for the orchestral Christmas genres.** The low strings no longer drop out: where a section had no
  bass, the celli and basses keep a soft pizzicato pulse on the downbeats. In the fuller genres (joyful, mischief,
  festive cinematic, carol choir, memory theme, flight, finale, sleigh ride) a tuba doubles the bass and a brass
  section doubles the chords in the choruses and climaxes. The gentle ones (lullaby, magic, sneak) get the low
  strings without the brass.
- **🎺 More brass / 🎻 More strings** switches (Rhythm card, "Orchestra"), for any genre:
  - **More brass**: a tuba and brass section in the big sections, and soft horns elsewhere.
  - **More strings**: the low strings never drop out, celli double the bass and a string section plays the chords.

**Also in 2.23.0:**
Richer harmony and bass phrasing for any genre, a rebuilt set of sunlit-electronica genres from a second look at the
reference records, and a breaks-techno genre.

- **Richer harmony** (Harmony control: genre decides / richer / plain). Songs can now use chords from outside the key,
  the way songwriters colour a plain progression:
  - **Borrowed chords:** in a major key the IV can turn minor, and the vi, iii and vii can become the flat VI, flat III
    and flat VII. In a minor key the iv can turn major and the v can become the major V. Only the turnaround of each
    8-bar phrase is coloured, and every repeat of a section does it in the same place. All the parts move together,
    the melody included, so nothing clashes.
  - **Bass inversions:** where the bass would jump between two roots, it plays the new chord's 3rd when that is a step
    away, so the line walks instead of leaping.
  - **Pedal notes:** in intros, breakdowns and outros, the bass can hold the home note while the chords move over it.
  - The result card says what a song used, e.g. "borrowed iv · bass inversions".
- **Bass phrasing** (Bass phrasing control: genre decides / always / never):
  - A pickup leads into the next chord at the end of every 4-bar phrase, and a bigger fill comes at the end of every 8.
  - Walking genres also step into every chord change.
  - Dubstep-style wobbles talk in 4-bar phrases: the call, an answer twice as fast, the call again, then a triplet
    stutter that stops dead.
- **The batch generator** can now spread harmony and phrasing across a batch.
- **The sunlit-electronica genres, re-measured.** I went back over the twelve reference records, with your notes on the
  two albums in mind, and measured how the parts relate:
  - chords keep about 70% of their notes from one chord to the next;
  - the bass plays 2.5 to 3.5 different notes a bar and walks into the changes;
  - the snare cracks clearly over the guitars;
  - the hats lean back with a light swing;
  - there is no extra drum fill every 8 bars;
  - the dreamy ones pump on every beat, the band ones much less.

  The genres now follow these numbers:
  - **Sunlit electronica** is now the live-band version:
    - a drummer with ghost notes, laid-back hats and a ride in the big parts;
    - a picked bass guitar that walks into the chord changes;
    - two clean neck-pickup guitars interlocking, one picking 8ths into a dotted-8th delay and one answering high and
      sparse;
    - pads underneath;
    - a soft synth melody now and then.
  - **New: Dive electronica** is the programmed, synth-led version:
    - soft sample-like drums on a steady pulse;
    - pads pumping on every beat;
    - round analog arpeggios carrying the motion;
    - a round mono bass pushing 8ths;
    - the guitar mostly as atmosphere.
  - **Daydream downtempo:** a laid-back groove, a snare that cuts through, and the neck-pickup guitar.
  - **All three:** one high guitar or glass note is held over each loop while the chords change under it. It is
    always a note of every chord it sits over.
- **New sounds:**
  - **Round arp:** a soft analog arpeggio with no click.
  - **Neck-pickup guitar:** warm, compressed and chorused.
  - **Reverse swell:** a pad tone played backwards.
  - **Dive kit:** soft programmed drums.
  - **Sun room kit:** its snare now has a clearer crack.
- **New genre: Steel breaks** (breaks techno and electro), from your two newest reference tracks:
  - tight, steely breakbeats layered with a hard kick and sharp claps, over a heavy mono sub;
  - a squelchy acid line, with one or two dark stabbed chords instead of a progression;
  - long DJ intros and outros, and hard pumping;
  - two moods: hypnotic at about 140, or a faster rave-breaks tool at about 155 with hype-man shouts.
- Each genre can set how hard the mastering may press on the low end. Steel breaks uses this to stay loud.

## 2.22.5
No more brass-sounding basses in the African genres.

- The FM basses use the textbook FM brass recipe: they hold a bright tone through the whole note, about 6-9 times
  their fundamental, where round basses sit at 1-2 times. On a bassline they sounded like a tuba or brass section.
  They had become the African genres' most common bass: a rule from 2.3 swaps bass guitars out of Electronic
  genres, and it was handing several African genres the FM bass instead.
  - No African genre uses an FM bass now, as its main bass, among its options or in a wobble genre's plain drops.
  - Coupe-decale plays the home-keyboard bass, the village synth genre a tri bass and mahraganat a distorted 808.
  - Tsonga disco, funana and the village party keep their electric bass guitar, as bands of those styles do.
- The home-keyboard bass (singeli, Kinshasa electronics, balani show, coupe-decale) now has a short rubbery attack
  and then a round tone, instead of a held, brassy one.

## 2.22.4
Fewer plucks, guitars and wobble basses in the African genres.

- **Plucks and guitars**: plucked synths and guitars had spread into most African songs' arps, leads and chords.
  They now make up about 3% of those parts. Before, they were in about a third of the arps and a sixth of the chord
  parts. The parts now go to the region's instruments:
  - Afrobeats: kora.
  - Afrobeat: clavinet.
  - Highlife and soukous: marimba.
  - Village party: balafon.
  - Village synth and afro wobble: the home-keyboard marimba.
  - Bacardi house chords: a stab.
  - Amapiano family: kalimba.
  Guitars stay where they are the style (soukous' lead, highlife's and afrobeat's rhythm guitar), and as rarer
  choices elsewhere. Highlife and soukous also play a shekere now, like afrobeat.
- **Wobble bass**: in afro wobble, kuduro wobble and Shangaan wobble, only the final drop wobbles (with one drop, its
  second half). The earlier drops get a plain bass. Log drums stay in amapiano, and wobble chops are gone from kuduro.
- Internal: the 2.22 African genre changes now live in each genre's own definition, and the sound lists in
  `pool_variety.AUDIT_2224`, instead of being patched on afterwards.

## 2.22.3
An instrument check of all 27 African genres.

- **Fixed instruments**: the ngoni clicked on every note and its low notes sounded an octave or a fifth too high
  (the fundamental was filtered away). The mizmar had a DC offset, and the thumb pianos (mbira, likembe) could
  stop while still ringing. All fixed.
- **New drums**: udu (Nigerian clay pot drum) and dundun (the djembe ensemble's bass drum, with its bell).
- **Afrobeat** plays a shekere instead of a studio shaker. **Highlife** plays its bell pattern on an agogo.
  **Afrobeats** gets a talking drum, and **Afro house** gets a djembe. **Shangaan electro** gets the party
  whistle. **Balani show** gets a dundun, and **Afro 3-step** and **batida** get an udu.
- **Better sound choices**: kora, balafon and mbira are now options in Afrobeats, Afro house and amapiano, and
  ngoni and kora in the village party. Shangaan electro's bass choices are keyboard basses (home-keyboard FM bass,
  organ bass) instead of deep-house saws, and it can use the home-keyboard marimba and lead. Kuduro gets the
  kuduro stab.
- Kuduro wobble and Shangaan wobble: re-rolling a part no longer swaps away from the genre's own sound.

## 2.22.2
- **Fix (Windows): the app could freeze right after loading.** Windows let a new sound engine start on the same port
  as one left over from an earlier session (after an update restart or a window closed hard). The main screen loaded
  from one engine and then talked to the other, which refused it. Each engine now gets a port of its own, skipping any
  port something else already answers on.

## 2.22.1
- The Mac installer build retries when macOS reports the disk image as busy (this transient error stopped the 2.21.1
  release from publishing).

## 2.22.0
More fast African electronic dance music, new instruments and drums for it, and a lead that sometimes starts early.

- **14 new genres** on a new **Afro Street & Rave** shelf (Afro 3-step, Bacardi house and kwaito join Afro & Amapiano):
  singeli (200-230), Tsonga disco, kwaito, Bacardi house, Afro 3-step, batida, tarraxinha, mahraganat, Kinshasa
  electronics, balani show, coupe-decale, funana, and two afro-wobble hybrids - kuduro wobble and Shangaan wobble.
  Each has its own drums, bass, sounds and drum machine, so none of them is a copy of a neighbour.
- **New instruments** (all synthesized, no samples): mbira (buzzing thumb piano), electric likembe (fuzzy amplified
  thumb piano), home-keyboard marimba, home-keyboard lead and FM bass, kuduro stab, ngoni (West African lute) and
  mizmar (Egyptian shawm). **New drums**: djembe (tone, slap, bass), talking drum, shekere, agogo (high and low),
  ferrinho scraper and a party whistle.
- **Lead from the start (African genres)**: in about 4 songs out of 10, the lead comes in quietly from the first bar -
  sparse and about 12 dB under its full level - long before its real entry.
- **Plugins**: the new instruments play through the plugins Studio Lab already installs (RipplerX, Dexed) and the
  ones it can find on your computer (TAL-NoiseMaker, OB-Xf, Kars) when those are set up. OctaSine (free FM synth) and Kars (plucked string) are now
  recommended in the plugin guide for your DAW.

## 2.21.1
- **Generating never overwrites a song.** When a song with the same file name is already in your output folder
  (same name, genre, key, tempo and seed - e.g. "New sounds", or the same seed with other settings), the new one is
  saved as `..._seed5 (2)`, `(3)` ... and the earlier one stays. Previews still replace their own scratch files.

## 2.21.0
Your own drums, learning from MIDI files, and genres that sound less alike.

- **🎼 Learn from MIDI** (next to 🎯 Match a reference): pick a song's MIDI file and Studio Lab reads its tempo, key,
  chord loops (as scale degrees) and its drum and bass rhythms (fills and build-up rolls left out). Then either
  **➕ Add to <genre>** - the genre plays those grooves among its own from now on - or **★ Save as my genre** - a new
  genre built on the one you're on, at the file's tempo, playing only those grooves, listed under **★ My genres**.
  What you taught is kept with your samples (survives updates) and listed with *forget* / *delete* links; forgetting
  puts the genre back exactly as it was. RIFF-wrapped .rmi files now read too.
- **Your own sample on any single drum**: Drum voices now has eight voices (kick, snare, clap, hi-hats, ride, crash,
  rim, shaker); each can come from another drum machine, a real kit or **one of your samples** - "＋ Load a sample for
  this drum…" right in the menu. Drum samples can have any name now (a library), not just the slot names.
- **Beat library** in Drum style: 19 classic beats (four on the floor, disco, 2-step, breakbeat, boom bap, trap,
  half-time, drum & bass, Jersey club, dembow, Afrobeats, rock, Motown, shuffle, train beat, bossa, swing, soft
  pulse, minimal) you can put on any genre's sounds; a break genre then plays the beat instead of its break.
- **Genres that sounded like a neighbour now differ**: Wonder plays the celesta, harp and horn its description
  promised (it had Storybook Score's sounds exactly); Celtic Punk gets the folk polka two-beat (kick on 1 and 3, snare
  on the off-beats) and its own kit instead of plain punk's drums; Celtic Session plays a pub guitar strum and
  mandolin instead of the reel's bouzouki and banjo; Anthem Trance gets its own supersaw anthem lead, pluck arp,
  classic trance kit and quarter-note ride instead of the club remix's; own kits for Progressive Trance (909),
  Cinematic Trap (hard), Rage (phonk 808), Plugg (soft), Sunrise Chillwave (vintage) and Switch-up Mallets (707).
- **tools/genre_twins.py** scores how alike every pair of genres is built (tempo, swing, kit, drum patterns, bass
  line, sounds); tests.features now fails if a new genre is a near-copy of an existing one.
- CI: the slow smoke render runs as 8 parallel shards instead of 3 (about 10 minutes instead of ~28).

## 2.20.3

- Fixed: turning a part down barely changed it in house, techno, dubstep and boom bap. Setting any part level switched
  the learned mix balance off, so the synths jumped back up ~5 dB and cancelled most of your change (a -6 dB lead came
  out about -0.7 dB, and the chords got louder). The balance now always applies, measured as if you hadn't moved
  anything, and your levels go on top: -6 dB on the lead is exactly -6 dB, and the other parts stay put.
- This also unblocks the 2.20.1 and 2.20.2 updates, which had not been released.

## 2.20.2

- The stepper sub (stepsub, the swelling "womp" bass) came up too often: it stays in its genres, but is now picked far
  less (about 2 songs in 100 in the 140 genres), and Vocal Stepper 140 now leads with a plain deep sub. Starring it as a
  favourite still brings it back as often as you like.

## 2.20.1

- Learned mix balance now measures the render the same way the records were measured (an RMS envelope, not raw
  power), so it no longer over-cuts the bass. Measured after the fix, against the real-record medians
  (bass / synths vs drums): house -9.2 / -11.9 dB (records -7.5 / -17.8; before -6.3 / -5.0), deep dubstep +2.8 / -13.3
  (records +1.3 / -12.4; before +5.1 / -16.2), boom bap -4.0 / -9.0 (records -2.2 / -9.3).
- Exported stems now include the learned balance, so they still add up to the mix.

## 2.20.0 - learned from real stems

Studied the stems and MIDI of ~60 real records (house, techno, 140 dubstep, hip-hop) with a new analyser
(tools/stem_study.py: tempo to 0.1 BPM, drum grids and swing, 8-bar structure, bass register and wobble, synth tone,
sidechain pump, echo, mix tone) and changed the app from what it measured. Only measurements are used, no audio.

- Mix balance learned from the records: house, techno, dubstep and boom bap now sit bass and synths against the drums
  the way the records do (house synths ~15 dB under the drums instead of ~5). Partial, capped nudge; your own part
  levels always win; trance, melodic, vocal and pop styles are left alone.
- 4 new synths modelled on the stems: rollbass (rolling house bass), stepsub (140 half-time sub with half-note swell),
  pumpstab (detuned house/techno stab), dustkeys (dark boom-bap keys) - added to the matching genres' sound pools.
- 3 new genres from the measured grids, forms and sidechain: Rolling Pump House, Peak-Time Techno, Vocal Stepper 140
  (408 genres).
- Boom bap: quarter-note echo on keys and lead (6 of 15 measured keys stems had one).
- Genre match % no longer goes negative.
- tools/stem_report.py: per-song report for multitracks and .stem.mp4 files.

## 2.19.0
Radio edit, original and extended mix of the same song - in the editor and when you export.
- **Also export 📻 radio edit / 🪩 extended mix** (under the Full song buttons): ⬇ Full song also saves the same song in those lengths, next to the original (`…_radio-edit`, `…_extended-mix`). Your ticks are remembered.
- **Length in the song editor**: 📻 Radio edit · Original · 🪩 Extended mix, plus − Shorter and + Longer, with the running time shown. The new arrangement appears on the timeline, where you can keep editing it, then 🎧 Hear changes or ⬇ Full song.
- **They're the same song.** A version only changes which of the song's own sections play and how long the intro and outro run, so the melody, chords, bass, drums, sounds and mix stay the same (a few hi-hat and arp details follow the new neighbouring sections).
  - **Radio edit** aims for about 3 minutes: a short intro and outro first, then, only while it's still too long, trims the second verse, the solo or bridge, and repeated choruses. It never cuts the first real chorus or drop or the last one, and never leaves a build-up leading into nothing.
  - **Extended mix**: dance music gets a 16-bar DJ intro (drums only) and DJ outro (drums and bass) for mixing, plus one more build and drop. Songs get one more verse and chorus before the ending.
- An edited song (sections changed) now always gets its own file instead of replacing the original.

## 2.18.0
A cleaner Sounds & instruments window with one button for everything, and a reworked song editor (its "play with changes" button really plays your changes now).
- **Sounds & instruments → ✅ Setup**: one checklist of every sound Studio Lab can use - recorded instruments, the General MIDI library, free synths and effects, plugin support - with a ring showing how much is ready.
  - **⬇ Get everything** downloads and installs every free item that can be installed automatically, in one go, with one progress bar. One failure doesn't stop the rest, and pressing it again retries what failed. Closing the window doesn't stop it.
  - **🔍 Check & repair** looks inside every installed library and plugin for missing or damaged files and fixes them.
  - Single items still have their own **Get** button. Things the app can't install for you (BBC Symphony Orchestra, LABS, Vital, TAL …) are listed separately as optional, with a link. Once BBC SO or LABS is found, **✨ Detect my instruments** appears right there.
  - Shorter tab names: Setup · Browse · Recorded · Free synths · My plugins · Orchestra · My samples · DAWs.
- **Song editor, reworked**:
  - **Fixed: "Play with changes" played the original song.** The edited version was saved over the original's file at the same address, so the player kept the old audio. Edited versions now get their own file, and every render a fresh address.
  - The actions stay at the top while you scroll: **▶ Original / ▶ Edited** (flips between them at the same spot; key **B**), **🎧 Hear changes**, **⬇ Full song**, **🎲 New sounds**, **↺ Undo all**.
  - **Every change is listed** at the top ("Bass → Saw bass", "Kick -6 dB", "sections", "4 note edits"); click one to undo just that. Changed parts are highlighted, each with its own ↺.
  - Sound, level, section and note changes are now one set: before, "Full song with edits" in the section panel dropped your sound changes, and the editor's own full-song button dropped your section changes.
  - Hearing your changes keeps your tab and scroll position and starts playing the edited version straight away.
  - The duplicate buttons from the song card are gone from inside the editor.
- **A sound you pick changes only that part**: picking a sound for one part used to also reshuffle the sounds of other parts, and which parts switch sounds between sections. Each part now draws its choices on its own. (So the same seed can pick slightly different sounds than in 2.17.)

## 2.17.0
Second batch of the improvement list: safer updates, faster renders, a check for every genre.
- **Updates only install tested versions**: a release is now made only after the full test suite has passed on that exact commit, and the app updates from the latest release (not the newest code on the branch). Every download is checked against the release's SHA-256 checksum before anything is replaced; a download that doesn't match is refused. (Want the newest code anyway? Set `"channel": "latest"` in `update.json`.)
- **Quick preview first**: ⬇ Full song now plays a short preview of the very same song within seconds, while the full version renders in the same job. Switch it off with "quick preview first" under the buttons.
- **Faster renders**: filter sweeps that hold still run as one long pass instead of hundreds of tiny ones, silent stretches of a part are skipped, the phaser runs its four stages in one go, the multiband squash uses one filter fewer, the auto-wah steps in 3 ms. Same sound (differences are 40-50 dB down) - except the phaser, which loses a faint buzz its old stepped feedback added.
- **Less memory on long songs**: the rendered-part cache now has a size limit (1.2 GB by default, `STUDIOLAB_CACHE_MB` to change) instead of holding up to 40 full parts.
- **A check for every genre** (all 405, in about half a minute, run on every push): tempo inside the genre's range, the key in one of its scales, playable note ranges, a sensible length, every part the song form brings in actually plays, the same seed gives exactly the same song, and each drum part still follows the genre's written patterns (and the chords stay in key) as closely as before. It also keeps the genre counts in the README and genre lists true.
- **Docs up to date**: README, docs/GENRES.md, GENRE_LIST.txt and GENRE_SPEC.md regenerated - 405 genres.

## 2.16.0
First batch of the improvement list.
- **Melodies turn back after a leap**: after a jump of a fourth or more, the next note now steps back the other way - the oldest rule of good tunes - instead of zig-zagging or climbing on.
- **The bass walks into chord changes** (rock, country, funk, soul, pop, jazz ... - played-bass genres): the last 8th before a new chord often becomes a scale step or half step leading into the new root.
- **Songs quote themselves**: the bridge can open with the verse tune a fourth higher, and the outro can bring back the intro's figure.
- **Orchestra seating**: orchestral parts sit where they would in a concert hall - violins left, violas centre, celli and basses right, harp far left, celesta right, horns behind on the left, trumpets / trombones / tuba behind on the right, timpani and percussion at the back (a touch more distant) - wherever the genre didn't place a part itself.
- **Cleaner low end outside club music**: in non-electronic genres the duck under the kick now only takes the low band (under 180 Hz) of the other parts, so the bottom is clear without any audible pumping.
- **Batch generator: 🏆 make 3× as many, render only the best**: every candidate is composed (no rendering, well under a second each), scored - the genre check, how singable and shapely the tune is (range, steps vs leaps, one clear high point, a rhythm that comes back), how much the sections differ - and only the best third per genre is queued for rendering.
- **Updates can't leave you stuck**: after an update, the first start checks the new version actually comes up; if it doesn't, Studio Lab puts the previous version back by itself and starts that instead.
- **Problem reports** (Options → Report a problem) now include the start-up log and the update state.

## 2.15.1
**Four more classic family-film Christmas score genres** (Orchestral → Christmas), in the style of the big 90s holiday-comedy scores:
- **Christmas Memory Theme** - the tender, nostalgic carol: celesta alone, a children's choir humming long notes, an oboe / flute tune over warm strings and harp, major-seventh and borrowed minor-iv chords, a soaring climax, back to the celesta.
- **Christmas Sneak** - the tiptoeing-burglars cue: pizzicato strings and a staccato bassoon creeping through a minor scale, a sly clarinet, celesta winks, soft timpani footsteps and a brass sting.
- **Christmas Flight** - soaring over the snowy town: a fast, sweeping 3/4 with harp runs, horns and trumpets on a heroic tune, the children's choir above, glockenspiel glitter and a key change to a triumphant last chorus.
- **Christmas Finale** - the bells-and-choir happy ending: tubular and church bells, full choir and pipe organ, brass fanfares, a key change up and a huge final chord.

## 2.15.0
**Eight new Christmas genres**, grown from the Christmas ones already here - each with its sleigh bells, and its own sounds kept:
- **Christmas Swing (big band)** - walking upright bass, brushed swing, a brass section answering a sax or trumpet tune, celesta sparkle.
- **Christmas Wall of Sound (60s pop)** - the boom, boom-boom, crack beat, sleigh bells and tambourine on every 8th, castanet clicks, hammering piano, a wall of strings, glockenspiel doubling the hook, lots of echo.
- **Rockin' Christmas (rockabilly)** - a fast shuffle with slapped upright, twangy lead, boogie piano and sleigh bells.
- **Sleigh-Ride Gallop (orchestral)** - a bright 2/4 gallop with woodblock hooves, sleigh bells, pizzicato, a cheeky trumpet tune doubled by celesta, horn calls and whip-crack crashes.
- **Christmas Lullaby (music box)** - a hushed, rocking 3/4 with a music-box tune, harp, soft strings and flute.
- **Christmas Carol (choir & organ)** - a stately carol: full choir on the tune, pipe organ (the real one when the Keys library is installed), church bells, timpani swells.
- **Christmas Lo-fi (cosy)** - dusty beats, warm Rhodes 7ths and 9ths, a celesta / music-box tune, gentle sleigh bells and vinyl.
- **Festive House (Christmas)** - four-on-the-floor in a major key with sleigh bells on the off-beats, house piano, a choir pad and glockenspiel on the hook.

Each tab now has a **Christmas** shelf in the genre list (Holiday moved there too). Bells and mallets are welcome in all the Christmas genres, electronic ones included.

## 2.14.3
- **Faster, lighter start with many plugins installed**: your startup.log shows the sound engine is ready in under a second, so the stalls came after that - from the plugin bookkeeping.
  - Each plugin's fingerprint (used to notice a reinstall) used to read *every file* inside the plugin - thousands for Cardinal or the big sample players - several times per page load. It now looks only at the plugin's program files and remembers the answer.
  - The plugin list is read once per page load instead of once per part menu.
  - The background check of new plugins (instrument or effect?) runs one plugin at a time, with a pause between, at low priority - and big sample players and racks (BBC SO, LABS, Kontakt, Cardinal ...) are no longer loaded just to ask; they're instruments. Because the fingerprint changed, each plugin is checked once more, quietly, after this update.
- Any request that keeps the page waiting more than 1.5 s is now written to startup.log, so if a start is still slow the log says exactly what it was waiting for.

## 2.14.2
- **Start-up freezes**: three changes.
  - The loading screen now asks the app for its progress and opens the studio itself, instead of the app pushing messages and the studio's address into a window that was still loading - on Windows that push could hang the window for good.
  - Studio Lab's window uses its own web view profile (in the app folder), so another program using - or closing - the shared web view can't take it down. Your settings come back from settings.json as before.
  - Only one Studio Lab window at a time: opening it again brings the open one to the front, and if an earlier copy has frozen (its window stopped answering), it is closed first, together with its engine, instead of making the new start freeze behind it.

## 2.14.1
- **The genre list is reorganised** into smaller, clearer shelves, each running from the best-known genre to its offshoots. Electronic: House · Disco, French & Nu-Disco · Techno · Trance · Psytrance · Dubstep · UK Garage, Grime & Bass · Future Bass & Wave · Drum & Bass & Jungle · Breaks, Rave & Hard Dance · Trap & Rap · Phonk · 808 Switch-ups & Bass Warp · Club: Jersey, Baltimore, Footwork · Pop, R&B & Hopecore · Afro & Amapiano · Latin, Brazilian & Caribbean · Chill & Lo-fi · Ambient & Synthscapes · Synthwave & Video Game · Hauntology. Classic: Rock · Punk · Metal · Surf, Rockabilly & Spooky · Pop & Indie · Soul, R&B & Gospel · Funk & Disco · Hip-Hop · Jazz · Swing & Big Band · Country, Folk & Blues · Celtic · Latin · Caribbean · African · Middle East, Balkan & Klezmer · South Asian · Indian Classical & Devotional · East & Southeast Asian. Orchestral: Film & Trailer · Epic · Fantasy, Games & Holiday · Classical Eras · Piano, Ambient & Experimental. Only the list changed - every genre sounds exactly as before.

## 2.14.0
Songs whose musical decisions feel intentional rather than independent random choices - the top three items of the improvement list:
- **Motivic development**: the lead's phrases no longer repeat word for word. In each pair of four-bar phrases the second one *answers* the first: it comes home to the tonic, moves the motif up a step (a sequence), echoes its opening cell twice (fragmentation) or shifts it an 8th later (rhythmic displacement). Later choruses / drops develop differently from the first, and the last hook climbs to a high point. This builds on the song's one-tune motif (verse lower and sparser, chorus hookier). Written cadences in classical forms and maqam / raga lines keep their own shapes.
- **Per-part human feel**: played instruments (keys, guitars, winds, bowed strings, mallets, bass guitar, upright, orchestral parts) get their own velocity spread, slightly varied note lengths and a dynamic swell over each four-bar phrase, and their timing breathes; synths and drum machines stay nearly exact (their timing looseness is cut to about a third).
- **Density that changes who plays**: in a song's first long section the supporting parts (pad, arp, counter-line) come in one at a time, and the bar before a big chorus / drop often takes a breath - pads, arps and chords drop out for two beats. Genres whose layout already stages its parts (the reference-built ones) are left as written.
- **Character traits steer all three**: Variation (low / progressive / theme and variations), Melodic behaviour (minimal motivic, call and response ...), Human feel (robotic switches the per-part feel off, loose / drifting makes it stronger) and Density (sparse / evolving: parts enter one by one more often, dense: fewer breaths).
- A new **Phrasing** setting (next to Melody theme) switches it all off for plain repeats.

## 2.13.4
- **Orchestra detection no longer bogs the plugin down**: while BBC Symphony Orchestra (or any orchestra plugin) is open, Studio Lab now only copies its state every few seconds - and less often by itself if the plugin is slow to hand it over - and does all the work of recognising the instrument in the app instead of next to the plugin, so the plugin's window stays responsive.
- **You can see it working**: each instrument appears in the log as soon as it is picked up ("✓ found celli spiccato"), sounds it can't name are listed too, and every 20 seconds it reports that it is still watching and how many sounds it has. Leave each instrument loaded for a few seconds so it is caught; whatever is loaded when you close the window is always saved.

## 2.13.3
- **Install all free plugins** (Sounds & instruments → Genre VSTs → ⚡ Install everything): one button downloads every free plugin that can be installed automatically. The open-source instruments are unpacked as before; the free open-source plugins that are only published as an installer app - Cardinal, Geonkick, Vaporizer2, CHOW Tape Model and BYOD - now have their official installer downloaded from the project's GitHub release, checked the same way (published SHA-256, Microsoft Defender, VirusTotal when you have a key) and run, silently where the installer allows it (Windows asks for permission first; on a Mac the system asks for your password). Each also has its own Install button. Plugins that need an account (Vital, LABS, BBC Symphony Orchestra, TAL, u-he) still need their own sign-up.
- **Smoother start after an update**: the new app now waits until the old one has fully closed (its engine, its port and the window's web view) before opening, which is what made the restart hang or come up blank. The window also appears sooner on every start (no more loading scipy before the window), and a first start after an update gets up to 5 minutes to compile instead of 2.
- **Orchestra detection (BBC SO) tells you what's happening**: if the plugin can't be read while its window is open, the log says so (the instrument loaded when you close the window is still saved - or set up one section at a time). When it can't name what it found, what the plugin's state did contain is kept in vst_sounds/.last_scan.json for a bug report.

## 2.13.2
- **Fewer bells in electronic genres**: every bell-like sound (glockenspiel, celesta, music box and all the synth / FM / trance bells) now only turns up as a rare colour in electronic genres - in roughly 1 song in 8 when it isn't the genre's own sound - and is otherwise swapped for one of the genre's own non-bell sounds (pool picks, section rotation and layers alike). Genres whose signature *is* a bell (trap, plugg ...) keep it. Melodic Club Rap's chords are now a dark poly synth instead of a bell.
- The Amapiano genre's log-drum check accepts the new log drums.

## 2.13.1
- **No more guitars in the synth Afro genres**: Afro Village Party - Synth now plays bright saw / digital plucks for its riffs (the wood and glassy-keys plucks that could sound like a twangy guitar are gone), and Afro Wobble is now built on the synth version - drum-machine kit, synth plucks, Juno chords, a square / synth-brass lead - instead of the clean guitar, organ and choir.

## 2.13.0
- **New genre: Afro Wobble (dubstep, 150-160)**: the village-party groove (tresillo drums, guitar riffs, sung call) crossed with dubstep - verses with no bass, snare-roll builds, a one-bar stop, then drops where a big wobble bass takes over, womping in beats, dotted 8ths and half bars and gliding between notes.
- **New genre: Afro Village Party - Synth (150-160)**: the same party on synths - a drum-machine kit (claps, rimshots, 808 cowbell, synth toms), an FM / analog synth bass, Juno-style chords, bright FM and saw plucks for the riffs and a square-wave or synth-brass lead.
- **New genre: Bass Amapiano (deep log drum, 110-116)** replaces Euro Club Bounce (that clip was bass amapiano; old Euro Club Bounce songs open as Bass Amapiano): the log drum is the star, with swung, laid-back shakers / congas / hats, a breathing detuned-saw pad, side-chain on almost everything, a mono low end, long builds and sparse drops.
- **New sounds**: sine log drum (strong pitch scoop, saturated, a little drift), deep log drum (sustained, resonant low-pass), talking log drum (synced bend + wah), breathing supersaw pad (7 detuned saws, slow LFO on the filter, pitch warble and scoop) and scooping supersaw stab. The classic Amapiano genre can use the new log drums and pad too.
- **The app opens in your theme**: the loading screen and the first paint of the app now use the theme you picked last time, instead of flashing the default colours.

## 2.12.0
- **New genre: Afro Village Party (150-160)** (Electronic > Afro, Latin & Caribbean), built from the ten open-air party videos: a kick on every beat with snare, rim, shaker and conga accents on the 3-3-2 tresillo (the half-time sway the recordings all share), a punchy bouncing bass, bright clean-guitar riffs cascading in 16ths, a cheap-keyboard organ chopping the off-beats, a sung call line that answers itself every two bars, sunny major keys - and the DJ move from the videos: every 8 bars the kick and bass drop out for a bar or two while the voices and guitar carry on, then everything slams back in. Its rhythm and sounds stay its own (no swapping in other genres' grooves).
- **New genre: Euro Club Bounce (128-132)** (House & Disco), from the DJ-controller clip: a hard four-on-the-floor, a fat bass rolling between every kick, off-beat open hats over 16th hats, wide detuned minor chords and a high one-note pluck hook, bass-heavy and laid out for a DJ set.
- **New genre: Melodic Club Rap (160)** (Hip-Hop, Trap & Phonk), from the music-video clip: half-time at ~160 with a long sliding 808, a sung hook, rapid hats with rolls, dark bell chords and sudden full stops where the beat cuts out and slams back.
- Written layouts can now keep 1-bar sections (used for the village-party drop-outs).

## 2.11.0
- **Concert grand piano (Salamander Grand Piano V3)**: a new free real library in Sounds & instruments - a big, open Yamaha C5 concert grand, 5 velocity layers, 230 MB. Once installed it plays the piano in classical, film piano, neoclassical, romantic, cinematic, storybook, minimalism, jazz (jazz, modal, bebop, soul jazz, smooth jazz), neo-soul, gospel, piano house, ambient, chamber pop and emotive deep house; lo-fi / vintage genres keep the worn upright. Also in every part's Sound menu as "Concert grand piano (Salamander)". License CC-BY 3.0: free for anything, credit "Salamander Grand Piano by Alexander Holm".
- **Muted trumpet (harmon) and muted French horn** added to the Brass & woodwinds library (same VSCO 2 source). The trumpet in jazz, modal jazz, jazz hop, jazz rap, lo-fi, trip hop, smooth jazz, electro swing, ethio jazz, soul jazz and neo-soul now plays with a harmon mute. Already installed? The library offers a small update.
- **OB-Xf is back as a one-click free synth** (Oberheim-style analog poly, open source, from its official numbered releases - never the nightly builds), now with six genre sounds written for it from its real parameters: brass, 80s chord stab, warm pad, strings, unison lead and fat bass. It's the first choice in synthwave, dark synthwave, darksynth, synthpop, italo disco, sophisti-pop, synth-funk, electro funk, 80s jam rock, new jack swing, synth R&B, 90s trance pop, progressive house journey and spacious breaks electronica, and a second option in trance, uplifting / anthem / 2000s club trance and progressive house.
- **More free instruments listed in Genre VSTs** (install them yourself - each only ships as an installer app or a 1 GB+ download): Vaporizer2 (trance / progressive leads, plucks, growl basses), Cardinal (modular pads and generative sequences for ambient, IDM and spacious breaks), Geonkick (designed kicks and 808s for techno, trance, house, dubstep) and DrumGizmo (big multi-mic acoustic kits for rock and metal). Save a sound in any of them and matching parts use it.

## 2.10.2
More natural-sounding songs:
- **A natural rise and fall in loudness** instead of every section sitting at one level and then jumping: the drums dig in a little more across each verse (about 1 dB), the pads, chords and arps swell over the last two bars into a chorus or drop, and everything eases back over the bar before a break. Gentle, acoustic genres move a little more.
- **Mixed more like a record:** a little more room in the low mids, the harsh 4-5 kHz eased, a softer presence lift and the brightest top pulled back 1 dB (each genre's own brightness still applies), and lighter limiting - at most 2 dB (was 3) and half the clipping - so the loud parts hit harder. Songs that can't reach their loudness target without squashing now come out slightly quieter instead.

## 2.10.1
- **Less vinyl noise:** the vinyl layer (lo-fi, boom-bap, soul-sample and the other genres that use it, and the vinyl background texture) has about a third as many crackles at half the level, and its hiss is ~8 dB quieter.

## 2.10.0
- **Fixed: bass wobbles going crazy at fast tempos.** Bass LFOs are tempo-synced in beats, so at drum & bass tempos a 1/6- or 1/4-beat wobble (and the default speeds of the growl, screech, riddim, wobble 808, laser and other LFO basses) ran at 12-23 wobbles a second - a buzz, not a wobble. Every bass LFO is now slowed by whole doublings (so it stays on the beat) until it is at most ~9.5 a second (a 16th at 140 BPM still fits).
- **Genres modelled on one record keep their own sounds:** Spacious Breaks Electronica no longer swaps its parts for other genres' synths (one test song had picked a trance pluck, a house pad and a choir) or rotates them between sections. New sounds made for it: a warbly **modular pad** (two oscillators drifting on their own, wavefolded), a soaring, gliding **modular lead** and a **generative modular blip** for the patch sequences. Its balance is the record's now: the synths carry the track over a constant sub from the very start, the drums sit under them.

## 2.9.9
- New genre: **Spacious breaks electronica (128-130)** - from a progressive-breaks record and your production notes: a long atmospheric opening of haze and weather, the chords and sub, then a soaring lead, before an energetic breakbeat with a flurry of percussion arrives; warbly, slightly unstable poly-synth chords and pads, melancholic Am - Fmaj7 - Dm - Em-style colour chords that never resolve, one continuous flowing arrangement (parts layer in and out, no hard cuts), a warm rolled-off top, a wide deep image and a quieter master that leaves room to breathe.
- New background textures: **wind** (slow gusts) and **fire** (a warm roar with crackles), next to rain, air, waves and vinyl. A genre can now give its own list of textures to pick from.

## 2.9.8
- New genre: **Anthem Trance (2000 club mix)** - measured from a 2000 trance remake: 138-140 BPM minor, built for the DJ - a filtered beat-only start, the rolling bass and then the percussion layering in, the riff, a short drop-out, a long breakdown that starts dark and empty and climbs (pad, chords, melody, snare build) into a 32-bar peak, a breath and a rebuild into a second peak, and a beat-and-bass outro. A controlled, darker top end like the records of the time.

## 2.9.7
- **Updates restart Studio Lab in a fresh window again** (as before 2.4.3): after an update installs, the app closes and opens the new version. The same-window swap could hang on the loading screen on Windows.

## 2.9.6
- **Fixed: an update restarting in the same window got stuck on the loading screen.** While the new version started, every progress line reloaded the loading screen and then waited on the window to answer - which on Windows can hang forever. The loading screen now loads once and progress lines never wait on the window. (The update INTO this version still runs the old code: if it sticks one last time, close Studio Lab and open it again.)
- New genre: **Choir Rap (minor, churchy)** - a dark church-choir hip-hop beat around 92-100 BPM, learned from choir-rap stems: a clean guitar / sample loop on slow minor changes, a big choir on the tonic and the fifth, a deep sub on a 3+3+2 rhythm, tape strings arriving late and a two-note half-step figure on top, the parts coming in one at a time.
- **Song structures learned from real pop / indie stems** - new arrangement moves for verse / chorus genres: two bars of the beat alone before the intro; a bare first verse (beat, bass and melody - the chords wait for the chorus); a 2-bar drum stop right before verse 2; a bridge stripped to beat, bass and one synth line; an instrumental interlude after the second chorus; and an ending on the melody alone.

## 2.9.5
From a trance / techno / house construction-kit pack (128-138 BPM):
- New sounds: **wide mid saw bass** (the rubbery, wide 3-note house rolls between the kicks) and a **bright trance chord stab** (wide supersaw, a third-of-a-second decay). House, Tech House and Techno can pick the bass; House and the trance genres the stab.
- New grooves from the kits: Uplifting Trance's double off-beat bass and 16th 'speed' hats; House's 3-note rolling bass, pre-offbeat hats and 8th shakers; Tech House's double off-beat and rolling basses and a broken hat groove; Progressive House's double off-beat bass and pre-offbeat hats.

## 2.9.4
- **The new wobbles and subs across the whole dubstep family:** Dubstep, Brostep, Riddim, Melodic Dubstep, Chillstep, Dark Dubstep (classic), Deep Dubstep Minimal / Rollers / Rolling, Early Dubstep and Steppy Halftime can now pick the slow, 'yoi', sweep, reese, bright, tearout and pitch-growl wobbles and the sleeper / diving / deep subs that fit them, and the dark atmosphere and flutter pads. Dubstep's and Brostep's signature-sound checks accept the new wobbles.
- **Dubstep drum kits:** every dubstep-family song now picks one of several kits - the genre's own, **deep-dark** (short tight kick, crisp bright snare), **soundsystem** (deep long kick, fat snare), **slam** (hard driven kick, cracking snare; Brostep / Riddim), **rimshot** (early-2000s dry kick, tight rimmy snare, short hats) or **smooth** (Melodic / Chillstep). Re-roll the sounds to change it; picking a kit yourself still wins.

## 2.9.3
- **Studio Lab is a normal Windows program now, however you got it.** On its first start it puts a **Studio Lab** shortcut with its icon in the Start menu (and one on the desktop), carrying the app's own taskbar identity - so you can right-click it, or the open Studio Lab window, and choose **Pin to taskbar**, and the pinned icon and the window are one taskbar button with the Studio Lab icon (not Python's). This covers running from a downloaded folder and older installs that were only ever updated in place; the installer already did this. To remake them any time: **Make Studio Lab Shortcuts (Windows).bat**, or `studiolab.py shortcuts`. Checked on a real Windows machine in the installer self-test.
- Tests: lint warnings fixed; Dream Pop's melody sits in the wash on purpose (like Shoegaze).

## 2.9.2
Learned from a deep-dark dubstep sample pack and five more reference tracks:
- New basses: **diving sub** (dives an octave, sags a semitone or two, or dives and comes back), **mono analog zap** (a saw diving from two octaves up through a closing filter) and **pitch-wobbling growl** (a moaning mid-bass whose pitch bends with the LFO).
- New pads: **dark swelling atmosphere** (slow seconds-long swell, kept under 1.5 kHz) and **fluttering hollow pad** (a fast ~10 Hz shimmer).
- Slow Wobble Dubstep: its main bass is always a wobble now (sub-only sounds moved out of its list); slower movement leads - half-bar and dotted-quarter sweeps, then bar, beat and triplet ones; keys around F / F# / D# / D; a tight, short kick and a crisp bright snare like the pack's; more hat and ride patterns from its loops.
- Deep Dubstep and Deep Dubstep Rolling can pick the new subs, growl and pads.

## 2.9.1
- **Fixed: clicks / 'clipping' at the start or end of bass notes.** Many synth basses (the acids, 808 variants, stab and 808 wobbles...) were cut off mid-wave - their last sample still 5-50 % of their peak - and some started on a non-zero sample. Every pitched note now ends with a 4 ms fade, and every bass note starts with a 1.2 ms one (too short to soften a pluck).
- **Dubstep bass glides:** about a third of the wobble notes that follow straight on from another note now glide into it (octave dives and rises, slides to the next note; never more than an octave).
- **The background 'waves' texture is no longer in every song:** about half the songs have none; the others get one of washing noise, a soft high air, light rain or vinyl crackle.
- Learned from your loops: new **'sleeper' sub** (the sub's own pitch bends slowly, or arcs up a tritone and back), **grimy bright wobble** (dotted / triplet bounce) and **tearout riff bass** (tight chops in 300 Hz - 4 kHz); skippy 32nd-note hat rolls and sparse percussion patterns for Slow Wobble Dubstep; deep dubstep and riddim pools get the new basses. Drum patterns can now use a 32nd grid (rolls) or 16th triplets.

## 2.9.0
- New genre: **Slow Wobble Dubstep (bass-led)** - deep half-time 140 where the bass is the song: a clean sine sub and one wobble on top moving slowly (a sweep per bar, half bar or beat, a dotted-1/8 bounce, or one sweep opening across the whole note), lots of space where the sub carries on alone, minimal drums. Measured against deep dubstep reference drops (sub share, darkness, wobble speeds).
- New bass sounds: **slow deep wobble**, **talking 'yoi' wobble** (oo-ah-oo vowels), **rising sweep wobble**, **slow dark reese wobble** and a clean **deep sine sub**. All take their LFO speed from the composer, sit on a clean sub, and work in any genre's bass.
- Wobble genres can now leave more space between phrases (the sub carries on alone).

## 2.8.0
- **Listening check** over 120 random genres (preview render, loudness, peaks, clipping, band balance, stereo width,
  silence, genre fit, melody-against-chord rubs). No errors, no clipping, every genre at 100% fit, loudness on target.
- **Ambient melodies no longer rub against the pads.** Held melody notes were tuned to the harmony early on, but later
  stages (calm long-note leads, answer phrases, extra arpeggios, layer copies) could still land a note a semitone
  above a pad note. The tuner now runs again after those stages: ambient went from up to 10% of held notes rubbing to
  under 1%. Neighbouring genres were already clean.
- **Faster previews with delay throws.** A fading echo tail left the signal full of near-zero numbers (denormals) that
  made the reverb on the delay return crawl: 4.7 s for one effect, now 0.2 s. Slam previews about 20% faster.

## 2.7.0
- **The genre test suite passes again** (it had been failing since 2.4.0, which hid real bugs). Fixes along the way:
  - **Trap and drill 808s were marked "not sliding".** The songs slid fine. The check only knew the plain "808", so a song
    that switched to its slide / wobble / drill 808 for the VIP section failed. Every 808 in the family now counts.
  - **Reading chord progressions from your reference MIDI.** Major-7th chords were read as their upper triad (G-maj7 as
    B minor, so IV came out as vi). The bass now counts double, as intended, and the bar's real bass note decides: the
    note the bass holds, not a quick pickup.
  - Genres no longer carry sound lists for parts they don't have (left over from genre inheritance: a chant had an 808
    list), and a genre's own sound always leads its list.
  - The meter test now leaves out the Celtic grace notes, which sit just off the beat on purpose.
- **Genre-fit fixer:** any song under 100% genre fit gets a **Fix genre fit** button. It pulls the tempo into the genre's
  range, drops your overrides that fight the genre (instruments, kit, groove, reference rhythm), calms variety, tries
  nearby seeds, then plays the fixed version.
- **Library filters:** filter your songs by genre, rating (kept, liked, disliked, not rated), genre fit and name. The library
  now lists your last 300 songs (was 60).
- **Genres lead with the new instruments:**
  - The tonewheel organ with its two-rotor speaker is now the organ in gospel, modern gospel, soul jazz, reggae, soul
    ballad, blues, ska, jam band and funk. The rock organ is the organ in rock.
  - Funk's second guitar is the wah guitar.
  - The old sounds stay in rotation, and the old organ keeps its classic Leslie when picked.
- **Song titles never repeat a word** ("Static of the Static" became "Static of the City").

## 2.6.1
- New genre: **Progressive House Journey (Y2K)** - the long, hypnotic turn-of-the-millennium progressive DJ track (128-131 BPM, about 6 minutes) that builds by adding one part at a time: percussion alone, a rolling bass filtering in, claps and an evolving widescreen pad, a dark hypnotic pluck under delays, muted stabs, and only late a sparse gliding lead - two breakdowns, a peak, then the parts leave one by one. Soft round kick, pumping sidechain, slow filter sweeps, a warm controlled top end.
- New sounds for it (usable anywhere): **rolling progressive bass**, **evolving widescreen pad**, **hypnotic pluck**, **dark progressive stab** and **gliding progressive lead**.
- **Fixed: bass crunching when it comes in and swelling when it stops.** The master's glue compressor reacted to the sub itself: when a loud bass entered, the whole mix ducked and the limiter caught the overshoot. Its level detector now ignores the sub (a 90 Hz sidechain filter) and averages over two bass cycles.
- **Fixed: the sine bass thumped on and off.** Its warm saturation left a DC offset in every note that jumped in at the start and out at the end; it's removed.
- Render workers now quit if the engine that started them is closed or crashes, instead of staying behind holding memory.
## 2.6.0
- **New genre: Synthscape vignette** (Electronic > Chill, Lo-fi & Ambient), modelled on the one-minute synth piece you sent.
  It plays one gesture: a hushed 4-bar opening, then everything drops in at once for 12 bars over a soft quarter-note
  heartbeat and a high bass walking the V pedal (in A-flat: Eb, Eb, F, Ab), warm maj7 chord tones pulsing in triplets
  against it, then an 11-bar tail that holds quiet and only fades at the very end. It is darker than the dreamy
  synthscape (almost nothing above 1 kHz), has no sub, sits narrower, and is about a minute long (sometimes a little
  longer). It shares the dreamy synthscape's sound palettes and pulses, so no two songs sound alike.
- **14 new instruments**, each added to the rotation of the genres it suits:
  - **Organs:** tonewheel organ with a real rotary speaker (drawbars, key click, percussion; the horn and drum spin
    separately, slow under chords and fast for solos) and an overdriven rock organ.
  - **Guitars and strings:** wah funk guitar (chicken-scratch through an envelope wah), 12-string jangle, lap steel /
    slide, dobro (resonator), ukulele and hammered dulcimer.
  - **World:** didgeridoo.
  - **Electronic:** donk bass, glitch chopper, omnichord and stylophone.
  - **Keys:** toy piano.
  - The Irish bouzouki and the modelled bagpipes stay as they were; those were already here.
- **Fixed: locked parts moved when you re-rolled.** Since 2.4.0 each song picks its own arrangement variant, and it
  picked one from the new seed. A part locked from another song then landed in different sections. The arrangement
  now follows the locked part's song, so locked drums, bass or chords stay where they were.

## 2.5.2
**More sounds, more variety**
- New trance sounds: hollow **virus pluck**, **FM pluck**, **reverse-swell pad** (sucks into the drop), **trance choir pad**, classic **square lead** with portamento, and a rolling **tri bass** for uplifting and psy.
- New acid sounds: **acid squelch** (resonance near screaming), **acid distorted** (acid techno) and **acid lead** (the 303 played high).
- New Celtic sounds: **Irish tenor banjo**, **crwth** (Welsh bowed lyre with drones) and **DADGAD guitar**.
- Trance, psy, techno, acid house, house and the Celtic genres now offer many more sounds per part - Euphoric Trance went from 4-7 sounds per part to 8-15.
- Drum kits: trance, techno, acid house and psytrance now pick one of several fitting kits per song (re-roll sounds to change it; choosing a kit still overrides).

## 2.5.1
- The gaita and the Scottish smallpipes are rebuilt on the Highland pipes' physical reed model (they were simple synth reeds): one continuous reed per phrase, folded into the chanter's range, with their own drones - the gaita open and singing with vibrato over a single deep roncón, the smallpipes quiet and sweet over three soft drones.

## 2.5.0
**More Celtic**
- New sounds: **clarsach** (wire-strung Gaelic harp), **cittern**, **Scottish smallpipes**, **gaita** (Galician bagpipe with its roncón drone), **bombarde** (Breton oboe) and **melodeon** (button accordion). They join the pools of the Celtic genres.
- New genres: **Pipes & Orchestra** (the pipe band with strings, horns, contrabass and timpani), **Breton An Dro** (fest-noz: bombarde, cittern, driving bodhrán), **Galician Muiñeira** (gaita over tamboril and bombo) and **Clarsach Air** (slow wire-harp music).
- Uilleann pipes, gaita and smallpipes drones now sit on the song's key.

## 2.4.15
- New sound: **Great Highland bagpipe, bright** - the same pipe band with its overtones pushed well forward (more edge, open top, same loudness). Picked by Highland Pipe Band and the Celtic genres alongside the regular bagpipe, or choose it yourself for the lead.
- Highland Pipe Band: the drones are 5 dB lower, so the chanters sit on top.

## 2.4.14
- Bagpipes much brighter, not muffled: the low fundamental no longer drowns the reed's overtones, the top end is opened up (all of 2.4.6's brightness, a high shelf, a 2.4 kHz presence lift, the old fizz-tamer mostly removed) and the hall's reflections are brighter too.

## 2.4.13
- Bagpipes: some of 2.4.6's sound back on top of 2.4.12 - brighter, reedier radiation, 2.4.6's nasal formants layered with 2.4.8's, less low boom, the reeds blended a bit harder into one wall, and the pipers a little tighter together. Still the 4-piper group, still no hiss.

## 2.4.12
- Bagpipes: the best of 2.4.8 and 2.4.11. The 4-piper group sound stays; 2.4.8's character comes back - the reed's breath (slow now, so it adds life without hiss), the crow at each phrase start (half as strong, so no twang), the nasal bite, the reeds blending into one wall, and the hall's space (only the later, softer reflections, so no tunnel).

## 2.4.11
- Pipe band sounds like a group again: 4 pipers, each drifting slightly ahead and behind on their own, a few cents apart and wandering in pitch independently, so the chanters beat against each other like a real band.
- Bagpipe tone: no more sitar twang - the pitch scoop at each phrase start is nearly gone, note changes are quicker (2.5 ms) and the tone EQ is broad instead of ringing.

## 2.4.10
- Bagpipes: the white noise / crunch is gone. The reed no longer gets breath noise while it plays (any of it came out as hiss, about 35 dB less now) - only a tiny puff to start each phrase.
- Bagpipes: notes now glide into each other (about 5 ms instead of an instant snap) and each phrase eases in softly instead of a hard 8-bit-style start. Timing is unchanged.
- Bagpipes: no saturation on the band, and the reeds were retuned to stay stable without the noise (all chanter notes within a few cents, no octave jumps). Drone buzz turned way down.

## 2.4.9
- **Fixed: the pipe band sounding like it was in a tunnel.** Two things caused it. The short "hall" reflections are gone, since copies of the sound a few milliseconds apart made a boxy comb; the pipes' space now comes from their normal reverb. And the three pipers were near-identical reeds playing almost exactly together, which flanged. Now each piper has a different reed (a different harmonic balance, all still in tune), they're spread wider, and they're as loose as humans at the note changes.


## 2.4.8
**Bagpipes: less electronic, fuller**

- **No more electronic fizz.** The chanter's reed snaps shut every cycle, which makes harmonics far above hearing. At the normal sample rate those fold back down as a fizzy, synthetic buzz (aliasing). The reed model now runs at **twice the sample rate** and is filtered back down, so the fizz is gone. Each note is tuned at that rate too, and all nine chanter notes land within about 4 cents.
- **Fuller and bigger:**
  - more body in the chanter around 500 Hz and gentler top-end emphasis
  - **early reflections of a stone hall** around the band, so it sounds like pipes in a space rather than straight out of a box
  - a stronger nasal bite (1.3 and 3.2 kHz)
  - snappier gracenotes (38 ms)
  - drones with a little room carved in their midrange so the tune cuts through
  - each piper's reed drifting a couple of cents on its own, like real reeds


## 2.4.7
- **Fixed: bagpipe drones drifting out of tune.** Their bag-pressure sway was a random walk that wandered up to nearly a semitone flat or sharp over a song, which is why the drones sounded out of tune only some of the time. It now holds within about 1 cent, as a steady piper does.
- **The pipes no longer stop inside a tune:** a note holds over short rests, as on a real chanter, and the reed only starts again after a real silence.


## 2.4.6
**Pipe band fixes: the drones' pitch, the chanter's range, the pipers' unison**

- **The drones were an octave too low.** They droned at 58 and 116 Hz, which comes across as a sub-bass rumble. Now the tenors sit an octave below the chanter's low A and the bass an octave below them, as on real pipes. They're rebuilt as cylindrical-pipe reeds (odd harmonics strong, the bass darker), with the two tenors a third of a hertz apart so they beat slowly, a shared bag-pressure wobble and a faint reed buzz. They're balanced about 8 dB under the chanters.
- **The tune stays on the real chanter.** The Highland chanter has exactly nine notes, low G to high A. Tunes used to run far above that and squeal. Now every note is fitted onto those nine, and the gracenotes are the real ones (high G, or high A on the top notes).
- **The pipers play in unison**, within about 2 cents and 3 ms of each other, instead of a chorus that beat against itself.


## 2.4.5
- **The pipe band is a band now.** Three modelled chanters play the tune together, the way a real band does: a few cents apart, a few milliseconds early or late, each on its own reed, spread across the stereo field and soft-saturated together. That gives the thick, slightly chorused wall of reed a real pipe band has, instead of one solo piper.
- Stronger nasal chanter formants (around 1.1 and 2.8 kHz), more present drones, and a louder, brighter master for the pipe band.


## 2.4.4
**Bagpipes: real piping ornaments and the traditional pipe scale**

- **Ornaments that follow the melody.** On a chanter that never stops, the ornament *is* the articulation, so it now depends on what the tune does:
  - a **gracenote or a strike** on every repeated note (the only way to sound the same note twice)
  - a **cut** from the note above when the tune steps down
  - a **doubling** on strong beats
  - a **taorluath-style** figure into long, heavy notes
  - a high-G gracenote going up
- **The traditional Highland scale.** The chanter is tuned pure against its drones rather than equal-tempered: the third 14 cents low, the sixth 16 low, and the famously "flat" high G at the natural seventh. That's what makes real pipes ring and lock with the drones.
- **New: Ornaments** (Song panel), from *None* (a plain melody) through *Light*, *Traditional* and *Heavy* to *Virtuoso*. It works for every Celtic genre: cuts, taps and rolls on fiddle, whistle and flute, and gracenotes on the pipes.


## 2.4.3
- **A real bagpipe.** The Great Highland bagpipe is now a **physical model**: a simulated double reed driving a conical bore, blown by a bag at constant pressure.
  - The pitch locks in by itself and the reed buzzes naturally. Every note is tuned and checked automatically, and notes that would overblow are eased off, as a piper would.
  - The chanter plays **as one continuous reed through each phrase**: each pitch holds until the next note, and the gracenotes are what separate the notes, as on real pipes. Before, every note started its own attack, which sounded synthetic.
  - The **drones** are three modelled reeds on cylindrical bores (two tenors beating slowly against each other and a bass). They run unbroken under the whole tune.
- **Synth pipes:** a new bagpipe-style EDM lead, with a detuned stack shaped like a chanter, its own root-and-fifth drone and a gracenote flick into every note. Celtic punk can pick it.
- **Fixed: Play with changes.** It now plays the moment it's ready; before, it quietly added a new card, so it looked like nothing happened. It also keeps the song's own sounds on every part you didn't change, so it's the same song with only your changes.
- **Updates restart in the same window.** After an update, the window shows the loading screen, starts the new version behind it and switches straight back to the app, with no closing and reopening. (Changes to the window itself, which are rare, still apply at the next launch.)


## 2.4.2
**The rest of the Celtic dance forms, and 9/8**

- **Celtic Hornpipe:** slower and heavier than a reel, with the dotted, swung long-short lilt and strains ending on three firm beats.
- **Slip Jig (9/8):** three groups of three, graceful and flowing. Studio Lab now supports **9/8**, with the right time signature in the MIDI file and the REAPER project.
- **Strathspey:** the Scottish dance built on dotted rhythms and the **Scotch snap**.
- **Celtic Polka:** fast and punchy, with an oom-pah guitar on the off-beats and accordion on the tune.
- **Celtic Session Set:** two or three tunes as one unbroken medley, the way a pub session plays them. Each tune is AABB, and the next one comes in a new key (up a fourth, then a fifth) with a lift in tempo.
- The Celtic dance genres keep their strict AABB form; the per-song layout changes don't touch them.


## 2.4.1
**Celtic, made authentic: session instruments, session drums, and real ornaments**

- **New instruments:**
  - **Session fiddle**: bowed, with rosin and bow-change scratch and a woody body. Almost no vibrato, the way folk fiddlers play.
  - **Irish bouzouki**: paired steel courses, the low ones in octaves, so every note shimmers.
  - **Wooden Irish flute**, breathy with a soft chiff, and a soft, airy **low whistle**.
  - **Concertina**: two free reeds a hair apart.
  - **Uilleann pipes**: a sweet chanter over its own drones.
  - **Great Highland bagpipe**, loud and nasal with no dynamics, plus its **drones** (two tenors and a bass, beating).
- **New drums:**
  - a **bodhrán** with a deep, hand-bent boom and high tipper strokes near the rim
  - **bones** and **spoons**
  - a crisp, high-tuned **pipe-band snare** and a **tenor drum**
- **Ornaments, the heart of the style.**
  - Fiddle, whistle, flute and pipe melodies now get **cuts** (a flick to the note above), **taps** (a flick below) and **rolls** on long notes.
  - The Highland pipes articulate almost every note with a **high-G gracenote**, and add **doublings** on strong beats.
- **The Celtic genres use all this:**
  - **Jig:** session fiddle with whistle, bouzouki, bodhrán with tipper.
  - **Reel:** a swung 8th-note lilt and bones.
  - **Slow air:** uilleann pipes.
  - **Sea shanty:** concertina and claps.
  - **Pipe band:** bagpipe chanter and drones at the chanter's real pitch (about B♭), pipe-band snare and tenor drums.
  - **Celtic new age:** low whistle.
- All of them play in session keys (D, G, A, E) with open, drone-friendly chords.


## 2.4.0
**Songs that don't repeat their shape, 22 new genres, fewer bells in dubstep**

- **Every song gets its own arrangement.** 225 of the genres had a single layout, so every song in them had the same shape. Now each song reshapes its genre's own layout with moves arrangers actually make, and about 1 in 4 still plays it as written.
  - **Verse / chorus songs:** a pre-chorus build into the chorus, the hook first (cold open), a radio edit, a drums-out breakdown in place of the bridge, a double final chorus that adds layers, a longer or shorter intro, or a cold ending.
  - **Club tracks:** a long DJ intro, a longer breakdown, a fake-out build, a switch-up final drop, an extended last drop, a short third drop, or a 32-bar drop split in two with the second half varied.
  - **A/B forms:** an extra varied A, a longer C, or B first.
  - Pop now comes out in 10 different shapes in 12 songs. Genres modelled on reference records, generated layouts, classical forms and genres that already rotate their own layouts keep their exact layouts.
- **22 new genres:**
  - *Celtic* (its own group, with the jig): **Celtic Reel (4/4)**, **Celtic Slow Air**, **Celtic Punk**, **Sea Shanty**, **Highland Pipe Band**, **Celtic New Age** (choir and harp).
  - *Electronic*: **Shangaan Electro** (180+ BPM marimba riffs), **Kuduro**, **Neoperreo** (dark, minimal dembow), **Darksynth**, **Mallsoft**.
  - *Classic*: **Dream Pop**, **Highlife**, **Soukous**, **Balkan Brass**.
  - *Orchestral*: **Gregorian Chant**, **Horror / Dread**, **Wonder / Discovery**.
- **Fewer bells in dubstep.** Dubstep, deep dubstep, riddim, brostep and switch-up bass no longer reach for bells: a bell now turns up in about 1 in 8 dubstep songs, and not at all in the others. Grime and chillstep keep theirs, since bell melodies belong to those sounds.
- **Genres can now be built from a close relative.** A new genre inherits everything from its parent and overrides only what makes it itself. The new genres are built this way.


## 2.3.1
*(Euphoric Trance and the sound check below were committed after the 2.3.0 release had already been built, so they ship here.)*

**New genre: Euphoric Trance, and an electronic sound check**

- **Euphoric Trance** (Techno & Trance), built from your uplifting-trance brief:
  - **The full arc, about 6 minutes at 138–142:** a DJ intro (kick, bass, percussion), then the arp and atmosphere, the main groove and a first build. The first drop has a simple lead. Then the lead fades and a **long breakdown** follows, with no kick or bass, where **the melody moves to piano** over wide pads. A tense main build (snare rolls, rising filters, the piano still singing) leads into a **climax far bigger than the first drop**, an extended climax, and a 32-bar mix-out.
  - **A lead harmony that follows the chords**, not a fixed interval. Each lead note gets the nearest chord tone a third above (else a sixth or a fifth). On passing notes it gets the diatonic third, like a second singer, so it always stays in key. It joins only the answering half of each phrase in the first climax, then plays throughout the extended climax, so the arrangement keeps growing.
  - **Every part has its own job:** a rolling off-beat mid-bass plus a clean, centred sub; a wide 7-voice supersaw chord stack, voice-led and pumping; an evolving pad behind it; a bright pluck / FM-bell arp in 16ths with ping-pong delay; a layered supersaw lead.
  - **F#, A, D and E minor**, using i–VI–III–VII and its relatives.
- **Electronic sound check:** I generated 12 songs in each of the 189 electronic genres and looked for parts that always got the same synth.
  - Daydream downtempo and Sunlit electronica always played the same bass because their sound palettes overrode the pick. Now a palette only decides a part when the palettes actually differ on it.
  - Trap, UK drill, plugg, reggaeton, alt R&B, baile funk, funk 150 and orchestral hip-hop now rotate through the 808 family: plain, long, punch, dark, distorted, sliding, drill and wobble. The plain 808 is still the most common.
  - Acid house now uses all its acid basses. Dream synthscape, ethereal wave and switch-up bass have wider pools.
  - Everything else already rotated properly. Chiptune stays on chip sounds and amapiano on its log drum, on purpose.


## 2.3.0
- **Electronic genres play electronic basses.** Bass guitars, upright and acoustic basses (finger, pick, slap, sampled or
  modelled) no longer turn up under electronic tracks. They were in about 40 electronic genres' bass rotations (deep house,
  melodic house, liquid DnB, K-pop, PS1 game, teen pop, glitch pop, the hauntology genres, chillwave and more), including
  the per-song palettes of sunlit electronica and daydream downtempo. Genres whose own bass was one of them now use a synth
  bass (Moog-style, FM or Juno), and short rotations were refilled with synth basses. Synth basses with a plucky filter
  stay. Electro swing, krautrock and future funk keep their real bass, because those genres are built on one.
- **Synth brass, not a real brass section,** in synthwave and electro. **No acoustic piano** in tech house.
- **Hook-first melodies** (Sound panel, or `--hook-first on`): the verse sings the chorus hook's rhythm and shape, lower and
  softer, over the verse chords, so the chorus lands as the payoff of an idea you've already heard. Off by default.
- **Four new genres:** Jazz-hop (crisp swung drums, 9th-chord Rhodes and piano, upright, flute and sax), Storybook film
  score (a nostalgic piano theme, warm strings, flute and glockenspiel answers, harp), Cinematic dark trap (menacing
  strings, choir and bells over sliding 808s) and 80s synth R&B (gated LinnDrum, pulsing synth bass, poly synths and
  synth brass, a soaring hook).
- **Fixed: metal genres lost their metal guitar** whenever a song picked from the genre's guitar list. They got the plain
  rhythm guitar instead. Every genre built on a 2.0 rig guitar (metal, jangle, dreadnought, telecaster ...) now lists it first.
- **Fixed: grunge's rebuilt guitars never rotated.** Its guitar lists were stored where the app doesn't read them.
- Genre matching now has fingerprints for grunge, euphoric UK techno, switch-up bass and the new genres.
- The test suites pass again: several checks still assumed pre-2.0 guitar names and the old trap bass list.

## 2.2.7
- **No artist or song names anywhere in the app.**
  - Genres made from reference tracks are now described only by their sound.
  - The classical genres name their era instead of composers.
  - The re-played breaks have descriptive names: classic jungle break, fast funk break, laid-back funk break, bongo funk break, tight funk break, heavy funk break, big-room rock break and swung soul-shuffle groove.
  - The sounds and patterns themselves are unchanged.


## 2.2.6
- **Fixed: start-up stuck on "Loading numpy…"** (2.2.3–2.2.5). The engine watched a pipe from the window to know when to close, and on Windows that froze its own loading of numpy. It now watches the window's process instead, with no pipe.
- **Faster start:**
  - The Windows installer ships Studio Lab, numpy and scipy already compiled, and the updaters compile right after updating, so nothing is compiled at start-up.
  - The plugin scan and the output-folder tidy-up wait until after the window has loaded.
- *startup.log* now records the time of every step.


## 2.2.5
- **Fixed: start-up stuck on "Loading the sound engine…".** The loading screen's progress messages could hold up the start itself (a pywebview quirk on Windows). Now nothing waits on them.
- **The loading screen shows each step** (numpy, scipy, instruments, genres, composer, studio) **and a seconds counter**, so you can see it's alive.
- **If the engine takes over 2 minutes or stops, the screen says so** and points to *startup.log* in your Studio Lab folder, which holds everything the engine printed while starting.
- The updater no longer clears Python's compiled-file cache, so the first start after an update is faster.


## 2.2.4
- **"Update Studio Lab.bat": update without opening the app.** Double-click it in your Studio Lab folder. It closes Studio Lab if it's open, downloads the latest version from GitHub and copies the program files over. Your songs, presets, settings, sounds, plugins and the bundled Python are never touched. It comes with every install and is attached to every GitHub release.
- **The in-app updater no longer moves away files it doesn't replace**, such as StudioLab.exe and the icon from the installer. It only backs up the files it overwrites, so it can put them back if an update fails.


## 2.2.3
- **Fixed: "127.0.0.1 refused to connect" at start-up** (2.2.1 and 2.2.2). The window could load before the studio was answering.
- **The window stays responsive while Studio Lab loads, and while songs render.** The sound engine now runs in its own background process, so Windows no longer says "Not responding". The engine closes with the window, and installing an update restarts both.


## 2.2.2
**Switch-up Bass: bar-long rising, sinking and alien effects**

- **Every section ends on a move across its last bar**, the way the reference track does it. Everything on top sinks together going into a drop-out or dark stretch: a tape slow-down, a low-pass closing to a thud, or a crush dive. Going into a new drop, it rises instead: a tape push, a filter opening or an accelerating stutter. Before a drop-out the sub often dives with it.
- **Alien moves inside each section.** Every few bars, one or two parts do that scene's own move across a bar or two:
  - a **frequency shifter** sweep that turns the sound inharmonic and UFO-like
  - **ring modulation** gliding from growl to robot clang
  - **robot vowels** morphing a-e-i-o-u
  - a **comb-filter scream**
  - **laser zaps** (every 16th diving in pitch)
  - **accelerating stutters**
  - a **sample-rate dive** into digital grit

  Each scene picks two of these, so every section moves differently.
- Every move is level-matched to the bar it replaces and cross-faded in and out, so nothing clicks or jumps out of the mix.


## 2.2.1
- **A loading screen at start-up.** The window now opens straight away with an animated loading screen ("Loading the sound engine…", "Starting the studio…") while the engine loads behind it, then switches to the app. Before, nothing showed for several seconds, so it looked frozen. The page also shows a loading screen until the genres and sounds have arrived, and if something goes wrong it says so instead of staying blank.


## 2.2.0
**New genre: Switch-up Bass**

- Measured from your reference: 131.75 BPM, and a broken UK-bass kick (1, the "a" of 1, the "e" of 2, and a push into the next bar) that **never changes from the first bar to the last**. Underneath it, a one-note sub on the root rides the kick and carries most of the record's energy.
- **Same rhythm all song, new everything else.** Every section is its own scene: a new mid-bass layer (reese, growl, FM, wobble, neuro, hoover), new stabs and samples (rave, sampler, noise, soul horn, MPC keys), new vocal chops and a new perc voice. Each one gets its own effect (bit-crushed, phased, wah'd, flanged, driven, filter-swept or OTT'd). No part keeps the same sound or effect two sections in a row.
- **Drop-outs where the sub stops dead**, and one or two **dark stretches** where everything on top is filtered down, like the record.
- Bass-heavy master (−9.5 LUFS, extra low end) and a mono-safe sub.


## 2.1.0
**Real-sounding guitars, a Grunge genre, and previews from the middle of the song**

- **Rebuilt guitars.** The old ones sounded synthetic for three reasons: each note of a chord was distorted on its own, left and right were one take made wide, and the cabinet was a plain low-pass filter. Now every guitar part is played twice (two takes, each with its own pick attack, pick position, a few cents of tuning and a few ms of timing), and the **whole part** goes through its rig together, so chords distort together like on a real amp. The rig is an amp, a speaker cabinet modelled on a real 4x12 / 2x12 / combo, and the effects the style uses.
  - **Metal:** down-tuned high gain. A tight boost in front, two hard stages, scooped mids, a V30 4x12 and a noise gate (the silence between chugs is part of the groove).
  - **Rock / punk:** a humbucker into a cranked plexi-style amp and a greenback 4x12.
  - **Grunge:** a fuzz pedal into a worn 2x12. Wooly, scooped, a little loose and out of tune.
  - **Country:** a Telecaster bridge pickup, a compressor for the snap, slapback and a little spring reverb.
  - **Jangle:** clean, chorused single-coil arpeggios for indie and 90s verses.
  - **Acoustic:** a dreadnought recorded with two mics (body and 12th fret), with strum noise and the odd finger squeak.
  - Solos are one player in the middle, not a wall, and guitar lows stay centred so the mix still works in mono.
  - Levels match the old guitars, so your mixes don't jump. The metal solo now sits on top of the rhythm wall instead of buried under it.
  - Rock, metal, nu metal, doom, punk, pop punk, garage, indie, post-punk, 90s alt, shoegaze, country, modern country, outlaw, bluegrass, folk, rockabilly and soft rock all use the new guitars, including when their sound pool picks one of the old ones.
- **New genre: Grunge.** Drop-D fuzz walls, clean chorused verses and crushing choruses, a heavy dry kit, minor and modal riffs.
- **Previews now play the song's first big chorus or drop**, from the middle of the song. Before, a preview could land on the last section or the outro, so you often heard the ending.


## 2.0.1
- **Surprise me generates straight away again.** A volume slider stopped it after it picked the random settings, so nothing played until you pressed Generate. The same fix applies to loading settings and presets.

## 2.0.0
**Studio Lab 2.0: SL2 merged in, a drawable energy curve, real groove templates, new synths, live note preview, ready-to-mix REAPER projects and a proper Windows app**

- **One Studio Lab.** SL2's ideas now live here. Its mix tools (true-peak limiting, round-robin hits, kick tuning, drum-bus glue and the mix check) were already merged in 1.97. Its **Euphoric UK Techno** genre is new: a simple, punchy broken kick and a heavy sub, then a long build where pads, rave stabs, plucks and a soaring lead stack up into a euphoric ending.
- **Generate and Play.** The main button is now **✦ Generate** (a new song). Next to it, **▶ Play** replays the last song. Once you change something, it becomes **▶ Play with changes**: the *same* song (same seed, sounds and note edits) played again with your changes, not a new song.
- **Draw the energy curve** (Song → Energy curve). Draw how the song should rise and fall, or start from Slow build, Two drops, Peak at the end or Arc. The arrangement follows your curve: low parts thin out to pads and chords, mid parts drop the drums, and high parts bring everything in.
- **Groove templates** (Groove feel → Classic feels): MPC swing 54/58/62 %, boom bap, drunk (very loose), UK garage shuffle, techno shuffle, tight trap, drill bounce and DnB roll. Each template moves each part differently, the way producers set it on their machines. Trap, drill, techno, DnB, boom bap and garage now use these by default.
- **New synths for trance, techno and hip hop:**
  - PWM pad, formant lead, FM perc, mod sequence, noise stab, sliding 808, 12-bit MPC keys (with crackle), soul horn and scratch.
  - Each one is in its genres' sound pools: the hip-hop scenes get MPC keys, soul horns and scratches; trap and drill get the sliding 808; techno gets noise stabs and mod sequences; trance gets the PWM pad and formant lead.
- **Live preview in the editor:** clicking, adding or moving a note plays that note on the track's own sound, straight away. Turn this off with 🔊 hear notes. In the editor, **▶ Play with changes** replays the song with your edits.
- **DAW project:** the DAW pack's REAPER project now opens ready to mix:
  - Each section has a marker and region, and the tempo map follows half-time breakdowns and tempo changes.
  - Every stem is on its own colour-coded track, and the drums sit in a Drums folder.
  - The full mix is on a muted reference track, and every part's MIDI is on its own muted track, ready for your own instruments.
  - A *Sections (markers).txt* file lists the section times for other DAWs.
- **A real Windows app:** Save buttons open the normal Windows Save dialog (and show the file in Explorer when it's done) instead of downloading the file like a browser.
- **Cleaner look, same layout:**
  - The result card is simpler: one row of actions (Full song, Edit, Extend, New sounds, ⋯, 👍👎). Parts, Play and *Like this* sit under **🎛 Tweak this song**, which remembers whether you leave it open. Skip intro and A/B are in the ⋯ menu.
  - Hover and focus states are calmer, inputs and scrollbars are tidier, and the hierarchy is clearer throughout.

## Older versions
The 1.x versions and earlier are in [docs/CHANGELOG-1.x.md](docs/CHANGELOG-1.x.md).
