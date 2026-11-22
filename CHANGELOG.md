# Changelog

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

## 1.97.0
**Slam / brutal deathcore, a cybergrind that never writes the same song twice, more professional mixes, and a tidier result card**

- **New genre: Slam / brutal deathcore**, built from your four reference tracks. What I measured, and what the genre now does:
  - **Mostly a wall of blasts and double kick** (65–85 % of the time in the references), with slam grooves in between.
  - **Breakdowns that are never the same.** Every breakdown in a song sits on its own pulse (one hit every 0.3 to 1.3 s in the references). Each one is now written fresh from eight kinds: kick-locked chugs, half-time slams over double kick, stop-start hits, triplet grooves, quarter-note beatdowns, gallops, crawling drags and pinch-squeal climbs. Each also gets its own phrase (2 or 4 bars, with an ending that answers it), tempo (full, ¾, ⅔, ½ or slower), snare and cymbals, and its own riff notes (the b2 rub, the tritone, squeals up to the octave). A song uses kinds it hasn't had yet, and no breakdown can repeat an earlier one.
  - **Breakdowns pile up toward the end** in most songs (as in the references), and the heaviest, slowest one comes last.
  - **Lower tuning, a clickier kick and a brutally loud master**, with the tone matched to the references.
- **Cybergrind rebuilt from your twelve reference tracks.** Before, every cybergrind song used the same nine-part form. Now:
  - **Every song gets its own layout:** a different opening (cold breakdown, blast, chiptune, a sample-style stop), 5–9 parts in a new order, and a different ending. Across 40 test songs, no two layouts were alike.
  - **Built on ~125 BPM like the records**, switching all the time: double-time blasts, half-time breakdowns, slam grooves, dead stops and quiet chiptune moments in the middle of the song.
  - **Mostly breakdowns and grooves, blasts only in short bursts**, matching the references (about 45 % breakdown, short blasts, songs 45–110 s).
  - **Every breakdown is new**, from the same generator as slam.
- **More professional mixes** (also in SL2):
  - **Drum-bus parallel compression:** a hard-squashed copy of the kit blended under it, so the body and room come up between the hits and the transients stay untouched. Electronic genres get 28 %, bands 15 %, orchestral none.
  - **Room for the lead:** chords, pads and arps now share a music bus that dips 3 dB at the lead's own frequency, only while the lead plays. The melody sits on top without the whole bed being turned down.
  - **Sub harmonics on electronic bass:** the bass's own upper harmonics, so the bass line is still heard on phones and laptop speakers.
  - **Sends follow the arrangement** in electronic genres: wetter breakdowns and intros, tighter drops.
  - **The mix report** now measures how far the lead sits above the music, and warns when it's buried.
- **A tidier result card:**
  - **One row per part:** each part's 🎲 new version, 🔒 keep and ♥ like buttons sit together.
  - **Main buttons up front:** Full song, Edit, Extend and New sounds. Use settings, Share, Save preset and Keep moved into the **⋯** menu.
  - **Sounds folded away:** the sound list is behind a *Sounds* link.
- **⇥ Extend:** the same song, longer. Every section gets more bars (1x → 1.5x → 2x), with the same parts and sounds.
- **The engine:**
  - A section can now run at its own tempo.
  - A section's drums and riffs can span a 2- or 4-bar phrase instead of repeating one bar.
  - Written layouts keep their 1- and 2-bar parts instead of being rounded up to 4 bars.
- **The genre matcher** now knows your 16 records (measurements only, no audio): 14 of 16 land in the right genre's top 3.
- The genre docs (`docs/GENRES.md`, `GENRE_LIST.txt`, `GENRE_SPEC.md`) are regenerated; they were behind the code.

## 1.96.0
**Sunlit electronica, wave, a new monster surf band, cleaner bass, and a wrapping mixer**

- **New genre: Wave (ethereal half-time, 808 sub, vocal chops)**, built from your two newest reference tracks. What I measured, and what the genre now does:
  - **Half-time at 140–155 BPM,** with the snare and clap on the 3 and busy trap hats with rolls.
  - **A huge held 808 sub** that slides between notes and carries the track. It holds most of the energy, so the mix is built around it.
  - **Slow, washed maj7 harmony** that hangs on one or two chords.
  - **A long intro with no low end:** 24–40 bars of airy pads and breathy vocal chops.
  - **Pads and chords that pump on every beat.**
  - **The tone** is matched to the references.
  - **Two new sounds:**
    - **Wave bass:** a held, saturated 808 sub that slides.
    - **Ether chop:** a breathy sung vocal chop.

  A style can now also let its bass slide into the next note now and then.
- **New genre: Spooky surf - monster band (spring guitars, combo organ).** The 60s monster-theme surf band, rebuilt with better instruments:
  - **The riff:** a new baritone six-string doubles the electric bass on the creeping chromatic riff, through a dripping spring reverb.
  - **The organ:** a new reedy transistor combo organ, with thin, buzzy pulse tones and a fast, shallow vibrato instead of a round drawbar organ. It holds the chords and takes a creepy organ break.
  - **The rest of the band:** a horn section for the stabs, a new bright surf guitar for the melody and its own guitar break, and a new hard-hit early-60s kit with a rattling snare and tom fills.
  - **Every song is different:** each picks its lead instrument (guitar, horns, organ or sax), its length, its tempo and whether the melody is played or tremolo-picked.
- **New sounds:**
  - **Surf guitar:** an offset guitar's bright pickup into a loud clean amp, with a spring-reverb tank modelled for that wet "drip".
  - **Baritone twang:** a six-string bass through the same spring reverb.
  - **Combo organ:** a 60s transistor organ.
  - **Surf 60s drum kit.**

  The older spooky-surf and monster-theme genres can now pick these sounds too.
- **The brass section's name** in the sound list said "Synth brass", but since 1.67 it has been the modelled trumpet and trombone section. It now says "Brass section".
- **New genre: Spooky surf - modern monster theme (synths).** It's the 60s monster-sitcom sound rebuilt with modern synths:
  - **The riff:** the creeping chromatic riff (root, a half step up, back, a half step down) on a new fuzz baritone synth, locked to a driven saw bass.
  - **The band:** wide synth-brass stabs, a new detuned "creep organ", a harpsichord arp and a sliding theremin lead.
  - **The beat:** tight, punchy modern drums at about 150 BPM (kick, snare plus clap, 16th hats with rolls).
  - **The shape:** a ghostly organ and theremin breakdown, riser builds, and a big last riff that stops dead.

  It's in the Retro & Video Game group. Like the other monster themes, its melody is original. The two new synths (fuzz baritone, creep organ) can be picked in any genre.
- **Bass notes no longer pile up.** Each bass note kept ringing under the next one: in dubstep, over half of all bass notes still sounded at 55–70% when the next note began. The two notes added up, which caused the clipped-sounding starts and ends, and two detuned bass notes at once phased and glitched. Bass parts now play like a mono synth, so a new note cuts off the one before it with a short 6 ms crossfade. The sub layer's peaks dropped by about a third.
- **Reese bass glitch.** Each reese note started its four detuned saws at random positions, so fast reese lines jumped to a different swirl on every note and sounded glitchy. Every note now starts the same way.
- **Riddim chops** open and close over 3 ms instead of 1.5 ms (no clicks on each chop), and the notes end over 35 ms instead of 20 ms.
- **Sub-octave bass variants** no longer add an octave below 30 Hz. Down there you can't hear it, and it only ate headroom, which made the limiter pump. Their level is also trimmed to match the plain sound.
- **Two new genres from your 12 reference tracks:** Sunlit electronica and Daydream downtempo. I measured each reference's tempo, key, chords, drum pattern, sections, tone, loudness, stereo width and how much the pads pump, then compared generated songs against the same numbers until they matched. What the references share, and the new genres now do:
  - **Two tempo families:**
    - **Sunlit electronica, 112–122 BPM:** a warm live-room kit, a round mono bass or bass guitar pushing 8th notes, and pads that pump on every beat.
    - **Daydream downtempo, 74–95 BPM:** a dusty hip-hop break with a syncopated kick, the snare on 2 and 4, and soft swung hats.
  - **Harmony that barely moves:** two or three chords, one or two bars each, always coloured (maj7, m7, add9, sus2), and sometimes one chord vamped for minutes.
  - **How the songs unfold:**
    - A long intro with no bass: 12–24 bars of pad and guitar, with the hats creeping in first.
    - Then the low end and the full kit arrive together.
    - Long sections change by adding and removing parts.
    - A breakdown drops the bass.
    - The outro loses the sub first, then fades.
  - **The sound:** strong lows and low-mids, a steep roll-off above 2 kHz (warm, tape-dark), about −10 LUFS with real dynamics, and moderate width.
  - **The instruments:** a clean guitar picking into a dotted-8th delay, a second guitar answering it, a guitar frozen into a reverb pad, warm analog pads, and an understated gliding mono-synth melody. Each song picks its own palette, guitar figure, layout, tempo, chord loop, bass style and melody rhythm, so no two come out the same.
- **New sounds** (usable in any genre):
  - **Space guitar:** a clean guitar note frozen into a slow-blooming reverb pad.
  - **Sun pad:** a warm analog poly pad with a slow bloom.
  - **Soft mono lead:** a warm, gliding analog melody.
  - **Round mono bass:** warm, with its weight in the low-mids.
  - **Sun room drum kit:** a soft round kick, a warm dry snare and dark hats.
- **Pads can pump on every beat.** A style can now duck its pads on every beat of the bars the kick plays in, not only on the kick hits. This is the steady breathing you hear in sunlit electronica.
- **Long sections keep moving in more genres.** The step that brings parts in over long club sections can now be switched on for any style. The two new genres use it.
- **Preview starts on the last chorus or drop.** The quick preview used to start two bars before the first big section. It now starts on the last one, usually the fullest part of the song.
- **Mixer view wraps.** Channel strips that don't fit the window now move to the next row instead of scrolling sideways.

## 1.95.0
**Dubstep genres get the same treatment as house, trance and techno**

The song audit now knows dubstep's rules: a half-time beat (the snare on the 3), wobbles in time, a sub-bass voice that owns the low end, and the sparseness of deep and early dubstep. It found these problems, now fixed:
- **Off the 8-bar grid.** Most dubstep, brostep, melodic and deep / early dubstep songs had stretched 28-bar or 12-bar sections. They're now on the 8-bar grid.
- **Instrument soup:** up to 8–10 melodic sounds. Now there's one sound per part all song, except that a breakdown may move its chords or pad to another sound. Doubled parts use a sound of the same kind, and only melodic dubstep and chillstep keep an answering sound. Brostep and riddim still trade bars between several bass sounds, which is part of the style.
- **Deep, early and dark dubstep were too busy.** They used 5–7 melodic sounds where the real records keep 2–4. These styles now never swap or double sounds.
- **64-bar drops with nothing changing.** Long drops now get a lift halfway, and grooves build up, as in the club genres.
- **The half-time beat could get lost.** Two deep dubstep genres were being treated as straight-beat genres by the drum-variety step, which then added snare patterns on 2 and 4:
  - **Deep dubstep minimal:** its clap was written as a soft hit, which the detector missed.
  - **Deep dubstep rollers:** its "steppers" kick (one on every beat) made it look like house.

  Both stay half-time now. Steppers kicks are still allowed, with the snare on the 3. No other genre's groove classification changed.
- **Drops that drone.** Dubstep drops piled a held pad and dense chords on top of the wobble bass, so the mid-range droned. In dubstep, brostep, riddim and the deep / early styles, the pad now steps out in the drops and the chords thin to one short accent every two bars, so the bass owns the drop. Melodic dubstep and chillstep keep their pads, since lush is their style.
- **Boxy, mid-heavy mix.** Measured against seven classic UK dubstep records, the generated dubstep mix had its 250 Hz–1 kHz band only about 5 dB under the sub, where the records keep it about 15 dB under. The wobble now sits lower against its clean sine sub, and the master's tone match aims at the records' balance, so the sub leads and the mids stop crowding. Riddim, which had no tone target, now uses brostep's.
- **A last check** drops a doubled layer if a later step swapped its main part to a different kind of sound (e.g. a bell layer left on what became a pluck).

## 1.94.0
**House, trance and techno songs that behave like real records**

A new audit (`tools/song_audit.py`) checks generated songs against how real club records work: phrasing, arrangement changes, the groove, the bassline, the hook, the harmony and the energy shape. It found these problems, now fixed:
- **Instrument soup.** A song could use 8–11 different melodic sounds: the arp and chords switched to new sounds each section, an extra answer sound came in, and layers paired unrelated sounds. Club records keep a few sounds all song. Now, in house, trance and techno:
  - **One sound per part for the whole song.** Only a breakdown may move its chords or pad to another sound, like the piano in a trance breakdown.
  - **No answer sound in house and techno.** Trance keeps its call-and-response, since that's part of the style.
  - **Doubled parts use a sound of the same kind:** pluck with pluck, keys with keys, stab with stab, never a pluck doubled by a vocal chop. Trance leads still layer a supersaw with a pluck, which is the classic trance sound.
  - Songs now use 4–6 melodic sounds.
- **Sounds from the wrong scene.** The trance pluck no longer turns up in house or techno, and the festival anthem lead no longer appears in plain techno. Melodic techno keeps it.
- **Off the 8-bar grid.** Some layouts stretched to 20- or 40-bar sections. Club genres now always use multiples of 8 bars.
- **Long static stretches.** Some trance sections ran 40–48 bars with nothing coming in or out. Long sections now evolve on the 8-bar grid:
  - **Grooves build up:** two secondary parts are held back for the first 8 bars, and one for the next 8.
  - **Long drops lift halfway:** an extra part (a ride, a layer, the counter line) comes in.
  - **Very long house and techno drops** also let the hook step out for 8 bars in the middle.

Things the audit checked that were already right: the kick is four-on-the-floor in every bar outside breakdowns, claps land on 2 and 4, house basslines sit on the off-beats, hooks repeat, and nothing clashes with the key or the chord playing at the time. Borrowed chords, such as the major V in minor-key trance, are normal and are not counted as clashes.

## 1.93.0
**Batch generator**
- **🎲 Batch** (next to Full song) makes many full songs in one go: from 1 to 500, in one genre or several.
  - **Genre order:** genres take turns, or each song picks one at random.
  - **What changes from song to song:** tempo (within each genre's range), key, energy, complexity, sounds, length, layout and mood. Tick the ones you want.
  - **How songs vary:** an **even spread** (calculated so the batch covers the whole range evenly, within each genre) or **random**. A **How far apart** slider sets how wide the range is. Every song always gets its own seed.
  - The batch goes into the render queue, so the songs render one after another while you keep using the app.
- **The render queue now survives a restart.** Songs left in it come back paused the next time the app opens. There are new **Start / Resume** and **Pause after this song** buttons.

**Keep only the final files**
- A new export option, **🧹 Keep only final files**, for single songs, the queue and batches. After each full song is exported, it deletes the stems, per-part MIDI, DAW / LMMS / Waveform projects, sample pack and plugin guide. Only the song itself stays (MP3 / WAV / FLAC, plus its MIDI if you chose MIDI), along with a tiny settings file so it still opens in the editor. On a test song with stems, that freed 534 MB.

**Faster renders**
- **Parts render on several CPU cores at once** on full songs (up to 3 extra cores, one left free for the app). The parts come back identical: tested to the sample against the one-at-a-time render. Parts that use plugins, your own samples, sampled instruments or real drum kits still render one by one. Set `STUDIOLAB_WORKERS` to change the number (0 turns it off).
- **Mastering is about a third faster** (42 s → 27 s on a 4½-minute song) with the same result: the same loudness within 0.03 dB and the same peak.
  - The loudness search now runs on the song's loud parts instead of re-limiting the whole song up to eight times.
  - The true-peak meter skips stretches too quiet to matter.

**10 new synths** (all in key)
- **House:** rubber bass (bouncy tech-house FM), tremolo keys (electric piano pulsing between the speakers), disco horn stab, vocal bounce (an "oh-ah" chop that opens with the note).
- **Trance:** vowel-morph pad (a choir moving from "aah" to "ooh" through the breakdown), saw harp (a ringing plucked-saw arpeggio), rising unison lead (its detune and brightness swell as the note holds).
- **Techno:** warehouse stab (a dark hit in a big room), FM acid (303 squelch with an FM bite), tonal kick-bass (the rumbling pitched low end).
- **Polymeter sequences in techno.** In about half of techno, minimal, dub techno and tribal techno songs (fewer in tech house, acid house and festival techno), the sequence loops in 3, 5, 6 or 7 sixteenths against the 4/4 kick, so it lands somewhere new every bar. It uses the chord tones the part was already playing (`polymeter`: auto / on / off).

## 1.92.3
- **Dreamy synthscape songs no longer all sound the same.** Each song now picks, from its seed, one option from each of these lists. The genre keeps its character, but 12 test songs gave 12 different combinations.
  - **Sound palette:** sine, glass (glass keys, tape bell pulse, bloom lead), tape (dust piano, warm pulse, tape flute), choir (hum choir, sine pluck, glide tone) or warm (R&B pad, warm pulse, tape-wobble sine lead).
  - **Pulse figure:** triplet rock, triplet climb, 8ths, dotted, or a slow quarter-note swell.
  - **Sparkle on top:** falling or rising glitter, slow stars, or none. The middle arpeggio is also on or off.
  - **Layout:**
    - the swell;
    - a slow drift (everything eases in, two long swells);
    - two waves with a hush and a tape stop between them;
    - a hypnotic loop that slowly fills up.
  - **Tempo:** slow (94–102), mid (104–112) or lifted (112–120).
  - **Harmony:** a major vamp with the suspended V, a minor loop, a lydian float, a dorian haze, a mixolydian glow, or major steps.
  - **Bass:** stutter entrances, long held roots, or a soft half-note pulse.
  - **Lead rhythm:** flowing, sparse or busy.
- Your own sound picks in the editor still override the palette. Any genre can now vary its songs this way (`song_variations`).

## 1.92.2
- **Dreamy synthscape: no more kick.** The original track has no real kick: its only regular low thumps sit about 40 dB below the music, and the pulse itself is the heartbeat. Our audible straight kick under the triplet pulse is what sounded off, so it's gone.
- **The bass now comes in the way the original's does:** about every two bars (every 4–6 seconds), struck three times in a quick triplet stutter, held for about two and a half beats, then space. It also sits lower, around 100 Hz like the original, and a little louder. The low end matches the original within a few dB.

## 1.92.1
- **Dreamy synthscape: the bass no longer feels off the beat.** The bass and kick notes always landed together, but the mix made them feel apart:
  - **The bass was ducked by the kick** (sidechain, plus the kick / bass dodge). It dipped on every beat and swelled back in between, so the low end pumped on the off-beats. It now holds steady and peaks right on the kick.
  - **The pulse was ducked on straight quarter notes** while it plays in triplets, so the ducking fought its rhythm. It's now ducked only slightly, and the pads breathe less.
  - **The round bass spoke slowly.** Its attack went from 40 ms to 12 ms, so it lands with the kick.

## 1.92.0
**More sounds in every genre, and everything kept in key**
- **22 new sounds**, each filed with the genres that use them:
  - **Chill / synthscape:** tape flute, glass keys (a soft sine electric piano), hum choir, dust piano (felt piano on cassette), bloom lead, tape bell.
  - **House / garage / disco:** chord-memory stab, deep FM bass, filtered disco chord.
  - **Techno:** FM bleep, ping chord (dub techno).
  - **Drum & bass:** jungle sub, atmos bell.
  - **Trap / drill:** choir stab, dark bell.
  - **Pop / afro / latin:** vocal pluck, wood pluck (afro house, amapiano), dembow lead (reggaeton).
  - **Retro:** DX electric piano, square arp.
  - **Hauntology:** shortwave tone, tape organ.
- **118 slight variations of the most-used sounds.** Each has a darker or brighter filter, a softer attack, a chorus double a few cents either side, an octave or sub-octave layer, a gentle tape wobble, or a little drive. Every genre now picks up to two variations of its own sounds per part, so songs in one genre don't all sound alike. A genre's signature sound accepts its own variations.
- **Nothing off key.**
  - The new sounds use only whole-number (harmonic) overtones.
  - The renderer now tells every sound which notes are in the song's key. Sounds that stack intervals on one note use the key's own intervals:
    - the colour bass's third and fifth;
    - the tanpura drones on the fourth when the fifth isn't in the key, as players do;
    - the trailer braam drops its fifth when it isn't in the key;
    - the industrial stab ring-modulates on the octave.
  - Fixed: the **tape keys** sound wobbled about 75 cents, audibly out of tune. It's now about ±6 cents.
  - Fixed: the **glint chime** had off-key bell partials. It now uses harmonic ones.
  - All 385 melodic sounds and the 118 variations were pitch-checked at three octaves. The only sounds that read off pitch are intentional: detuned stacks such as supersaws and hoovers (their normal chorus spread), the organ's octave stops, pitch sweeps and drops, and the gamelan's own tuning.

**Dreamy synthscape**
- **The lead was too quiet.** The whistle lead is up about 8 dB and now sits on top.
- **It felt slow.** The tempo was right (about 107 BPM), but the original moves in triplets, three notes per beat, and ours pulsed once per beat. The pulse and the glitter arpeggios now run in triplets. The pulse rocks between two or three nearby chord tones, like the original. The rhythm now measures the same as the original (pulses at 3x and 1.5x the beat).
- **More sounds to choose from:** bloom lead, tape flute, hum choir, glass keys, dust piano and tape bell join its pools.
- **Harmony:** a vamp on the home chord's maj9 with a suspended V and the vi7 now and then (in A-flat: Abmaj9, Ebsus4, Fm7). Some songs instead loop on the relative minor (C minor: i – VI – III – VII), using the same notes.

**Song structure: several layouts per genre, plus club layouts measured from real records**
- **House, trance, dubstep and drum & bass now choose between several layouts**, a different one per song:
  - **House:** a DJ layout (a long intro the parts come into, a long main section, a mix-out) and a song edit (two hooks with a breakdown between).
  - **Trance:** a double-breakdown layout (a short break into the first drop, then the long one into the big drop) and a progressive layout (one long journey: a long groove, one big breakdown, one long drop).
  - **Dubstep:** a VIP layout, where the second drop switches to a different bass, and a fake-out layout, where the first build stops on a stripped beat for a few bars, builds again, and then the real drop hits.
  - **Drum & bass:** a DJ layout (a drums-first intro for mixing in, a switch-up second drop, a drums-and-bass outro) and a roller (the drop keeps going and switches up before the break).
- **Club layouts from real records.** Section lengths in 16 dubstep, drum & bass and trance records were measured (an intro rolling straight into the drop, 64-bar drops, 16- or 32-bar breaks), and each genre got a layout in that shape. Pick **Extended / club** to get it. The genres also use it now and then on their own. These songs run about 5 minutes. Before, drops were about half that long.
- **Parts come in one after another** in club intros (kick, hats, bass, snare, pads, arp, lead, each on its own 4-bar line). In club outros they leave in reverse.
- **Long drops take a breath.** At some 16-bar phrase ends, the kick and bass drop out for two beats or a bar, or everything stops for a beat, then a crash brings it back.
- Those records were also added to the "sounds closest to" matcher.

**Windows: a real StudioLab.exe to pin to the taskbar**
- The installer now puts a **StudioLab.exe** with the app icon in the program folder, and the Start menu and desktop shortcuts point to it. Right-click either one, or the running app, and choose **Pin to taskbar**.
- The app window now uses the same taskbar identity as the pinned icon, so they share one taskbar button instead of the window showing up as a separate "Python" or Edge button.
- The installer also includes the built-in app window (pywebview). If it's missing, the app falls back to an Edge app window as before.
- Installs that update themselves inside the app don't get the launcher. Run the new Setup.exe once to get it.

**New genre: Dreamy synthscape** (Chill, Lo-fi & Ambient)
- Modelled on a chill synth piece, measured layer by layer. Almost every layer is a near-pure sine: two copies a hair out of tune beating slowly (about 1.2 Hz), a slow tape wobble (about 7 cents), nothing bright and no sub. There are no real drums; percussion is a quarter of a percent of the energy.
- Six new sounds, built to match:
  - **sine pad**: the slowly beating chord drone;
  - **sine pulse**: soft chord tones that speak, settle about 6 dB and hold, played in quarter notes against a muffled heartbeat kick;
  - **round bass**: a pure sine around 100 Hz, in the fuller parts only;
  - **whistle lead**: a smooth sine that slides from note to note and wavers about ±40 cents, like a gently played whistle or theremin;
  - **sine pluck** and **glint chime**: the background arpeggios. One is faint, around C5. The other glitters in octave 6, walking down the chord and fading through each 8-bar phrase.
  - Also **warm pulse** and **glide tone** as alternatives.
- **Harmony:** a near-static vamp on the home chord's maj7 / maj9 with a **suspended V** and the vi7 now and then (in A-flat: Abmaj9, Abmaj7, Ebsus4, Fm7). The voices keep the notes the chords share.
  - Any genre can now name chords to voice as sus4 (`sus_degrees`).
  - Any genre can add extra arpeggio layers that walk the chords at their own rate, direction and register (`arps2`).
- **Form and mix:** one long swell (quiet, fuller, a hushed middle that ends in a dead tape stop, back in, fade). A steep cut below the bass (`sub_cut`) and a tone target taken from the original keep the mix within a few dB of it from the bass to 4 kHz.
- Gentle genres skip the drop-evolving and call-and-response moves.

## 1.90.1
- **Call and response at even volumes.** When a second sound answers the lead in the hooks, the answer is now matched to the lead by how loud it sounds to the ear, not by its raw level. The lead's doubled layer is counted too. Before, the answer could come in noticeably louder or quieter than the lead, depending on the two sounds: up to about 8 dB apart in the songs checked. It now sits just a touch under the lead.

## 1.90.0
**Songs with real ups and downs**
- **Section dynamics** (electronic genres): the second, doubled sound on the lead, chords or bass is now saved for the drops. Verses and intros play one sound per part. Breakdowns start bare and get their layers back halfway through, so a drop adds weight instead of only getting louder. The first downbeat of every drop also lands harder.
- **Genre fills and transitions:**
  - **Drum & bass, jungle, garage and grime: the rewind.** A few bars into the second drop, the record spins backwards and the drop starts again from the top (sometimes with a shout).
  - **Dubstep, brostep, riddim and a few loud cousins: the drop stop.** Everything cuts out for a beat before the drop, and a hype-man shout ("oi", "yeah", "go"…) fills the hole. The shout is synthesized inside the app, so there's no sample to clear.
  - **Trance: the snare roll climbs in pitch** through the build (an octave on the last one), while the pads' filter opens on top of the high-pass sweep.
  - Switch either feature off with `section_dynamics` / `genre_fills`. Turning transition effects off also turns off the fills.

**App**
- **Undo and redo for the whole app.** Ctrl+Z / Ctrl+Shift+Z (or Ctrl+Y), or the new ↶ ↷ buttons in the top bar, step back through changes to the main settings: a sound pick, the genre, a slider, the part levels or the mixer. Section edits on a finished song aren't included. While the notes editor is open, Ctrl+Z still undoes notes.
- **Genre map** (🗺 next to Styles). Find a genre and see the genres that sound closest to it around it, each with a reason (same family, same tempo, half or double time, four-to-the-floor, half-time drums). Click a circle to move there, or use the genre you land on.
- **Render queue** (＋ Queue next to Full song). Queue full songs with their settings as they are now, keep changing things, and queue more. They render one after another. You can reorder the queue or remove songs from it.
- **Favourite sounds and favourite genres no longer get mixed up.** They used to share one saved list, so starring a genre could go through the sound list. Your sound favourites move to their own list automatically. Both lists, along with the other app settings, are kept in the app's settings file, which now holds bigger lists.
- **"Sounds closest to" (reference matching)** now reports tempo on the scale each genre uses. A song read at half or double speed, or at a 3:2 ratio, is matched to the right genre and given that genre's tempo when you use it. New ÷1.5 / ×1.5 buttons sit next to ÷2 / ×2. On the 72 reference records, when the right genre is suggested its tempo is now right 42 times out of 49 (up from 21).

**Sound and mixing**
- **Previews sound like the full song.** The tone part of the production pass, which the full song already got, now runs on previews too (quickly, after the master).
- **Era check on genre sound lists.** When a genre borrows sounds from related genres, it no longer picks up ones from the wrong era or the wrong mood. That means no modern festival plucks, hypersaws or vocal chops in 90s, synthwave, chiptune or jungle genres, and no brutal bass-music sounds in deep or gentle ones. 24 borrowed sounds were dropped from 13 genres. `tools/pool_audit.py` lists them.
- **Less memory.** A full render uses about half the memory it did (a 5½-minute trance song went from 6.0 to 3.2 GB, a 3½-minute dubstep song from 4.0 to 2.0 GB), with the same sound. The changes:
  - the mix stays in 32-bit;
  - true-peak limiting and clipping run in chunks;
  - the compressor and loudness meter work one channel at a time;
  - each part's notes are freed as soon as the part is rendered.

## 1.89.0
**8 more trance synths**
- A **gated choir**: an "aah" pad chopped in a 16th trance-gate rhythm.
- A **breakdown piano**: a bright piano layered with a soft saw pluck an octave up.
- A **trance sequence**: a mono saw whose filter snaps open on every 16th.
- A breathy **trance flute** with glide and vibrato.
- A **vocoder chord** (robot choir).
- A hollow **trance pizzicato**.
- A distorted, pitch-bent **raw lead** for hard trance.
- A tight **off-beat trance bass**.
- They are added to all the trance genres, including classic vocal trance and festival techno. Uplifting trance's protected lead accepts the trance flute and the classic trance lead.

**8 more dubstep synths**
- A **laser bass**: diving FM zaps in 16ths or triplets.
- A **robot bass**: a talking ring-mod voice.
- A blaring FM **dubstep horn**.
- A **dive bass** that drops an octave over each note.
- A **creak bass**: a creaking comb-filter growl.
- A soaring **melodic dubstep lead** with pitch bends.
- A **color bass**: a wobbling chord-bass that carries the harmony.
- A **stab wobble**: short, stuttering wob hits.
- They are added to dubstep, brostep, riddim, melodic dubstep and future bass; dubstep's and brostep's protected bass accepts them. Deep, minimal and early dubstep keep them out.

## 1.88.0
**22 more synths, filed with the genres they were made for**
- **Retro / synthwave:**
  - **swelling poly brass**, whose filter and pitch rise as the note is held;
  - **outrun bass**, punchy, for driving 16ths;
  - an 80s **digital wavetable bell-pad**;
  - a gliding **synthwave lead**;
  - an 80s **synth slap bass** (also in city pop, new jack swing and electro funk).
- **Future bass / pop:**
  - a wavy, wide **future bass chord**;
  - a **kawaii pluck**: a bright square with an octave blip;
  - a woody **tropical pluck**;
  - a sung "ooh-aah" **vowel lead**.
- **Lo-fi / R&B / trap:**
  - **tape keys**: a wobbly cassette e-piano;
  - a bit-crushed **crushed piano**;
  - a dark, silky **R&B pad**;
  - a bright **trap bell pluck**;
  - a round, sliding **sine lead**.
- **Ambient / cinematic:**
  - a **shimmer pad** with an octave halo;
  - a **reverse swell** that sucks into the beat;
  - a glassy **ice bell**;
  - **bowed glass**;
  - a **swelling guitar** with bowed sustain;
  - an airy **wind pad**.
- **Chip and acid:**
  - a **chip lead** with a duty-cycle sweep and vibrato;
  - an **acid square**: the 303's square-wave voice. Acid house's protected acid bass accepts it.
- Each is added to the genres it suits, about 40 of them, including ambient, film, post-rock, shoegaze and chiptune genres that hadn't been getting new sounds.

**Fixed**
- **Mid-song instrument rotation** works for the newer synths again. Sounds added since 1.57 belonged to no instrument family, so a song led by one of them could never swap it for a related sound in its verses and breaks. Every built-in sound now gets a family from its description (pad, keys, mallets, synth, bass).
- Genres whose scene has no shared sound list now get the sounds made for them as well.

## 1.87.0
**Tuned on seven more sets of reference records**
- **Tone targets measured on the records** for ten genres: the band balance of their loud parts, used by the master and the production pass. The genres:
  - ambient electronica (three hauntology styles);
  - early and deep dubstep;
  - the electro-dubstep genre (brostep);
  - nu-disco;
  - smooth jazz horns;
  - drum & bass;
  - cybergrind.
- **Loudness targets moved toward the records:**
  - early and deep dubstep -11 LUFS (masters of that era are quieter and more dynamic);
  - ambient electronica and smooth jazz horns -13;
  - nu-disco and DnB -8.5.
- **New synths:**
  - a **square wobble** (the simple, slow-LFO bass of mid-2000s dubstep) and a **saturated sine sub** for early dubstep;
  - a **warble pad** and a **warble lead** (detuned analog that drifts out of tune like an old tape) for ambient electronica.
- **Early and deep dubstep keep to their era's sounds:** square and sine wobbles, subs, grime squares, dark stabs, organ and bell. The modern brostep and riddim sounds that had crept into their lists are gone.
- **Cybergrind** now also plays 8-bit chip melodies, like its records.
- **Nu-disco** gets a talk-box lead; the electro-dubstep genre (brostep) gets 80s synth brass and an analog lead.
- **Nu-disco** has less sub and **smooth jazz horns** has more low end, closer to their records.

**A much better "sounds closest to" for reference songs**
- The genre matcher now compares a reference song with **real records** as well as with rendered previews of each genre. It holds fingerprints of 72 records across 19 genres: only measurements, no audio or titles.
- Its weights were tuned on those records, mainly weighing tonal balance more. Each record was scored with its own fingerprint left out:
  - the right genre first: 6 → 18 of 72;
  - in the top 3: 11 → 36;
  - the right family in the top 3: 42 → 57.
- Genres without records get no penalty: there is no bonus for having records.
- New tool: `tools/record_fingerprints.py` adds records from a list (genre, file) and reports how well they're placed (`--eval`).

## 1.86.0
**Three new genres, each built from a set of reference records**
- **Dark dubstep (sub-weight, 2009-12):**
  - Half-time 140-144 with the snare on beat 3 and syncopated kicks.
  - A huge mono sine sub that is the loudest thing in the mix, under a new **dread wobble**: a dark, slow, low-passed growl.
  - New **grime square** riffs, **horror stabs** (dissonant metallic hits) and a **dub siren** thrown into the echo.
  - Very mono and dark on top, like the references (L/R correlation 0.94-0.98).
- **Classic vocal trance (2004-09):**
  - 136-140 in a minor key, with an off-beat rolling bass ducking hard under the kick and constant 16th hats.
  - A new **classic trance lead**: bright, singing, with glide and a delayed vibrato.
  - Gated supersaw chords, dreamy pads and a piano breakdown.
  - Long arrangements with a big quiet break in the middle.
- **Festival techno (big-room trance, 2011-14):**
  - 134-138, with the bass on the 16ths right after each kick.
  - A new **mega stab** (a very wide nine-saw supersaw) and a new **sync stab** (a tearing hard-sync hook).
  - Build pads, a pumping sidechain and very wide leads, like the references.
- These genres keep their own sound lists: shared scene sounds don't leak into them.
- The production pass no longer narrows a genre that is meant to be very wide.

**Parts panel reorganised**
- Every extra sound now sits under the part it belongs to: the genre's extra parts, layers, section switches, the call-and-response "answer" and instruments you added (an extra pad under Pad, a layered lead under Lead). Each has the same controls as the main parts: a searchable sound menu with ▶, mute, volume, octave and its own effects chain.
- **Drums:** every drum sound of your last song (kick, clap, hats, shaker, congas, build-up ride ...) has its own row in the Drums section, with a **volume knob**, mute, a searchable sound menu and ▶.
- Effects can now be set on one sound (one layer or extra part) instead of only on a whole part.

**Song editor**
- **Undo / redo:** ↶ ↷ buttons, Ctrl+Z, Ctrl+Shift+Z or Ctrl+Y.
- **Velocity:** a velocity lane; drag a note's bar up or down.
- **Note length:** drag a note's right edge.
- **Filter, reverb and pan lanes** next to the volume line, with points you draw for each sound.

**More**
- **MIDI import:** a MIDI file loaded as a reference can now give the song its **melody, chords or bass**. The notes are moved to the song's key and repeated through each section on the genre's own sounds.
- **Favourite sounds ☆:**
  - every row in a sound menu has a star;
  - favourites are listed first;
  - favourites are picked more often when a genre chooses sounds.
- **Sound browser** (Sounds & instruments → 🔎 Sound browser):
  - every built-in sound, filtered by part, by genre, by character (dark, bright, soft, aggressive) or by name;
  - ▶ to hear a sound, ☆ to make it a favourite;
  - "Use for…" puts it on a part.
- **⇄ A/B last two** button in the player bar (or the **B** key): flips between your two newest results at the same spot, loudness matched.
- **Faster previews:** unchanged parts are reused from the last preview, about 1.6-1.9x faster when you change one thing. A reused part is note-for-note and bit-for-bit what a fresh render gives.
- The production pass now runs on full songs and exports; previews stay quick.
- **Installers:**
  - all three installers are now built and self-tested every Monday;
  - a GitHub upload timeout can no longer stop a release (1.84.1 lost its Apple Silicon download that way).

## 1.85.0
**Songs that develop instead of looping**
- **Melody check:** each song writes four candidate hooks and keeps the strongest. Hooks are scored on:
  - range and steps with a few leaps;
  - a clear shape;
  - phrases that repeat with a change;
  - a high point late in the phrase;
  - an ending that lands on a chord tone.
  The rest of the song is unchanged.
- **Later drops evolve.** In electronic genres, the second and later drops each change something:
  - the lead climbs an octave halfway through;
  - the bass adds off-beat pushes;
  - the last bar stutters into the next section;
  - the last two bars go half-time;
  - the arp doubles the lead an octave up.
  The final drop gets two changes.
- **Call and response:** in about half of electronic and pop songs, a second sound answers the lead every other two bars in the hooks. It plays the lead's phrase, often an octave apart. It shows up in the editor as its own part, "answer".
- **4th / 8th-bar variation:** small changes at phrase ends so loops don't repeat bit for bit:
  - a dropped hat;
  - a ghost snare;
  - an arp note moved within the chord.
  Locked parts stay note-for-note.
- **Basslines step into the next chord** in house, funk, DnB, trance, pop and chill genres, not only the acoustic ones. 808s, acid lines and riff basses keep their written line.

**Transitions**
- New **risers tuned to the song's key**, one per genre family:
  - a supersaw that climbs two octaves with the filter opening and a stutter at the end (house, trance, big room);
  - an FM siren whose wobble speeds up (dubstep, bass music);
  - a noise sweep over a saw (DnB, breaks).
- **Impacts** are now a sub drop on the song's root note, with a noise burst and a short tail.
- **Downlifters** now fall in pitch and filter.
- All three widen as they move. Classic synth mode keeps the old ones.

**Production**
- **Sidechain shape per genre family:**
  - "pump" holds the dip, then swings back: big room, house, electro;
  - "breathe" is shallow and smooth: trance, deep and melodic house;
  - "tight" ducks only the kick's attack: DnB, breaks, dubstep.
- **Masters are never squashed flat:** the whole song keeps at least ~8 dB between its peaks and its loudness. Big room and dubstep masters had only ~7 dB left.
- **Reverb and delay step back while the lead plays** and bloom in its gaps.
- **Delay throws:** the lead's phrase-ending notes are thrown into the delay.
- **The production pass is now on by default.** After mastering, the mix check runs; anything it finds (tone far from the genre's references, too wide, squashed, harsh) is fixed and the song is mastered again. The better version is kept. It can correct tone by up to 5 dB per band, up from 3.
- **Reference matching by section:** a reference song's quiet part (its breakdown) is measured too. Your song's quiet sections are matched to it, and its loud sections to the reference's loud parts.

**Fixed**
- The plucked moog bass now closes its filter properly after the attack, so it is clearly darker than the sustained one.

## 1.84.1
- **Moog-style basses re-voiced: dark, round and warm.** The 1.84 version was far too bright: genres pass a filter setting tuned for the old bass, and the new one multiplied it up to seven times on every note, opening the filter past 6-10 kHz.
  - The genre's setting is now the most the filter ever opens, on a hard hit, and it settles well below that.
  - A gentle top roll-off keeps the fizz out.
  - A saw, a square and a square an octave down (moved up on the lowest notes so it never turns into rumble), over a solid sine fundamental.
  - Level stays even from note to note.

## 1.84.0
- **35 new synths for house, techno, drum & bass, dubstep, trance and festival music:**
  - House: a French-house filtered disco chord, disco strings (with the upward swoop), a bouncy UK garage organ bass, a warm Detroit chord pad, a house vocal stab made from scratch, and a deep house organ chord.
  - Techno: a hypnotic Berlin sequencer line, a harsh industrial stab, tuned metallic FM percussion, a dark evolving drone pad, a screaming peak-time lead, and a swooping rave hoover stab.
  - Drum & bass: an airy liquid pad, liquid e-piano keys, a bouncy jump-up bass, a deep roller bass, a talking neuro formant bass, and a phasing dancefloor reese.
  - Dubstep: a talking "yoi" vowel bass, a metallic FM screech, a gated square riddim bass, a talking growl that changes vowel within a note, a pure sliding sub, and a brutal tearout bass.
  - Dreamy trance and house: a wide floating pad that opens slowly, a soft singing lead with glide and delayed vibrato, an atmospheric air texture, a soft blooming pluck, and a clean supportive bass.
  - Festival and big room: a huge seven-saw anthem lead, a resonant festival pluck/stab with a noise click, a tight hard bass, a folded electro growl bass, and a rising build pad.
- **Every electronic genre checked so its songs rotate through all of its proper sounds.** Across 24 songs per genre, the median part now uses 92% of its genre's list:
  - Electronic genres now pick from their whole list more often, with no extra weight on the first sound.
  - The defining bass or lead still keeps its own sound more often than the supporting parts.
  - Fixed: when a bell or mallet sound wasn't allowed in a genre, it was always replaced by the same sound. It now picks any of the genre's own sounds.
  - Deep, minimal and liquid genres keep the brutal sounds out. Each new bass goes only into genres whose own bass plays the same kind of line.
- **Rebuilt the Moog-style basses** (sustained and plucked). The old ones beat against themselves, so notes swelled and thinned, and sat behind a dull fixed filter. The new ones:
  - Use three oscillators that restart on every note.
  - Have a key-tracked filter that bites on the attack and then settles.
  - Keep a solid fundamental, so the bass is fat and steady on every note.
  - The 1.57-1.83 versions stay available as "(1.57-1.83 sound)".
- **Rebuilt the reese bass so it no longer crackles like clipping.** The old reese drove its low fundamental into the distortion, which rippled the growl. Now only the mids are driven, and the sub sits lower against the growl, so it leaves the master more headroom. The old reese stays available as "Reese bass (1.59-1.83 sound)".
- **Sound menus now have search built in:** open any sound menu and type to filter it. Arrow keys and Enter pick a sound. Older versions of sounds are grouped at the bottom.
- **▶ Hear any sound before rendering:**
  - Each sound menu has a ▶ button that plays a short phrase for that part.
  - Every row inside the open menu has its own ▶, so you can try sounds without picking them.
  - Drum voices play a few hits.
- **Drum voices from any kit:** the kick, snare, clap and hi-hats can each come from any drum machine or real kit (a real kick under 909 hats, an 808 clap on a real kit).
- Fixed: the 808 variants (distorted, long, punchy) now get the same 808 treatment (slides, warps, high notes handed to the mid-bass) as the plain 808.

## 1.83.0
- **New genre: Dark drill (sliding 808s, wobble switch-ups),** measured on a reference record:
  - ~143 BPM; very dark on top, bass-heavy and mono.
  - A deep, distorted **drill 808** that slides between notes and changes its pattern from section to section, with a distorted grit copy of the 808 for presence on small speakers.
  - A short hard kick, an off-kilter snare on 3, and sparse skippy hats with triplet rolls.
  - An eerie lo-fi **dark sample bed** standing in for the chopped sample loop, plus bells and choir in the hooks.
  - A **wobble section** where the bass hands over to a new **wobble 808** (an 808 sub under a beat-synced wobble).
  - The arrangement follows the reference: sample-only intro, 808 and hats creeping in, hooks and verses, a short drop-out.
- **Jam band reworked into 70s psychedelic jam rock:**
  - The song goes head, then long modal jams on a two-chord vamp, a spacey drumless section in the middle, and back to the head.
  - A new **singing, sustained lead guitar** and a new **envelope-filter rhythm guitar** (the funky "quack").
  - Honky-tonk piano and Leslie organ, and a busier melodic lead-bass.
  - Two drummers spread left and right, with congas, tambourine and toms.
  - Pentatonic lead lines, a warm tape-era mix.
- **Fixed: hi-hats vanishing in the DJ-effect genres** (the 808 switch-ups, bass-warp trap and others). The "hat roll" DJ edit is meant to replace the last beat of one bar, but it deleted every hat from there to the end of the song.
- **Fixed: high 808 notes handing over to the second bass outside the sections meant for it.** Genres can now limit the hand-over to marked sections.

## 1.82.0
- **Mono-safe stereo on 69 instruments:**
  - Many voices made their stereo by copying the note into the right channel 1-2 ms late. Played back in mono (phones, club PAs, radio) that copy cancels part of the sound and hollows the note out.
  - Now the delayed copy goes into the side signal only, so mono gives back the note exactly.
  - A plucked instrument used to lose about 3 dB in mono; now about 0.5 dB.
  - Classic synth character keeps the old way.
- **Only one sound owns the sub:**
  - When two basses play together, a sub-type sound (sine, 808, deep bass) takes the bottom and the other is high-passed.
  - With no sub-type sound, the main bass keeps the low end and its layer is cut below 110 Hz.
  - An audit of every genre (3 seeds each) now finds no electronic genre with two full-range basses stacked. The remaining pairs are natural ones: celli over contrabass, a surf guitar doubling the bass.
- **Faster:**
  - The moving low-pass behind filter rides and filter arcs is now one smooth per-sample pass.
  - A trance preview renders about 1.5 s faster (13 s to 11 s).
  - Long sessions were checked: render time and memory stay flat from song to song.

## 1.81.0
- **7 new trance synths**, offered right after each trance genre's own sounds (trance, uplifting, progressive, club 2000s, early-2010s progressive, vocal-trance remix, electro-prog, 90s trance-pop, hard trance):
  - **Classic trance pluck:** detuned saws and a square, a snappy filter and a wide chorus, made for 1/16 arps into a dotted delay.
  - **Trance bell:** an FM bell layered with a short pluck.
  - **Uplifting screamer lead:** a wide supersaw stack plus a pulse an octave up, with long glide, delayed vibrato and a touch of grit. Now also a valid lead for uplifting trance.
  - **Trance strings:** a warm string-machine ensemble that swells in, for breakdowns.
  - **Laser pluck:** a pitch-diving "pew" arp (hard trance gets it first).
  - **Uplifting supersaw stab:** a filter "bwow" on the off-beat chords.
  - **FM rolling bass:** the trance roll with an FM "tok" for bite, over a clean sub.
- A part that a genre's authenticity check protects can now take sounds that check already accepts.

## 1.80.0
- **Song editor > new "Notes & volume" tab:**
  - A piano roll of any sound in the song (lead, layers, drums, section sounds), with that sound's **volume line** underneath and every other sound's line shown faintly behind it.
  - **Volume line:** it starts from the programmed one (full where the part plays, silent where it rests). Drag a point, double-click to add one, right-click to remove it; the bottom of the lane is silent.
  - **Notes:** click to select, drag to move (in time and pitch), Delete to remove, double-click to add.
  - **↺ Volume line** and **↺ Notes** undo one sound's edits.
  - Edits are saved with the song's settings, so **Preview** / **Full song with these changes** and later re-renders keep them.
- **🎲 Re-roll sounds now re-picks everything you hear:** the main sounds, the layers under them, the sounds that take over in other sections, and the drum-machine voices. Every note stays the same, so a re-rolled song really does sound different. **↺ Genre sounds** goes back.
- **Clipping bass fixed (DnB and other layered basses):**
  - When a clean sine sub is layered under a mid bass (reese, growl, saw ...), the mid bass is now high-passed above the sub. The two subs on the same notes used to beat against each other and spike into the limiter.
  - The mastering clipper now works only above 150 Hz, so it can't flatten a bass wave.
  - The final limiter holds for a whole 40 Hz cycle, so its gain no longer wobbles inside a bass note.
  - The example DnB song now masters 3 dB louder with more low-end headroom.
- **Production tools** (Mix & master):
  - **Master for:** Radio (dense, even), Vinyl cut (mono-safe lows, gentle highs, dynamic) or Film / picture stem (-18 LUFS, no squeeze).
  - **Production pass:** after mastering, Studio Lab reads its own mix check (stereo, punch, tone against the genre's references, harshness), fixes what it finds and masters again from the same mix, keeping whichever version checks better. The result card lists what it changed.
  - **Match a reference > match its tone:** the master is steered toward a reference song's tonal balance, not just its tempo, key and loudness.
  - **Section width (analog character, electronic genres):** intros, breakdowns and builds sit a little narrower, so the drops open up wider.

## 1.79.0
- **5 new genres**, each measured on reference records you sent: tempo, key, tonal balance, loudness, loudness range, stereo and how the energy moves.
  - **Spooky TV theme (90s mystery):**
    - a slow electronic groove;
    - an echoing four-note piano ostinato in a long delay;
    - dark pads and a lonely, sliding **whistled** melody;
    - very wide and reverb-soaked, quiet and dark on top.
  - **UK R&B / swingbeat (mid-90s):**
    - a heavily swung 96 BPM sampled-loop groove;
    - deep round bass, e-piano and organ 7th / 9th chords, string swells;
    - thick, warm, loud and nearly mono.
  - **Vocal-trance club remix (late 2000s, instrumental):**
    - a long DJ intro, then a driving rolling 16th bass and a gated tech-trance riff;
    - a huge breakdown with an airy vocal-like pad where the singer would be;
    - a full lead drop, with real contrast between the breakdown and the drops.
  - **Cybergrind / drum-machine deathgrind:**
    - songs about a minute long: programmed blasts, a machine-gun double kick, gravity runs and bounce parts;
    - crushing breakdowns where the kick hits with every guitar chug.
  - **Switch-up deathcore:** the switch-up 808 engine (a new 808 move every bar) under deathcore breakdowns and blast bursts, with the guitars chugging in time with the kick.
- **Retuned on references:** early-2010s progressive trance (darker top, louder) and sunny melodic house.
- **New sounds:**
  - **Whistle.**
  - Three synths modelled on 2000s and 2010s drum & bass:
    - **Electro saw** (a talking, distorted saw stack);
    - **Tech / neuro bass** (metallic, rolling, with a clean sub);
    - **Dancefloor DnB stab** (anthemic).
  - They're offered in DnB (not liquid, which stays soft) and selectable in any genre.
- **The middle panel is reorganised:**
  - **Melody & harmony:** complexity, simplicity, repetition, melody range, melody theme, lead and melody style, counter-melody, chord speed, voicing, colour, bends, vocals.
  - **Groove & drums:** energy, swing, humanize, groove feel, bass rhythm, drum style, percussion, drum sounds and mutes, drummer.
  - **Parts:** every sound, plus the synth character, brightness and vinyl.
  - **Arrangement:** now also holds Variety and layered sounds.
  - Voice sample stays above Parts, and Basics stays at the bottom by the Preview bar.
- A breakdown can lock its kick to the guitar chugs (`kick_riff`). Sections can bring their own riffs and drum patterns.

## 1.78.0
- **12 new part effects** (Parts panel > **+ FX**). The genres also pick some of them now and then:
  - **Auto-pan:** 1/2 note or slow over 2 bars, with the low end kept in the middle.
  - **Stutter fills:** the last beat or two of a section repeats in 16ths and then 32nds into the next one.
  - **Shimmer reverb:** a long hall whose tail rises an octave.
  - **Tape echo:** dark, worn, wobbly dotted-1/8 repeats.
  - **Ring mod** and **frequency shifter**, for metallic and swirling effects.
  - **Transient punch** and **soften:** a snappier or rounder attack.
  - **De-esser** for voices and choirs.
  - **Volume shaper:** pumping drawn as a curve on every beat, even when no kick is playing.
  - **Reverse swell:** a backwards reverb that rises into each new section.
- **21 new instruments:**
  - **World:** handpan, duduk, erhu, guzheng (with its pressing vibrato), pipa (with its fast tremolo on long notes), dizi (with the buzzing membrane), kora, balafon (buzzing gourds), hurdy-gurdy (with drones), cimbalom.
  - **Rare colours:** theremin, glass harmonica, waterphone.
  - **Synth engines:** a morphing **wavetable synth**, a **granular pad**, **formant vocal chops** (no sample needed), a **hollow pluck**, and three 808s (**distorted**, **long glide**, **punchy**).
  - **Down-tuned metal guitar:** two separate takes hard left and right, and a gate that stops each chug dead.
  - They're offered where they fit: handpan and granular pads in chill and ambient genres, the theremin in trip-hop and spooky surf, kora and balafon in Afro house, and so on.
- **Every sound has its own level** (song editor > each sound's card > **Level**, -24 to +9 dB). This includes layers, extra parts and the layered kick; muting them was already possible.
- **DnB layered kick:** it was too much.
  - The layered kick now carries the low end with a rounder body and a softer click.
  - The break's own kick sits underneath as a quiet ghost knock.
  - These settings come from measuring kick level, length and knock on reference DnB tracks.
- A song section can now bring its own drum pattern and riff (used by the metal genres that follow).

## 1.77.1
- Installers: numba (the optional speed-up for the analog filter and reverb) is added only where a ready-made build exists. The Intel Mac installer build failed trying to compile it. Without numba, the app uses its fallback filter and reverb.
- Smoke test: quiet solo genres (solo piano) may sit near -20 LUFS (the loudness meter is exact since 1.76).

## 1.77.0
- **The electronic synths sound played, not programmed** (Sound panel > **Synth character: Analog**, on by default):
  - **Every note is its own take.** Before, every repeat of the same note was the exact same copy, which is the "machine-gun", MIDI-file sound.
    - Now each note picks one of three takes, with tuning, filter cutoff and envelope times varying slightly from note to note, like a real analog poly.
  - **Velocity shapes the tone**, not only the level: a harder note is brighter, with more filter envelope and a little more drive. Three velocity layers per note.
  - **Drum-machine accents:** harder hats, claps and snares are brighter as well as louder; soft ones are duller.
  - **New ladder filter:** a transistor-ladder model, worked out sample by sample.
    - Plucks and stabs close smoothly instead of in small steps.
    - The resonance follows the cutoff and compresses on loud notes.
    - It's about 3x faster than the old filter.
  - **Filter rides:** on electronic chords and arps, the cutoff drifts slowly open and closed over 8 or 16 bars, each part on its own cycle. A long loop keeps moving, the way a producer rides the knob.
  - **New reverb:** early reflections, then a dense, slowly moving tail whose highs die away faster than its lows, like a real room or hall.
  - **Classic (before 1.77)** brings back the old sound exactly. From the command line: `--synth classic`.
- **New club synths**, offered right after each genre's own sound in house, techno and trance:
  - **House chord stab** (chord-memory stab with a pitch snap and a noise tick);
  - **Dub-techno chord** (dark, for long echoes);
  - **Techno bleep** (an FM blip);
  - **Hypnotic techno sequence** (resonant, a little different on every note);
  - **Layered trance pluck** (supersaw + an octave-down body + an attack tick);
  - **Analog mono lead** (breathing, with glide and delayed vibrato);
  - **Split club bass** (a clean sine sub under a filtered top).
- numba (optional speed-up) is installed quietly by the installers and start files wherever a ready-made build exists. Without it, the old filter and reverb are used.

## 1.76.0
- **One tune per song** (Feel card > **Melody theme**, on by default):
  - The verse, chorus and alternate melodies now grow from one motif instead of being written separately.
  - The chorus states the motif in full.
  - The alternate sections move it to their own chords, turn it upside down or sequence it a step higher.
  - The verse plays it lower and thinner, and climbs toward the chorus.
  - Arpeggio, riff and ostinato leads replay the main figure on the other sections' chords.
  - Arabic maqam genres keep their free, taqsim-like lines.
  - "Separate melodies" brings back the old way. From the command line: `--motif free`.
- **Mastering fixes:**
  - The master's saturation now runs oversampled, so bright, loud genres lose the harsh fold-back distortion.
  - **Width:** 1.0 now means "as mixed". The master used to widen every song by 15%.
  - Each genre's own width setting now works (it was being overwritten by the width slider).
  - **Mono-safe width:** a wide genre is pulled back only as far as needed to stay mono-compatible.
  - **True peak:** the last stray peaks over -1 dBTP are limited on their own. The whole song used to be turned down for them, which left it under its loudness target.
  - **Dynamic EQ** (300 Hz and 3.6 kHz): cuts low-mid build-up and harshness only in the full sections where they happen, and leaves the rest of the song alone.
  - Loudness (LUFS) is now measured with the exact standard filters; it read about 0.2 dB low before.
- **New exports:** **WAV 24-bit** (no dither) and **FLAC** (needs ffmpeg), in the export chips.
- **Mix check additions:**
  - loudness range (LRA) and the loudest 3-second moment;
  - how much quieter the song gets in mono;
  - how far the tone is from the genre's reference records, band by band;
  - how often the kick and bass hit the low end together;
  - what the dynamic EQ did.
- New fast test suite: `python -m tests.dsp_checks`.

## 1.75.0
- **Extra instruments** (Parts panel > **+ Add instrument**): add as many rows as the arrangement needs, beyond bass / chords / pad / arp / lead.
  - Each extra doubles the melody, chords, pad, arp or bass, or plays the counter-melody (added when the song doesn't have one).
  - Set its own instrument, octave (-1 to +2) and level.
  - "+ Add instrument" suggests the classic orchestration moves in turn:
    - celesta and glockenspiel an octave or two above the melody;
    - horns on the counter-melody;
    - a choir on the chords;
    - pizzicato on the bass;
    - flute.
  - Your extras are never swapped out by the genre.
- **New genre: Festive cinematic Christmas (full orchestra)** (Orchestral > Film & Trailer):
  - A warm, nostalgic carol-like theme, the melody doubled by celesta + glockenspiel, harp arpeggios, pizzicato doubling the bass.
  - Horns or cello on a counter-melody, a choir, sleigh bells and timpani.
  - Rich maj7 / add9 harmony with smooth, stepwise bass lines.
  - It starts with high, glittering textures and grows to the full orchestra.
  - **Film-score dynamics:** the opening plays very softly and each section grows louder, up to the full tutti (every part, not only the fader).
  - Mixed like a film score: quieter (-17 LUFS) with lots of headroom, with a tonal balance measured on film-score references.
- **New orchestral / festive sounds:**
  - Children's choir: pure and high, with almost no vibrato.
  - Piccolo.
  - Xylophone: hard mallets, comic runs.
  - Bass clarinet: dark and woody, the sneaky low-woodwind sound.
  - Triangle and wind chimes / bell tree, as drums.

## 1.74.0
- **Each song picks its own drum sounds**, using the same tick-box system as the instrument parts (Sound panel > **Drum voices**):
  - On drum-machine genres, every song can take its kick, snare, clap and hi-hats from a different machine that suits the genre.
    - For example, a 909 kick under a 707 clap and 606 hats in house.
    - Techno and trance draw on the 909 / techno / 707 / 606 machines.
    - Trap draws on the 808 machines; synthwave on the LinnDrum, DMX and 707.
  - The genre's own kit stays the most likely pick.
  - A genre whose kick is part of its identity (psy, hardstyle ...) keeps that kick.
  - The machine each voice used in your last song shows with a ★.
  - **Untick a voice** to keep that machine for every song, or pick any machine yourself. **Tick it** to let the genre choose again.
- **Runs like an app on your computer:**
  - Options > "Create app shortcut" now makes a shortcut on the desktop and in the Start menu, with the Studio Lab icon. It starts with no console window.
  - Right-click it > **Pin to taskbar**.
  - On Windows, Studio Lab installs a native app window (pywebview, using the Edge WebView2 built into Windows) in the background, so the pinned icon and the open window are one taskbar button.
  - Downloads work in that window too.
- **A more professional look:**
  - **Transport bar** along the bottom:
    - play / pause (space bar), the song's title and details;
    - a clickable waveform to jump around, the time, its loudness and a volume control (remembered).
  - **Mixer view** for the Parts panel (List | Mixer switch): every part as a channel strip with its sound, volume, octave, mute and FX chain side by side.
  - **One consistent line-icon set** instead of emoji on the buttons.
  - **Calmer colours:** one accent for the main action (Preview). Full song and the other buttons are neutral, with no glows.
  - **Help sentences moved into a small (i)** next to each control (hover to read). Options > "Show help text" brings them back.
  - **Tighter type scale:** odd in-between font sizes are evened out.

## 1.73.0
- **Effects on every part, picked by the genre or by you** (Parts panel, an **FX** line under each part):
  - **Genre picks:** the electronic, pop, lo-fi and retro families each choose effects that suit each part, and every song rolls its own:
    - house chords through a chorus or phaser;
    - a dotted-1/8 echo on a trance or techno lead;
    - a slow filter sweep on a techno arp;
    - OTT on a dubstep bass;
    - a phaser on DnB pads.
  - About half the parts stay dry, so the mix keeps some room.
  - The genre's picks for your last song show as dashed ★ chips.
  - **Your own chain:** "+ FX" adds as many effects as you want, ✕ removes one, and ↺ goes back to the genre's picks.
  - **16 effects:** chorus, phaser, flanger, tremolo (8ths / 16ths), auto-wah, bit-crusher (light / lo-fi), OTT, stereo widener, drive (warm / dirty), echo (1/8, dotted 1/8, 1/4) and a slow filter sweep.
- **Analog-modelled drum machines for house, techno and trance** (the 909, Techno 909 and Trance 909 kits):
  - **Kick:** the body holds for a moment before it decays, the pitch drops in two stages, it has a beater click, and its drive is smoothed so it's fat rather than fizzy.
  - **Snare:** shell tones that drop in pitch, plus a separate "snappy" noise.
  - **Clap:** 3-4 slightly uneven hand hits with a reverb-like tail.
  - **Hats:** six-oscillator metal with a softer top end.
  - The old sounds stay in the drum menu as "classic sound, before 1.72".
- **Round-robin drums:** hats, claps, snares, shakers, rides and rims cycle through three takes instead of repeating one frozen sample (the "machine-gun" effect).
- **Mastering keeps the song's dynamics:**
  - **Loudness target set by the loud parts:** the target is now measured on the drops and choruses, not the whole-song average. Before, long quiet intros pulled the average down and the drop was pushed into the limiter until it was barely louder than the breakdown.
  - **Clipper before the limiter:** a 2x oversampled clipper rounds off the kick and snare peaks with no attack or release. The limiter alone ducked the whole mix on every kick and squashed the drops.
  - **Gentler glue compressor:** it now only works on the loud parts.
  - **A trance song, section by section:** before, intro / drop / breakdown came out at -10.4 / -10.0 / -12.6 LUFS. Now they're -11.3 / -8.6 / -16.6, close to the mix's own arrangement.
- **Level visualizer:** it now spans the whole top bar, with more bands and finer detail.
- **Three new psytrance genres** (Techno & Trance), built from reference tracks and a psy production guide:
  - **Progressive psytrance (136):** deep and hypnotic.
    - A short, tuned kick on every beat, with the rolling bass playing three short notes between kicks (K-B-B-B).
    - Long 32-bar sections, filtered acid lines and dark pads.
    - A dark, smooth top end and a bone-dry mono low end, as measured on the references.
  - **Goa trance (140-148):** the classic 90s sound.
    - Squelchy detuned-saw leads in phrygian dominant / harmonic minor and interlocking acid arps.
    - Choirs in the breakdowns, brighter and busier than modern psy.
  - **Dark psy / forest (148-158):** a hard short kick, a growling rolling bass, laser zaps instead of melodies, flangers and crushed percussion.
  - **Full-on:** the existing Psytrance genre is now labelled "full-on" and can also use the new psy sounds.
- **New psy synths:**
  - **Psy rolling bass:** split the way producers build it - a clean sine sub under a filtered saw / square bite.
    - Oscillators restart on every note, so all three 16ths attack the same.
    - A fast plucky filter, almost no sustain, and a tiny cutoff change per note so the roll breathes.
    - "Growl" setting for dark psy.
  - **Goa lead:** squelchy detuned saws with a slow filter LFO.
  - **Psy zap:** laser blips.
- **Fixes in the Parts panel:**
  - The "Also playing in your last song" and extra-part rows were squeezed into a 16-pixel column, with titles wrapping letter by letter. They now have their own two-column layout.
  - The effect-plugin menu sits on the FX line instead of floating on its own row.

## 1.72.0
- **Breath sounds like breath, not white noise** (flute, ney, shakuhachi, tin whistle, breathy lead, sax, harmonica, older flute / sax):
  - **Before:** the air was plain filtered noise sitting beside the tone.
  - **Now:** the air is shaped like a real player's breath:
    - it resonates in the instrument's bore, so it carries the note's pitch;
    - it pulses with each vibration of the air jet or reed;
    - it wavers slowly with the breath, and its fizzy top end is softened.
- **Indian and Arabic slides land on the right notes:**
  - **Meend glides from the scale note below or above:** a bug sometimes started the glide on a note outside the raga, so it slid in from an off-key pitch.
  - **Ornaments aim at real quarter-tone notes in Bayati, Rast and Saba:** gamak shakes, glides and falls now target the maqam's actual notes, not the piano key next to them.
  - **The whole band plays the maqam's quarter tones:** chords, pads and bass now play the half-flat notes too. Before, only the melody did, so it clashed by a quarter tone with the chords (every Rast chord).
- **Mastering:**
  - **True-peak limiting:** the limiter reads the waveform between the samples (4x oversampled), and a final check keeps every master under -1 dBTP. No clipping after MP3 / AAC conversion, and loudness is unchanged.
  - **Kick / bass separation for genres without sidechain ducking:** the bass's lowest band (under 110 Hz) dips briefly under each kick, so the two don't blur into one boom.
  - **Mix check in the log after every render:**
    - loudness, true peak and peak-to-loudness ratio (how much punch is left);
    - stereo correlation, how mono the low end is, and how much the sections contrast;
    - plain warnings when something's off.
- **Mastering target buttons** under Loudness:
  - **Streaming** (-14 LUFS): the most dynamic. Streaming services turn louder songs down to this level anyway.
  - **Balanced** (-10 LUFS): loud but still punchy.
  - **Club** (-8 LUFS): dense and loud for DJ sets.
- **Mix check on every result:** a "mix ✓" or "mix: N notes" tag. Hover it to see the numbers and any warnings.
- **Fix:** silent renders (NaN) in some trance / future bass / psytrance songs, caused by a rounding error in the multiband "OTT" effect.

## 1.71.0
- **"genre picks" tick box on every part** (Parts panel, next to each sound):
  - **Ticked:** the genre chooses that part's sound for each song from its suggestions.
  - **Unticked:** the part keeps the sound shown, starting from the genre's own sound or the one you just heard.
  - Picking a sound from the menu unticks it, and ticking it again hands the choice back to the genre. You can always see which parts are yours and which are the genre's.
- **Parts panel tidied:** the "genre picks" box is now a small tick at the start of each row, under one column heading instead of the words on every line. The sound menu is wider, and the genre's own sound now shows as "★ name" instead of "Style default (name)", so the names fit.
- **New synths:**
  - **Mono synth (SH-101 style):** saw, a moving pulse and a square sub an octave down, a breath of noise, a snappy key-tracked filter and glide. The round, rubbery bass and bleep sound of techno, minimal, acid, electro and Berlin school, gentler than the 303.
  - **Sharp digital pluck:** two saws with an FM edge on the attack and a bright filter snapping shut very fast, for crisp, bouncy trance arps.
  - **Rave stab:** a detuned saw-and-square stack with a downward pitch "whoop", a resonant band-limited filter and a hard, short envelope, for 90s hardcore, rave, eurodance and hard trance.
- **New production effects for any part:**
  - **OTT-style multiband squash:** quiet detail pulled up and peaks held down in three bands, for dense, forward EDM synths.
  - **Mid/side widening:** above 200 Hz, with a little Haas delay, the low end kept mono.
  - **A part's own echo time:** for example a 1/8 echo on the pluck under the genre's dotted-8th lead delay.
  - The trance genres now use them: wide pads, squashed leads, and plucks with their own 1/8 echo. So do future bass and melodic dubstep chords, deep-house and progressive-house pads, anthemic-DnB chords and big-room leads.
- **Phonk, closer to the real palette** (drift phonk, house phonk, Brazilian phonk, Memphis phonk):
  - **Cowbell:** the 808 cowbell lead is now overdriven until it cuts like a synth, bit-crushed and gated short, the way phonk producers process it.
  - **808:** split into a clean sine sub under the driven growl, so the low end stays solid and round on big speakers while the distortion lives in the mids where small speakers hear it. It still glides between notes.
  - **Drums:** the whole kit is lightly bit-crushed and saturated harder as a group.
  - The lo-fi tape texture on the mix, the Phrygian riffs and the trap hat rolls stay as they were.

## 1.70.0
- **Techno rumble, done the real way:** in techno, hard, dub, melodic, tribal techno and minimal, the kick itself is sent into a long, dark reverb. The result is low-passed to the sub region, driven so it growls, high-passed under 35 Hz and ducked by the kick: the rolling low-end roar between the kicks. Because it's built from the kick, it always sits in the kick's key and rhythm. It comes out as its own stem ("kick_rumble").
- **Modular-style sequencing** (techno family, acid house, tech house, Berlin school):
  - Off-beat hats only play some of the time, with each song getting its own odds.
  - Hits now and then roll into 2-4 quick ratchets.
  - One percussion part loops every 3, 5 or 7 sixteenths, drifting against the bar.
  - A few steps of each loop are always accented or ghosted (parameter locks).
  - Kicks, claps and snares stay put.
- **Deep-house chord voicings:**
  - New minor-11th chords (1 - b3 - b7 - 9 - 11) and the quartal "Detroit" stab built in stacked fourths.
  - Each house / techno song now picks its own keyboard voicing (drop-2 9ths and 11ths, quartal stabs, open or close triads) and its own colour (7ths, 9ths, minor 11ths).
- **House groove per sound:** in the house genres the closed hats and shakers swing harder than the kick, the shaker is pushed ahead, the rims and congas sit a little back and the clap is a hair late. It feels played rather than quantized.
- **Open-hat choke:** in the electronic genres with drum-machine hats, the closed hat cuts the open hat off the moment it's struck, as on a real drum machine.
- **Fix - "Sounds & instruments" not opening:** the Genre VSTs page's server call failed (a naming clash in the server code, there since 1.54). The hub reopens on the last page you used, so once that page was Genre VSTs the whole window silently never appeared. Now:
  - The server call is fixed.
  - The window always opens straight away, showing "loading…".
  - If a page can't load, it falls back to the overview instead of never showing.
- **Automatic tone matching to the reference records:** genres modelled on your reference tracks now carry the records' tonal balance. That covers emotive / melodic / organic / sunny deep house, the trance genres, club trance, festival psy, the progressive trance genres, and anthemic and liquid DnB. The master compares each render with it and nudges every band part of the way there (at most +-3 dB), which fixes a too-dark or too-thin render without forcing it onto the records.

## 1.69.0
- **More dubstep / bass-music basses,** built from your notes on growls:
  - **Dark smooth wobble:** rounded saw and triangle through a low, gently resonant filter swept only from very dark to warm, over a heavy sub. For deep and dark dubstep.
  - **Sub wobble:** a pure sine sub that swells on the LFO, for deep pressure.
  - **FM growl:**
    - A pure sine carrier frequency-modulated by a sine and a square an octave and a twelfth up.
    - One synced LFO drives the FM amount, a pitch bend and a moving formant band, so the sidebands "talk".
    - Four detuned voices go through multi-band distortion, an all-pass smear, an OTT-style squash and more saturation, with a clean sub split underneath. It glides between notes.
  - **Talking growl:** a vowel filter walked "wa - oo - ee - ow" by a stepped LFO (the drawn-LFO growl), with the pitch bending along and hard clipping after the formants.
  - **Metallic neuro bass:** an FM tone through a resonant comb tuned to the note, its feedback moving with the LFO, hard-clipped and squashed.
  - **Fuzzy filter bass:** one analog saw into a screaming low-pass, its cutoff pushed by the envelope and wobbled by hand, with overdriven resonance and glide. This is the rubbery late-90s French / electro bass.
  - Deep, early, chill and melodic dubstep get the dark and sub wobbles; dubstep, brostep, riddim and midtempo get the growls; neurofunk, DnB and jump-up get the metallic bass; electro, French house, bass house, big beat, electro-funk, nu-disco and outsider house get the fuzzy bass. Wobbles in drum & bass now move at DnB speeds.
- **Trance:** a new **progressive pluck-lead** (round, mid-focused, resonant, made for long dotted delays) and a **trance-gated supersaw pad** (a wide supersaw chopped into 16ths by a built-in, tempo-synced gate).
- **Switch-up / phonk / Memphis voices:**
  - **Orchestra hit:** brass, strings and a timpani thump in one crunchy 80s sampler stab.
  - **Horror piano:** detuned against itself, with tape wow, crushed to 10 bits.
  - **Eerie pad:** players drifting slowly out of tune, a dark filter and hiss.
  - **Music box:** a glassy steel-comb ping with its mechanical tick.
  - **Crushed lead:** a 6-bit saw with portamento.
  - Added to the switch-up, phonk, Memphis and bass-warp genres; the music box also goes to the lullaby, dark hauntology and witch-house genres.
- **New genre - Progressive trance, early 2010s (instrumental),** from your breakdown:
  - **Drums:** a rounded 129 bpm kick, a crisp layered clap, off-beat hats with 16ths in the energetic parts, shakers and rides.
  - **Bass:** three layers (sine sub on the roots, a round short mid-bass, the rolling off-beat notes) pumping against the kick.
  - **Synths:** warm wide pads, a bright digital pluck in delayed arps, a smooth layered supersaw lead with a simple rising-and-falling hook, and high bell counter-lines.
  - **Harmony:** minor chords that move slowly, two bars each, in open voicings.
  - **Arrangement:** an extended arc where every section adds a layer, then a long, exposed breakdown and a full melodic drop.
  - It stays strictly instrumental (no vocal or choir sounds) and never reaches for aggressive festival or techno sounds.
- **New genre - Progressive trance, electro-edged (late 2000s),** from your notes:
  - 130 bpm in i - iv - VI - VII minor harmony.
  - A strong driving bassline and a short piano theme in the breaks, with evolving filtered and trance-gated pads and layered leads.
  - A push-pull arrangement where the melodic break keeps interrupting the groove, then heavy low-pass builds bring it back with a tighter, mid-heavy electro edge.
- **Anthemic drum & bass, after your four new tracks:**
  - The mid-bass now moves: an 8th-note filter LFO inside a slow one-bar sweep. In the tracks that movement sits at 2 per beat and once per bar.
  - The chords follow their progressions: vi - IV and vi - I - IV in major, i - VI, i - v and i - III - VII in minor, mostly two bars per chord.
- **Fix - bass clipping:** in bass-heavy genres (screwed, 808 genres) a loud sub could drive the final limiter, whose fast gain changes rode the bass waveform itself and distorted the low notes. The master now has a bass-safe pre-limiter on the band below 120 Hz, whose gain is held over a whole bass cycle and released slowly. The final limiter holds its gain over half a bass cycle, and the loudness target never pushes the bass band past about 80% of the ceiling, so a bass-heavy song comes out a little quieter instead of clipped.
- **Fix - the genre list no longer jumps when you click a genre:** the row you clicked stays exactly where it was on screen while the list and the description above it update.

## 1.68.0
- **Every electronic genre has a much wider list of suggested sounds.** Many offered only 1-4 per part (drum & bass, trap, house, techno...), so the Sound panel's "Suggested for this genre" list was short and songs kept picking the same few sounds. Each scene now has its own idiomatic set, added after the genre's own sounds, so the signature sound stays first and most likely. Every part now has up to 8.
  - **House:** the deep, Juno, organ, rubbery-tech and bass-house basses; the 90s house piano, Rhodes, sampled stabs, Juno chords, house organ, anthem keys and woody plucks; lush, Juno and vocal pads; vocal chops and breathy leads.
  - **Techno / trance:** tech-trance riff and dub stabs, hypersaw, dark pad and atmosphere, techno sequence, psy and emotional leads, the rolling psy bass.
  - **Drum & bass:** reese, neuro, DnB wobble and bouncing bass; anthem keys, Rhodes and sampled stabs; lush, vocal and trance pads; bleeps, vocal chops and the emotional, breathy and sync leads.
  - **Dubstep / garage / bass:** all the wobbles, growl, reese and mid-bass; future-bass chords; vocal chops.
  - **Trap / phonk, pop, chill and retro scenes** get their own sets too.
  - The part a genre's authenticity rules check (trap's 808, dubstep's mid-bass, trance's lead) keeps exactly its own list. A bass line written for a sub, an 808, a walking line or a 303 is never handed a sound it wasn't written for.
- **House synths upgraded:**
  - **90s house piano** rebuilt on the new acoustic piano, with a glassy FM tine on the attack, hollowed low mids, a pushed top and a little chorus.
  - New **sampled chord stab:** detuned saws and an organ-ish pulse snapped shut, crunched to 12 bits like the old samplers.
  - New **rubbery tech-house bass,** whose pitch snaps down into each note. It is now tech house's own bass.
  - New **bass-house bass:** a growling "yoy" that snaps on every note, over a clean sub. It is now bass house's own bass.
- **New genre - Festival psy-trance (big-room / psy hybrid),** based on your reference tracks:
  - A hard, tight kick at 134-138 with the rolling psy bass playing three short notes between every kick (K-B-B-B).
  - Squelchy FM psy leads and acid lines over it.
  - Big supersaw chords and a wide pad in the breakdown, with an emotional lead.
  - A long snare-and-riser build into the main riff drop, with very wide mids and a tight mono low end.
- **Interface:**
  - **New default font:** a modern UI font (Inter / Segoe UI Variable / SF Pro, whichever your computer has). ⚙ Options → Appearance now has a **Font** menu: Modern, Rounded, Geometric, Humanist, System default or Monospace.
  - **Compact genre list:** the list is now tight table rows with an alternating background tinted from your accent colour. Long names are trimmed to one line, with the full name in the tooltip. Options → Appearance → **Genre list → Roomy** brings back the old spacing.
- **New psy synths:** a **psy rolling bass** (tight saw with a snappy filter and a pitch click) and a **psy lead** (an FM tone whose index is swept by an envelope and a fast LFO, with a vowel formant on top, driven and wide).

## 1.67.0
The next batch of widely used first-generation sounds is rebuilt. Old ones are kept as "(classic sound, before 1.67)".
- **Choir:** six singers, each a breathy glottal pulse with their own pitch, vibrato and timing, through the five formants of the vowel ("aah" by default, or "ooh" and the others). The formants sit lower for low voices and higher for high ones, with a slow swell and a wide stage.
- **Brass section:** three players whose buzzing-lip tone opens with the breath. They are a little out of time and tune with each other, with a scoop into each note and a punchy attack. This is the horn section of soul, funk, ska, salsa and big band; synth brass is still "Synth brass".
- **Mallets by modal synthesis:**
  - **Marimba:** bars tuned 1 : 4 : 10, a yarn mallet, and the resonator tube's bloom.
  - **Celesta:** felt on steel plates, pure and sweet.
  - **Kalimba:** a steel tine, its quick high overtone, the box buzz and the thumb click.
  - **Glockenspiel (new):** bright steel bars with their inharmonic shimmer. It was added to the Christmas, musical-theatre, lullaby, adventure, fantasy, indie and anime genres.
- **Harp, pizzicato strings and clavinet** are now modelled strings:
  - **Harp:** a round fingertip pluck with a long free ring.
  - **Pizzicato:** four players plucking a hair apart, through the violin-family body.
  - **Clavinet:** a bright, nasal struck string with two pickups, choked by the yarn damper.
- **Palm-muted guitar** and **twang (Telecaster)** now use the modelled electric guitar string and amp.
- **French horns, trombones and tuba** now use the new brass-section model: the horns mellow and slower, the trombones broader, the tuba darkest with a round low bloom.
- **Tubular bells** are rebuilt by modal synthesis (the tube's strong upper partials and a long, beating ring), and there is a new **church bell** (hum tone, strike tone and the minor-third partial that makes a bell sound like a bell).

## 1.66.0
I went through every genre and counted which instruments they lean on and which built-in sounds stand in for them. The most-used acoustic stand-ins were still simple first-generation sounds, so they are rebuilt. Each old sound is kept as "(classic sound, before 1.66)".
- **String section** (used by ~210 genres): seven players a few cents apart, each with their own vibrato and slow drift, spread across the stage. The bow brightens as it bites in, with a whisper of bow noise, through the body resonances (warm 280 Hz, the 2.8 kHz singing formant, the nasal dip between).
- **Acoustic piano** (~150 genres): stretched, inharmonic partials whose brightness follows the register. Each partial has the two-stage piano decay, the lower notes have the slow beating of their unison strings, plus a hammer knock, soundboard bloom and dampers. The level is even across the keyboard and notes spread low-left to high-right.
- **Electric guitars** (~95 genres): picked waveguide strings on a magnetic pickup, muted by the hand at the end of each note, with palm mutes, every string at the same level, into three amps:
  - **Clean:** tube compression and the scooped American-amp tone.
  - **Crunch:** a cranked tube amp that cleans up as the note decays, with a mid hump and a 4x12 cabinet.
  - **High gain:** a tight boost into two clipping stages, scooped metal mids and a steep cabinet roll-off. Palm mutes become the chug.
  - Genres that asked the old guitar for "dist" now get the crunch or high-gain amp. When the sampled clean, overdriven and distorted guitars aren't installed, these models stand in for them.
- **Saxophone** (~65 genres, tenor and soprano): every harmonic present, getting brighter the harder it's blown. It has the horn's formants, breath riding the tone, a scoop into each note, a delayed vibrato and an optional growl.
- **Flute** (~110 genres): a near-sine air-jet tone that gains harmonics up high, breath tuned around the note, the attack "chiff", a soft start slightly flat, and a vibrato that moves pitch and loudness together.
- **New effect pedals for any part:** phaser, flanger, beat-synced tremolo, auto-wah and bit-crusher. Some genres now use them:
  - Wah on funk's clavinet and on the disco-funk, chicha and Thai-funk guitars.
  - Phaser on disco strings and on psych and krautrock keys.
  - Surf tremolo on the surf guitars.
  - Flanger on shoegaze guitars.

## 1.65.0
- **Rhodes electric piano:** a model of the tine-and-pickup piano. The pickup "barks" harder the louder the note (bright attack, mellow sustain), with a short tine ping and hammer thump, a fast-then-slow decay, felt dampers and the suitcase's stereo tremolo. It is now the main keys sound of neo-soul, R&B, lo-fi and deep house, and an option in jazz, gospel, soul, city pop, smooth jazz and Tokyo deep house. The DX-style FM piano is still there as "Electric piano".
- **Modelled acoustic guitars:**
  - **Steel-string:** pick-flicked waveguide strings that ring on, through the air and top-plate resonances of the body, with palm mutes. It replaces the old synth acoustic guitar, which is kept as "(classic sound, before 1.65)".
  - **Nylon-string:** a soft, round finger pluck with a warmer, shorter ring. Bossa nova, flamenco rumba, tango, son, folk, cumbia, bachata, samba and lo-fi can use it.
  - When the sampled guitars aren't installed, the "sampled" nylon and steel guitars now fall back to these models.
- **Hard-dance lead:** a supersaw with an octave layer driven hard into a clipper, with its bite pushed and a late, fast vibrato, for hardstyle, gabber, UK hardcore, rave hardcore and hard trance.
- Test runs now delete their temporary renders when they finish. They had been leaving gigabytes of WAVs in the temp folder.

## 1.64.0
- **New synths:**
  - **Vocal chops:** short sung syllables through vowel formants, the vowel moving with the note (ah, oh, eh, oo, ee), each one levelled, with a scoop in and a clean cut out. These are the pitched vocal-chop hooks of house, future bass, tropical house, garage and DnB.
  - **Future-bass chord:** a bright supersaw with a vocal-ish formant, swelling up after each hit (the sidechain bloom) with a little scoop, and wobbling when held.
  - **Lo-fi keys:** a soft electric piano on worn tape, with slow wow and flutter, a dark top, gentle saturation and a little hiss.
  - Added to the house, garage, future bass, melodic dubstep, DnB, lo-fi, jazz-rap and beat-tape genres.
- **Mix balance checked against the reference tracks** (frequency balance and stereo width of the busiest section):
  - The club trance remix was much darker on top than the record, so it now has more air and louder hats.
  - Emotive deep house's top end was too dark, so it gets more air and a louder shaker.
  - Anthemic DnB was too bright and fizzy on top, so it has less air and quieter hats and bleeps.

## 1.63.0
- **New genre - Emotive deep house (extended mix):** built from the reference tracks' measurements. 121-124 bpm with a deep, round kick and a long low tail. The bass rolls on the off-beat 16ths and pumps hard against the kick. Shakers, an airy off-beat hat and soft claps keep the groove. Woody plucks bounce through dotted-eighth delays over a lush pad that breathes with the sidechain, with soft piano or guitar chords and a breathy, vocal-like lead. The top end is dark and warm and the mids wide. The arrangement runs DJ intro → the groove stacking up → a first main section → a long emotional breakdown → build → full return → DJ exit.
- **New genre - Club trance remix (2000s):** a tight 909 kick at 138 with a galloping off-beat rolling bass, driving 16th hats and a punchy, syncopated tech-trance synth riff through a dotted delay. Gated supersaw chords and a wide pad fill it out. The long club arrangement has a big breakdown where the pad, a breathy lead and the chords slowly filter open, then a snare-roll build and long full sections.
- **New house synths:**
  - **Deep rolling bass:** a clean sine sub under two soft saws, a low filter with a small "bow" on each note, warm saturation.
  - **Melodic-house pluck:** warm and woody, with the filter falling from warm to dark, plus a gentle chorus. It isn't the glassy trance pluck.
  - **Lush pad:** a soft supersaw and string ensemble swelling together, with a filter that opens as the chord is held.
  - **Breathy lead:** a flute-like triangle / sine tone with breath, a scoop and a late vibrato.
  - Melodic, sunny, organic, deep, progressive, afro and Tokyo deep house can pick them.
- **New tech-trance riff synth** (two saws + a square an octave down, a resonant filter that snaps shut, driven).
- **New genre - Drum & bass, anthemic:** a crisp, punchy 174 two-step with ghost snares and a 16th shaker. A round, bouncing mid-bass kicks its filter open on every note over a clean sub. Big bright chords come from a piano doubled by a wide supersaw, with lush strings, a singing vocal-like lead and bleepy arps. The arrangement runs keys-and-vocal intro → two 64-bar drops that switch up halfway → a long breakdown where the chords filter down and open again.
- **New synths for it:** **Bouncing DnB mid-bass** (saw + square through a filter that kicks open and settles, over a mono sub) and **Anthem keys** (piano doubled by a soft, wide supersaw that swells in under it).
- **Every song gets its own arpeggio.** House, techno and trance songs kept playing the same arpeggio into the drop: one note order per genre (up / up-down), one speed, and the same pluck. Now each song picks its own figure:
  - **Note order:** up, down, up-down, outside-in, a pedal note under or over each chord tone, octaves, a small fixed motif (3- and 5-note ones drift across the beat) or random.
  - **Range, speed and gate:** one or two octaves, a step faster or slower, and on 16ths often a gate rhythm with rests.
  - The genre's own figure stays the most likely. Written figures (montuno, Alberti, banjo rolls, mallets, tapping, beat-locked arps) are untouched.
- **Supporting parts vary more.** Genres whose sound is strongly defined (trance, techno, house, rap, R&B, country...) used to keep every part's sound almost every time. Now only the defining part holds (trance's lead, techno's bass, house's bass and chords...). The arps, pads and other supporting parts are picked from the genre's own pool like everywhere else.
- **Builds aren't always "the arp, rising":** about half of them now ride the chords and pad, sometimes with a teaser of the lead, and leave the arp out.
- **Filter automation across the arrangement** (trance genres, progressive house, techno, melodic techno, and the two new genres). The synths' low-pass is part-closed in the intro and groove, darker in the breakdown and slowly opening, swept open in the build and wide open in the drop.
- **Sidechain that follows the energy** in the same genres: deepest in the drops, gentle in the breakdown, growing through the build.
- **Instrument check:**
  - Every genre's sounds were rendered across their part's range: no errors, silent or clipping sounds, or wrong octaves.
  - Fix: the screech sound played everything an octave up, so as a lead (footwork, hard techno, midtempo bass) it sounded an octave too high. It now only jumps up from the bass register.
  - Dub techno's chords now use the dub-techno chord stab.
  - Every sound a genre plays in a part is now offered for that part in the Sound panel's menus. Guitar leads, organ arps, brass pads, timpani bass lines and more used to be missing from them.

## 1.62.0
- **Daisy easter egg: a steadier voice.** The first words still seemed to swell and dip: low notes came out boomy and high ones thin, and the "ei" of "Dai-" brightened and darkened as it moved. The voice now goes through a three-band dynamic EQ (each band ridden towards its usual level, at most 5 dB either way) before the vocal rider, and the rider measures loudness the way loudness meters do (K-weighting) instead of A-weighting, which used to push low notes up until they boomed.
- **Different wobbles for dubstep and drum & bass:**
  - **DnB wobble:** a reese-like pair of detuned saws through a tighter filter on a fast LFO (16ths by default), cleaner drive and more mids - rolling under fast breaks. Jump-up now uses it, and DnB / neurofunk can pick it.
  - **Vocal wobble:** formant filters slide o - a - i with the LFO so the bass talks ("yoy"), clipped hard after the filter.
  - **Multiband wobble:** the low-mids and the top band move on separate LFOs, each driven on its own.
  - **Wavetable wobble:** the oscillator morphs sine - triangle - saw - square while the filter wobbles.
  - **Chop wobble:** a falling saw LFO slams the filter on every step, volume-gated and bit-crushed - the stuttering riddim wub.
  - All of them keep a clean mono sine sub under the moving mids. Dubstep, brostep, riddim, chillstep, midtempo and 140 genres can pick them.
- **Techno voices:** a **rumble** bass (the driven, low-passed roar between the kicks), a **dub-techno chord stab**, a **techno sequence** synth whose filter changes a little on every step so a repeating line evolves, a **dark evolving pad** and an **atmosphere** texture (tuned noise that breathes). Added to techno, melodic, hard, dub and tribal techno; the atmosphere also to the trance genres.
- **Trance:**
  - New **emotional lead**: a softer supersaw with a round triangle, a small scoop into each note, a vibrato that deepens and a filter that blooms over long notes.
  - The halls now have pre-delay and a high-passed return, so the low end stays tight.
  - The arrangement follows the classic arc: DJ intro with the pad filtering in, groove with plucks and arps, a first main section with the lead, the long emotional breakdown, the build, then the full drop and a DJ outro.

## 1.61.0
- **Leads sit an octave lower in many genres.** The melody register used to centre around E5-E6, which put a lot of synth and vocal-style leads an octave above where they'd normally be played. It now centres around G4-G5, still above the chords. Genres with their own lead register (riff leads, phonk cowbells, the G-funk whistle) keep theirs, though the whistle comes down a little.
- The supersaw lead's octave-up "air" layer is quieter and higher, so it adds sparkle without making the lead sound an octave up.
- **Real-sounding basses.** The bass guitars are now physical models: a waveguide string (computed a period at a time, exactly in tune), set moving the way a bassist does it, read by a pickup, muted by the fretting hand at the end of each note, then the DI / amp tone and gentle compression.
  - **Electric bass** (the most-used bass, ~50 genres): a finger pluck, a bridge-pickup midrange, a round low end and a little 800 Hz growl. Notes now sustain like a real bass and stop cleanly.
  - New **Picked bass** (rock, punk, post-punk, garage, metal, surf), **Slap bass** (low notes thumbed with fret clank, high notes popped, scooped funk tone - funk, disco, fusion, new jack swing) and **Fretless bass** (soft attack, singing sustain, the "mwah", slides between notes - fusion, smooth jazz, city pop, soft rock).
  - **Upright bass** rebuilt: a heavy plucked gut string with a woody thump and the body resonances of the instrument.
  - When the sampled bass sounds aren't installed, the "sampled" finger / pick / slap basses now fall back to these models instead of a generic sound.
- **Sine bass** is phase-continuous and can slide, with a touch of asymmetric saturation so it's heard on small speakers; **Saw bass** moved to the analog voice (saw + square sub, resonant 24 dB filter, glide). The old sounds are kept as "(classic sound, before 1.61)".

## 1.60.0
- **Classic-hardware voices** for the instruments that cover the most genres:
  - **Acid bass (303) rebuilt:** one saw (or the lopsided square) into an 18 dB/oct resonant low-pass that squelches but stops short of self-oscillating. Accented notes get a louder VCA, a short fixed filter decay and the accent circuit's extra cutoff "wow" that grows with resonance; slid notes glide over ~60 ms with no new attack, and the filter envelope carries on through the slide instead of re-triggering. The old sound is kept as "Acid bass (classic sound, before 1.60)".
  - **Juno pad, Juno poly chords and Juno bass:** a single rock-steady DCO (saw + modulated pulse + square sub) with the high-pass, a gentle 24 dB filter and the stereo bucket-brigade chorus (modes I, II and I+II, left and right swept in opposite directions, darker wet path). Used in house, deep house, nu-disco, Italo, eurodance, city pop, vaporwave and more.
  - **Jupiter pad:** two drifting saw oscillators per voice, slow filter swell, lighter chorus - the lush 80s pad (synthwave, synth-pop, city pop).
  - **OB brass stab:** two bright saws per voice through an open filter with a fast swell - the big 80s rock / synth-pop chord stab.
  - **Mono analog lead:** three oscillators overdriving the mixer into the resonant ladder filter, glide and a late vibrato (funk, G-funk, electro, synthwave).
  - **Hypersaw:** two supersaw stacks (fourteen saws) plus a sub, high-passed and wide, for 2000s trance / progressive / electro chords and leads.
  - **FM solid bass:** a 1:1 FM bass whose brightness snaps from bark to round, with a little feedback edge (synth-pop, freestyle, electro-funk, city pop).
- Drum machines: the 808, 909, 707 and LinnDrum kits were already modelled voice by voice (pitch-swept sine kicks, tone + noise snares, metallic hats) and stay as they are.

## 1.59.0
- **Trance synths, built the way the genre builds them:**
  - **Supersaw** is now a JP-8000-style supersaw: seven saws at the original's relative offsets, its non-linear detune curve and its centre-vs-sides mix, spread across the stereo field.
  - **Supersaw lead** is layered like producers stack it: a supersaw body, a second wider supersaw for the mids, an octave-up layer high-passed for the "air", and a whisper of high-passed noise for sparkle - with glide, delayed vibrato and a filter that opens on every note (long hall and stereo delay from the track).
  - New **Trance pad** (slow-attack supersaw bed with a breathing filter, built for sidechain and the trance gate), **Rolling trance bass** (saw + square an octave apart, short pluck envelope, snappy filter - the offbeat 16ths between the kicks) and **Supersaw pluck** (the JP stack with the filter snapping shut, for arps). Trance, uplifting and progressive trance now use the rolling bass and trance pad; 90s trance-pop the rolling bass.
- **Dubstep / drum & bass synths rebuilt** - every distortion now runs at 4x the sample rate (no aliasing fizz), with real resonant filters and band-passes moving in tempo, and a clean sine sub split off under each mid-bass:
  - **Wobble** (unison saws + square through a resonant low-pass swept on an exponential curve, a vowel band-pass following it), **Growl** (FM pair, two moving vowel formants, wavefolder), **Reese** (four breathing saws, resonant filter, drive and a moving notch - the DnB "movement"), **Riddim**, **Screech** and **Hoover** (7-voice PWM saws scooping into the note).
  - New **Neuro bass** - a torn-up reese with sweeping comb-like band-passes, a wavefolder and a hard clip (neurofunk, DnB, jump-up).
- **House**: new **House organ stab** (the M1-style organ of 90s house) - house now plays it on the arp and bass house on the chords.
- Every sound replaced keeps its previous version, marked "(classic sound, before 1.59)".


## 1.58.0
- **More of the built-in synth:**
  - **Organ** is now a proper tonewheel organ: nine drawbars set by a registration, key click, the decaying percussion on the 2nd harmonic, a little tube drive and a two-rotor rotary speaker (fast horn, slower drum, each with its Doppler wobble). Parts that use their own rotary effect still get it.
  - **Synth brass** (80s / synthwave): detuned saws and a sub through a filter that swells open on each note and settles.
- **New sounds** (pick them in Parts; they're also mixed into the matching genres' sound choices):
  - **Sync lead** - the tearing, vocal 80s hard-sync lead (synthwave, synthpop, italo, analog arp drive).
  - **Mellotron strings** and **Mellotron flute** - the tape keyboard: a soft swell, wow and flutter, a dusty band, notes that run out after ~8 seconds (hauntology, psych pop, lo-fi rock, cinematic beat tape).
  - **DX bell** - the glassy FM bell of 80s ballads, city pop and sophisti-pop.
  - **Synth choir "aah" pad** - the wordless vocal pad of chillwave, downtempo and 80s pop.
  - The previous organ and synth brass stay available as "(classic sound, before 1.58)".


## 1.57.1
- **New genre: Trap metal (clipped 808s, drop-tuned guitars)**, from your reference instrumental: short, violent and loud - blown-out, clipping 808s and kicks, a half-time snare cracking on 3, hats and rolls, double-tracked drop-tuned guitar chugs and power chords locked to the 808 in a sinister phrygian-dominant key, an eerie lead on the hook, mixed as loud as it gets (~-6 LUFS), mono and slammed. Voice samples get chopped & screwed in it too.


## 1.57.0
- **A built-in analog synth.** The classic synth sounds are rebuilt on one proper virtual-analog voice: band-limited oscillators (saw, pulse with pulse-width modulation, a sub-octave, noise), up to 7 unison voices spread across the stereo field with free-running phases and a slow analog drift, a **resonant 24 dB low-pass filter that moves through each note** with its own envelope and key tracking, a soft drive stage in front of it, and analog-style envelopes. No install - every genre using these sounds gets the upgrade at once:
  - **Warm pad** (Juno-style: saw + moving pulse + sub, the filter opening as it swells), **Poly synth** (Prophet-style filter "bwow"), **Supersaw** (7 voices, wide), **Saw lead** (glide, delayed vibrato, a filter bite), **Soft lead** (hollow square), **Pluck** and **Stab** (the filter snapping shut), **Saw bass**, **Moog bass** and **plucked Moog bass** (fat, resonant, settling filter).
  - **Electric piano** is now a DX7-style FM e-piano: a warm body plus the bright "tine" bark on the attack, harder notes bark more, with tremolo.
  - The previous sounds are still there to pick, marked "(classic sound, before 1.57)".
- **More synths you can add**: Vital, TyrellN6 (a free Juno-style synth, great for the chillwave genres) and the sfizz sampler (for free SFZ instrument libraries) are now listed under Plugins with their download pages. They need an account or their own installer, so the app can't fetch them by itself.


## 1.56.7
- **Three new sunlit chillwave genres**, from your eleven references of one artist's work - each family of its records:
  - **Sunlit chillwave (live drums, chorus guitar, analog synths)**: a long ambient intro of tape hiss, warm pads and a chorus-drenched guitar picking in the delay, then a real drummer driving a straight indie beat, a picked bass guitar, a bright analog arp and a simple synth melody; slow, open major-key chords (IV-V-I, I-V-vi-IV), pads breathing with the kick, a breakdown with the drums out, a slow fade.
  - **Hazy downtempo (pumping pads, dusty break, wide)**: 75-90 BPM, a soft break with busy quiet hats, deep analog pads swelling with the kick, a round synth bass, wordless vocal pads and a very wide, dreamy stereo field.
  - **Analog arp drive (pulsing sequence, pumping pads)**: a 16th-note analog sequence whose filter opens over the builds, pumping against a steady kick, swelling pads, bass guitar and a soaring synth lead.
  - All three: tape-warm (almost nothing above 8 kHz), chorus on the guitars and pads, sus / add9 colour, one sound per part kept for the whole song.
- **Velvet pop (soft, warm, dark)**, from your soft-pop instrumental: a muffled, close drum machine, a deep warm bass carrying the song, mellow organ / Rhodes chords and soft pads, nothing sharp on top.
- **Emotive 2-step house** (swung 2-step, deep sub, chopped vocal hooks, warm keys) and **Sub pressure 140** (dark, minimal 140 that is almost all sub), from your last three references.
- Removed artist names from the notes (genres are named for how they sound).

## 1.56.6
- **New genre: Math rock** (Classic → Rock & Metal), from your reference album: a clean guitar tapping a looping two-hand figure of 5, 6, 7 or 8 notes that drifts against the bar line, a second clean guitar on the melody (panned the other way), a melodic fingered bass, a busy, precise drummer (ghost notes, ride, fills, accents hit together with the guitars), bright major / lydian keys with added 9ths - and **real odd time signatures**: bars of 7/8, 3/4 and 5/8 between the 4/4 ones (riffs that cycle 4/4-4/4-4/4-7/8, all-7/8 riffs, 3/4 + 7/8 ...). The odd bars are shorter, not squashed: every note keeps its length, and the MIDI export carries the tempo changes so it lines up in a DAW.
- **Five more genres from your reference batch**: **Rolling atmospheric bass** (wonky swung beat, a deep rolling bassline, hazy wide pads, glitchy vocal chops), **Cinematic beat tape** (instrumental hip hop layered like a film score), **UK tribal techno-bass** (broken skipping kicks, tribal toms and congas, a huge rolling sub), **Steppy halftime / acid step** (140 half-time with a stepping kick, deep sub, often an acid line) and **Balearic chill** (sunset nylon guitar over a soft slow house groove).
- Your other references are already covered by existing genres: Jump-up / Dancefloor liquid DnB, UK bass 130, Electro, DnB / Neurofunk, Melodic house and Trap / Glitch future bass.


## 1.56.5
- **New genre: IDM jungle - moody theme**, from your reference: half a minute of warm, detuned pads and a melancholy synth theme alone, then frantic chopped jungle breaks crash in with no bass, then a nimble, melodic bass guitar; dark minor chords, a breakdown back to the synths, and a key change up for the last stretch (~160 BPM).
- **New genre: Drill & bass - spacey**, from your other reference: hyper-detailed breaks at 172-190 under bright, spacious jazz-fusion chords (Rhodes, vibes), a soft lead drifting in long delays, a very wide, airy mix and a busy bass guitar; it opens on the synths and drops the drums for a floating breakdown.
- Both follow your notes on the style: **the break is resequenced hit by hit, so no two drum bars are the same** - flams, micro-stutters (32nd / 48th bursts), reversed and re-pitched single hits, kicks and snares swapping places, ghost hits filling every gap, hat ratchets, and edits in the middle of phrases too - while the **melody stays calm**: simple, long notes that sit and breathe over the chaos.
- **The growl bass is gone from the switch-up / bass-warp genres.** The high bass notes are now played by a new **Mid-bass** sound: a round, saturated, warm tone (the way a distorted 808 sounds up high), low-passed so it's thick, not thin, squeaky or snarling. The 808's own "growl" move (the long growl section in Bass-warp fast) is rebuilt too: a warm, saturated 808 with a slow low-pass "wah" instead of harsh square grit.
- **Switch-up 808 - mallets plays like the reference now, not one long arpeggio.** Each beat is its own figure, the way your reference does it: a roll (one note struck over and over in 32nds), a trill with the note next door, a hop between two chord tones, a quick run up into a note, an octave bounce - or a rest. Four beats make a motif that repeats for two bars with a small change, a new motif comes every four bars, the note it sits on walks between chord tones like a tune, and the quieter sections leave more gaps.


## 1.56.4
- **Drop a voice clip straight on the 🎤 Voice sample box** to load it (it lights up as you drag over it). It's named after the file and picked straight away. Dropping anywhere else still opens a project or uses the song as a reference.


## 1.56.3
- **Voice samples are easier to find**: a new **🎤 Voice sample** card above Parts, with its own "Load a voice sample…" button - load a clip and it's picked straight away, with the use / pitch / how-often choices right there. (It was tucked under Feel, and loading one meant going through 🎛 My samples.)
- **Switch-up 808 - mallets: the arpeggios now lock to the beat.** Every beat starts the run again from the bottom (up one beat, down the next) with the first note of each beat accented and the off-beat half a step down, instead of one long run drifting across the beats with random gaps. Their echoes are timed to the beat, their reverb is shorter, they duck a little with the kick, and the DJ pitch edits leave them alone.


## 1.56.2
- **New genre: Switch-up 808 - hard (punchy kicks)**: the switch-up 808 beat made aggressive - hard, distorted kicks with a sharp click and a fast pitch drop (more of them, double kicks), the 808 ducking hard out of their way, cracking crushed snares and claps, a dirtier 808, cowbell stabs, and a louder mix.
- **New genre: Switch-up 808 - mallets (fast arpeggios)**, from your reference: marimba and vibes rippling through the chords in 32nd notes (about 45 ms apart) and two-octave cascades over the switching 808, opening and closing on the mallets alone.
- **Renamed**: "Shadow 808" is now **Switch-up 808** (and Switch-up 808 - DJ edits). Songs saved with the old names still open.


## 1.56.1
- **The bass no longer goes squeaky-high in the switch-up 808 genres** (Bass-warp trap, Bass-warp fast, Switch-up 808, Switch-up 808 - DJ edits). The 808 now stays down low; whenever the bass leaps up or is raised (the switch-ups, breaks, octave jumps and outro), those notes are handed to a second, distorted mid-bass - a reese, growl or FM bass, picked per song - like the no-sub sections of the reference. It never goes above E3, and it's levelled so those parts no longer jump out louder than the drops. Together with 1.56.0's fix for the torn-speaker fizz on hard-driven 808 notes.
- **Fixed: the 808 getting very loud in parts**: any 808 notes still played higher up are turned down to match how loud they sound (the ear is far more sensitive at 100-200 Hz than at 40 Hz).
- **Chopped & screwed now gets the full DJ treatment, just slower**: fake vinyl slowdowns into nearly every hook, stuttered and repeated beats (more chops), hats and lead notes sinking and rising in pitch, the 808 switching up bar to bar with dead stops and rolls, and tape stops - over a darker, heavier mix (more low end, the top end rolled off). It now has hooks to slow down into (verse / hook / break form).
- **The app remembers your theme and window size.** Theme, visualizer and the other app settings are now kept in Studio Lab's own settings file (the window used to lose them when it opened on a different port or kept no storage), and the window opens at the size and place you left it.


## 1.56.0
- **New genre: Switch-up 808** (Electronic → Hip-Hop, Trap & Phonk), modelled bar by bar on your reference track (162 BPM, phrygian, 80% of the energy in the sub, almost mono, nearly nothing above 8 kHz). The 808 never plays the same bar twice: grinding root / flat-2nd 8ths, leaps of one or two octaves that slide back down, 16th rolls, dives, wobbles, bars of folded, buzzing 808 with the sub gone, chopped stabs, sudden gaps and dead stops where the drums cut out. The last bar of every 4-bar phrase leaves space.
- **New genre: Switch-up 808 - DJ edits**: the same beat cut up like a DJ is playing with it - **fake DJ slowdowns before the drops** (the record dragged by hand, sinking in pitch, then the drop slams in), hats that climb, dive, swoop and drop an octave, pitched rolls diving into the next bar, a lead that gets down-tuned, up-tuned and played a tone flat, plus chops and tape stops. Switch-up 808 gets a lighter dose of the same edits.
- **Voice samples, chopped & screwed.** 🎛 My samples → Voice samples: load a few seconds of a voice (a word, a shout, a line, a quote) and pick it under Sound → **Voice sample**. Uses: *chopped & screwed* (slowed and pitched down, words caught twice, a deep word into each drop), *stutter chops* (b-b-bounce it, rolls into the drops), *ad-lib one-shots*, *whole phrase* (intro, breaks, outro) or *melody* (it plays the lead's notes). Auto picks by genre: phonk / DJ / Houston genres screw it, club genres stutter it. Pitch (down / natural / chipmunk) and how often can be set too.
- **Arabic music** (Classic → Arabic), built like the Hindu genres: maqam melodies with **real quarter tones** (Bayati, Rast and Saba bend their half-flat notes a quarter tone; Hijaz, Nahawand and Kurd too), slides and turns on oud, ney and violin, and the darbuka / riq / bendir rhythms (maqsum, baladi, saidi): **Takht** (opens with an oud taqsim over a drone, then the ensemble), **Raqs sharqi** (belly dance, with a darbuka solo), **Arabic pop** and **Sufi dhikr** (the ney alone, then frame drums and chanting that speed up into a trance). New sounds: qanun, ney, riq, bendir.
- **Seven more genres from your reference tracks**: Deep dubstep - rolling percussion, Chipmunk 2-step (pitched vocal chops), Fourth-world ambient (FM marimba, pan flute, no drums), Outsider house (murky, lo-fi), Chopped & screwed (Houston slab, with the DJ's chops), UK bounce house, Glitch future bass.
- **Fixed: the tanpura "bass" playing off the beat** in Indian genres that speed up (jugalbandi, kirtan, qawwali ...): it plucked on a clock fixed to the starting tempo. Every string is now a note on the beat, so it follows the tempo.
- **Fixed: 808s sounding like a torn speaker on some notes** (higher notes, octave jumps, growls): the hard-driven 808 layer is now distorted at 4x the sample rate (no fizzy aliasing), driven less the higher the note, and its top end is rolled off.
- **Daisy Bell**: a vocal rider now evens out every vowel and every part of a word (A-weighted, as the ear hears it) - syllables now sit within about 1 dB of each other, where they swung by up to 8 dB inside a word. The sung vocals in songs get the same treatment.

## 1.55.0
- **Themes** - ⚙ Options → Appearance: pick a main colour, an accent colour (and a second accent) and light or dark, or start from a preset: Studio, Black & neon green, Midnight blue, Ember, Rose, Daylight, Paper & teal. Every part of the app follows the theme, and it's remembered.
- **A levels visualizer in the top bar**, in your accent colours - bars or a wave (or off) in ⚙ Options. It only runs while a song plays and costs about 0.1% of one CPU core.
- **⚙ Options** in the top bar now holds Appearance, ⟳ Updates (the "new" badge shows on Options) and 🩺 Report a problem.
- **Preview, 4 Variations, Full song and Surprise me are at the top**, with the exports, song length and status - they stay in view while you scroll the controls.
- **Skip the start screen**: a Skip ✕ button (or Esc), and it only comes back if you tick "Show this when Studio Lab opens".
- **Drop any song on the window to use it as a reference.** One of your Studio Lab projects still opens in the editor; anything else (MP3, WAV, MIDI ...) is analysed as a reference and its closest genres, tempo and key show right away.
- **⏭ Skip intro** on full songs: play from where the intro ends.
- **Fixed: the tanpura drone "doing its own thing" in the Hindu genres** - it plucked its strings on its own clock (every 0.9 s, whatever the tempo), so its low string drifted against the tabla like a stray bass line. It now plucks in time with the song, and its lowest string is softer.
- **Daisy Bell**: every syllable now sings at the same loudness (levelled by what the ear hears, after the robot effect - syllables used to differ by up to 9 dB), and the creepy machine voice sings a fourth lower with a rounder, less harsh buzz.
- **Fixed: buttons that showed up white with unreadable text** (Report a problem and a few others).
- **Fixed: Preview doing nothing after the layout change** (two elements shared one name); a test now guards against duplicate names.

## 1.54.1
- **Fixed: sounds you pick in Parts weren't being kept** - each new song went back to the genre's own sounds. Since the layout tidy-up in 1.51.5 the octave menu sat in front of the sound menu, and your pick was saved to the wrong menu (so it was never sent with the song). Picks now stick through Preview, Full song, 4 Variations, More like this and mood changes.

## 1.54.0
- **✨ Start here.** A friendly first screen (it opens the first time, and from the ✨ button any time): pick a kind of music - lo-fi, house, trap, rock, film score, bhajan, spooky surf, outlaw country ... or Surprise me - optionally a mood, and press **Make my song**. All the controls are still one click away.
- **Find genres fast.** The genre search now also matches instruments, scales and sounds (try *sitar*, *surf*, *organ*, *808*), ☆ stars favourites, and your ★ Favourites and 🕘 Recently used genres sit at the top of the list in every tab.
- **✨ More like this / 🔀 Something different** on every result. Tick what to keep - groove, chords, melody, sounds - and get a new song that keeps exactly those (a kept melody comes back note for note with its key, tempo and chords, in a fresh arrangement). *Something different* keeps only the genre.
- **Sung vocals.** Vocals → "ooh", "aah" or your own lyrics, sung on the song's melody in a female, male, choir or robot voice - with vibrato that blooms on long notes and a breathy tone. Lyrics are turned into syllables from their spelling (simple words work best). Genres without verses and choruses sing their lead melody. Command line: `--vocals`, `--voice`, `--lyrics`.
- **Reference → genre suggestions.** 🎯 Match a reference now also tells you which genres a song sounds closest to - tempo, key, the drum feel (four on the floor, backbeat, half-time, kick and hat patterns) and the tonal balance, compared with how every genre actually sounds - with one-click buttons to use them.
- **Recorded Indian instruments.** With the sound library installed, sitar, harmonium (reed organ), santoor (hammered dulcimer) and koto play recorded samples, slides and meend included; shehnai and shamisen are new recorded sounds; bongos use recorded bongos. (The tabla stays built-in - no free library has one yet.)
- **📤 Share a song.** Saves a tiny settings file; a friend opens it with **Presets → 📥 Load a shared song** and gets the exact same song.
- **Full song length** in one click under the buttons: radio edit, normal, extended / club or a 16-bar loop.
- **Smaller full songs.** Full songs now export MP3, MIDI and an LMMS project by default; the exports that save every part as audio (Stems, Waveform, DAW pack, sample pack - often 200-500 MB a song) are off until you tick them, and your choice is remembered.
- **Meend & gamak - the sliding, shaking notes of Indian music.** On sitar, veena, bansuri, saz, oud, violin and shehnai, held notes now pull slowly in from the previous note (up to 5 semitones, up or down), shake up to the note above and back (gamak), sway on very long notes (andolan) and fall into the next note - the way a sitarist pulls the string sideways. Raga-phrased genres have it built in; **Bends** (Feel card, or `--bends`) makes it Subtle, More or Off. Works on recorded instruments too.
- **Previews keep every ornament.** Previews used to drop strums and slides (the full song had them); now strums, slides and bends are in previews too.
- **Fixed: the bass "breaking" in breakcore, drum & bass and other reese-bass genres.** The reese was re-struck on every beat with a small gap, so it dipped 3-6 dB and restarted its growl each time; held basses (reese, growl, sub, wobble...) now roll on legato and only change where the pitch changes. And the reese's detuned saws no longer cancel its sub: the low end stays steady instead of swelling and dropping out by ~8 dB on held notes.
- **The 80s sampled shakuhachi** - a new instrument with the breathy chiff, the scoop up into the note and a blooming vibrato (the recorded General MIDI shakuhachi when the sound library is installed) - and **three genres for it**: *80s adult pop - gated drums & shakuhachi*, *Smooth jazz - horns & shakuhachi* (a unison horn section with the shakuhachi answering) and *Chant downtempo - shakuhachi & monks* (it opens on a lone shakuhachi, then the monk choir and the slow heavy break). Japanese zen and 90s new-age chill now use it too.
- **Automatic mix check** (tests/mixcheck.py, run on every update): every genre on three seeds - no part loses its genre level, no lead is buried under the chords, nothing is extreme; `--measured` renders songs and measures the real stems.

## 1.53.0
- **19 new genres**:
  - *South Asian*: **Qawwali** (Sufi: lead line answered by the chorus, harmonium, tabla, dholak, hand claps, speeding up towards ecstasy), **Bollywood / filmi** (60s-70s: swinging dholak and bongos, strings, sitar and bansuri), **Ghazal** (slow and poetic: sitar, harmonium, gentle tabla, santoor), and **Carnatic kriti** in Hindu devotional (veena alapana, then pallavi / anupallavi / charanam with mridangam, kanjira and ghatam).
  - *Psych & world rock*: **Anatolian psych rock** (saz in the Hicaz mode, fuzz guitar, combo organ, darbuka), **Thai funk / molam** (phin and khaen over a funk beat with ching), **Chicha** (Peruvian psychedelic cumbia), **Desert blues** (Tuareg interlocking guitars, claps, hand drums).
  - *Jazz*: **Ethio-jazz** (a hypnotic minor groove, vibraphone, horn riffs, organ), **Exotica / tiki lounge** (vibes, congas and bongos, strings, flute bird calls).
  - *Rock*: **Garage rock** (60s fuzz and Farfisa-style organ, tambourine), **Rockabilly** (slap bass, twang with slapback, 12-bar shuffle), **Post-punk** (melodic chorus bass, trebly angular guitars), and **Krautrock / motorik** in Electronic (the endless straight beat, pulsing bass, layers fading in).
  - *Latin & world*: **Flamenco rumba** (rasgueado guitar, falsetas, palmas, cajon), **Son cubano** (tres montuno, son clave, bongos, maracas, trumpet), **Klezmer** (a slow free doina on clarinet, then the band jumps into a fast freylekhs), **Gamelan** (metallophones in the pelog scale, gongs closing each cycle, kendang), **Rai** (darbuka maqsum, oud, accordion, synth lead in Hijaz).
- **New instruments**: saz / baglama, oud, veena, khaen, phin, tres, gamelan metallophone; mridangam, darbuka (doum and tek), cajon, gong and kempul. New scales: pelog and Ukrainian dorian.
- **Hand-drum genres never get rock toms**: every fill and build-up in tabla / dholak / darbuka / cajon / bongo genres is played on the genre's own drums.
- **12 new samples in the README** (Hear it): a Hindu bhajan groove, the monster TV theme, outlaw country, stoner raga, Anatolian psych, ethio-jazz, qawwali, flamenco, rockabilly, gamelan, raw juke and garage rock.
- Tests no longer leave their rendered previews behind (a full test run used to leave ~1.5 GB in the temp folder).

## 1.52.1
- **Four more Hindu devotional genres, led by drums and sitar** - each opens either on the sitar alone over the tanpura drone or on the drums alone:
  - *Bhajan - sitar & tabla*: the sitar unfolds the raga alone, the tabla plays the cycle by itself for a moment, then the song begins with the sitar on the melody.
  - *Bhajan groove - tabla, dholak & bongos*: the drums start alone and lock into a rolling keherwa, then the drone and sitar come in; a drum break in the middle and a drums-only ending. Percussion up front.
  - *Kirtan - drums & sitar*: dholak, bongos and kartal open it, the sitar calls each line and the group answers, with drum breaks - speeding up until it's wild and ecstatic.
  - *Sitar & tabla jugalbandi*: a slow sitar alap, the tabla joins, then they trade solos phrase for phrase before playing together, faster and faster, into a blazing jhala.
- **New drums: bongos** (high and low finger slaps).
- No more violin in the devotional genres: their melody is played by sitar, bansuri, santoor or harmonium.

## 1.52.0
- **Easy installers - no Python needed.** Each release now has a Windows installer (`StudioLab-Setup-<version>.exe`) and Mac disk images (Apple Silicon and Intel). They carry their own private Python with everything Studio Lab uses - audio libraries, VST plugin support and an MP3 encoder - so nothing else has to be installed. Windows installs per user (no admin password), with Start-menu and desktop shortcuts and a normal uninstaller; on a Mac you drag Studio Lab into Applications. ⟳ Updates keep working, and your songs, presets and sounds are kept across updates and reinstalls. Each installer is built and tested automatically (installed, a song made, uninstalled) before it's published.
- **MP3 export without ffmpeg.** If ffmpeg isn't installed, Studio Lab now encodes MP3s itself (lameenc, included in the installers), with title / artist / genre tags.
- **Hindu devotional music - four new genres** (World → Hindu devotional), built around the raga's rising and falling movement:
  - *Bhajan*: a heartfelt devotional song - harmonium following the melody, tanpura drone, dholak in an 8-beat keherwa and manjira cymbals; a free opening, then refrain (sthayi) and verses (antara).
  - *Kirtan*: call-and-response chanting - each line is sung and then answered by the group, with harmonium, kartal / manjira and dholak; it starts slow and **speeds up chant by chant** (about 70 → 140 BPM) until it's ecstatic.
  - *Aarti*: the temple prayer - bells ringing on every beat, manjira, dholak and harmonium under a joyful melody, ending on the bells alone.
  - *Devotional raga (santoor)*: the santoor's bell-like strikes and shimmering strings rising and falling through a morning raga over the tanpura; a free alap, then the tabla enters and it builds to a glittering jhala.
- **Raga melodies**: a new lead style for these genres and Raga (sitar, tabla, tanpura): each phrase winds upward (aroha) - sometimes touching the note above and turning back - to a peak it holds, then falls back (avaroha) to rest on Sa or Pa, with meend glides into the long notes. New raga scale **Bhairav** (the classic morning raga).
- **New instruments**: harmonium (two beating reed banks, bellows breathing), santoor (hammered unison strings with a bell-like strike and a long shimmer), manjira hand cymbals, and dholak (bass "dha" and treble "ta"). Hand-drum genres now fill on their own drums instead of a rock tom roll, and have no EDM risers, impacts or crash cymbals.
- **New genre: Stoner rock - raga / psych** - slow, heavy fuzz-guitar riffs and fuzz bass under a tanpura drone, tabla rolling on top of the drum kit, and a sitar singing raga phrases; it opens on the drone and sitar alone, breaks down to tabla and sitar, then ends in a heavy psychedelic jam.
- **New genre: Spooky surf - organ & brass** - the monster TV theme with a reedy combo organ (Farfisa / Vox style) holding every chord and taking a creeping organ break, a full horn section on stabs and melody, over the same twangy guitar + bass chromatic riff.
- Fixed: a genre with a single build-up style could crash song generation.
- Fixed: when a genre picked one of its alternative sounds for a part (say, a sampled distorted guitar instead of its built-in one), that part lost the genre's mix level and fell back to a generic one - often too quiet (riffs) or too loud. The genre's balance now stays.

## 1.51.6
- **Swing no longer moves held chords and pads.** Swing pushes every other 16th late; a pad or sustained chord that started on one of those spots came in late too and smeared against the beat. Notes held 3/4 of a beat or longer now always land straight on the grid. Short stabs, plucks, bass and drums still swing, as the genre wants.

## 1.51.5
- **Chords through plugins play as chords again.** When a chord, pad or stab part was played by a plugin synth (TAL-NoiseMaker, Surge XT, Dexed, or a sound you saved), the synth kept whatever voice mode its loaded preset had - often mono or legato with portamento. A chord then came out as a single note that slid in late, one note per chord, so supersaw / pluck chords sounded like a slow, delayed arpeggio, and songs across many genres sounded alike. Any part with notes that sound together now switches its plugin to polyphonic, full voices, no glide, before it plays (leads and basses keep their glide).
- **Tighter middle column.** Feel / Mix knobs sit in a compact strip; menus pair up two per row with their long hints moved into hover tooltips; Parts shows one row per part (sound, volume, octave, mute, 🎲); the action bar is solid and the export buttons sit in one scrolling row; cards use 3 columns on wide screens and 1 on narrow ones. Big cards (Cinematic Journey, orchestra) keep their full layout and stay collapsible.

## 1.51.4
- **Sounds no longer change behind your back.** With "Keep my sounds" (Parts → Sounds between songs, the default), each new song keeps the sounds you just heard on every part - so changing one part's sound, or pressing Preview again, no longer swaps the others. The Sound menus show what's playing. 🎲 / Re-roll sounds / ↺ Genre sounds, setting a part back to "Style default", or changing genre (which keeps only the sounds you picked yourself) let the genre choose again. "Genre picks" gives every song its own sounds, as before.
- **Daisy Bell moved** into 🩺 Report a problem - click the little robot at the bottom of that window.

## 1.51.3
- **Build-ups no longer default to a snare roll.** 64 genres had no build-up of their own and fell back to a snare ramp - lo-fi, ambient, trap, deep and garage house, hauntology, footwork and more. Each genre now gets a build-up that fits its beat: a filter sweep for four-on-the-floor, a drop-out for half-time / dembow / garage / syncopated beats, a stutter or half-time switch for breakbeats, a swell where there are no drums. Snare and kick ramps stay only where they belong (trance, big room, drum & bass, dubstep, hardstyle, rave, UK hardcore, big beat ...), and even there not on every build.
- **Juke, footwork, gqom, dub techno, minimal and similar never ramp**: their builds are drop-outs - the groove falls away to percussion or nothing and slams straight back.
- **Two new juke genres from your references** (studied hit by hit on a 16th grid):
  - *Juke / ghetto house - raw (130)*: kick on 1, the "a" of 2 and the "e" of 4; claps and hand percussion in the same off-kilter pattern every bar; dense 16th hats; a huge sub; a long drums-only intro; breakdowns to almost nothing; one repeated vocal chop - no build-ups, all repetition.
  - *Juke house - bouncy (126)*: a 3-3-2 tresillo kick, hats on the off-grid spots, claps every five 16ths for a rolling cross-rhythm, a busy 16th percussion loop, a fat sub and one bright major-key synth riff.
- **Surf rock, spooky surf and the monster TV theme, re-tuned to your 60s TV-theme reference** (around 154 BPM, kick 1 & 3, snare 2 & 4, 8th hats): a low tremolo-picked twang guitar rumble on the bass line (the twang guitar can now tremolo-pick, about 15 picks a second like the record), a dark, bass-heavy 60s mix (a new vintage tape top-end roll-off in mastering) and wider stereo. Tone balance now within ~2 dB of the reference.
- **Daisy Bell: every syllable at the same volume.** Each sung note is levelled automatically (a note used to jump louder or softer depending on whether one of its harmonics landed on a vocal resonance).
- **Storage clean-up** (Library → 🧹 Storage): previews are cleared after a day; songs you haven't ⭐ kept are, after 1-90 days (default 7), either trimmed to their MIDI + settings file - the Library offers ⟳ Re-render, which rebuilds the exact same song - or deleted completely, or left alone. ⭐ Keep on any full song (result card or Library) protects it. Only Studio Lab songs are touched.

## 1.51.2
- **Daisy Bell says "Daisy" again, not "Die-easy".** The first syllable was spelled with the "eye" vowel instead of "ay", and every two-part vowel (ay, eye, oh) glided for over a third of the note - so long notes sang a separate "ee" before the next consonant. The main vowel is now held and only glides to its end sound in the last moment, as a singer does. Both voices.

## 1.51.1
- **Daisy Bell, fixed and with a second voice.** The computer voice was mostly hiss and clicks: its vowels came out 35-50 dB quieter than the consonants (the vocal-tract resonances were chained so they cancelled each other). It now sings clearly - vowels carry the voice at an even level, consonants sit under them and land just before the beat.
- **Pick the voice** next to the 🤖 Daisy Bell button: *Creepy machine* (high, buzzy, bit-crushed) or *Deep, calm computer* - an octave lower, slower, smooth and warm, with a softer music box; it starts winding down early in the second chorus and sinks much further. Command line: `python studiolab.py daisy --deep`.

## 1.51.0
- **Orchestra plugin detection (BBC Symphony Orchestra, LABS, Kontakt).** Sounds & instruments → 🎻 Orchestra plugin → ✨ Detect my instruments: the plugin opens once, you click through the instruments (and articulations) you want in its own browser, and each one is recognised from the plugin's state and saved with the right name ("BBC celli pizzicato (Celli · Pizzicato)"), so matching parts in every genre use it. No naming, no reopening. Sounds it can't name are kept for you to name; saved sounds can be renamed, tested and removed in the same window.
- **One "Sounds & instruments" window** replaces the five header buttons (Real instruments, Genre VSTs, VST, My sounds, My plugins): an overview of what you have plus a tab for each.
- **Your sound picks stay picked.** Changing genre, blending or Surprise me no longer clears the sounds you chose for bass / chords / pad / arp / lead; parts left on default follow the new genre. Choose "Genre picks" in Parts to get the old behaviour. A part you picked also stops being swapped out in some sections by the genre's instrument rotation.
- **Drum style and drum sounds are separate.** *Drum style* = what the drums play (the genre's beat, a classic break, the genre's programmed beat without its break, or any other genre's beat); *Drum sounds* = the kit (machines, real kits, sampled-break kits, your samples). Changing the sounds never changes the patterns: jungle on a 909 still plays its jungle break, boom bap on brushes still plays its laid-back funk break. Old settings that picked a break as the kit still play that break.
- **Drummer and percussion, also separate.** *Drummer* sets fills (none / fewer / more), ghost notes (off / more) and hi-hats (sparse 8ths / busy 16ths) on whatever beat plays. *Percussion* is picked on its own: the genre's, none, or a set - shakers, tambourine, disco, Latin (real campana), Afro, Caribbean (iron), woodblocks. Songs with everything on "Genre" are note-for-note the same as before.
- **Smarter drum style menu:** beats that fit the song's tempo come first, then half / double time, then the rest grouped by feel; every beat is labelled (four-on-the-floor, half-time, two-step, breakbeat, swing / shuffle, dembow / clave, backbeat, 3/4 ...), and beats in another meter aren't offered.
- **Genre fixes:** jazz leads on trumpet (not a brass section) and keeps an upright bass; the string quartet's harmony is a viola, not a full section; Classical-period broken chords on short strings instead of piano; no timpani thud in the minuet; celli / basses (not the whole section) on the bass line in Orchestral, Film Piano and Cinematic; Japanese zen gets one soft taiko stroke a bar and an airy pad instead of Western strings; no drum-kit kick in salsa; big band swing and bebop on sticks instead of brushes; boogie rock now shuffles; metal on a tight modern kit; synth brass, tuba and e-piano removed from the Classical-era sound pools.
- **Drum check of all 217 genres** against how each style is played: 90s Italo piano house keeps its four-on-the-floor kick in every section (two of its three patterns had lost it), western swing rides the jazz "spang-a-lang" pattern instead of a dotted shuffle figure, and melodic techno's closed hats roll in soft 16ths instead of doubling the off-beat open hat.
- **40 new genres (257 in all).**
  - *Electronic:* French house / filter house, trip-hop, big beat, hard techno (150), UK hardcore / happy hardcore, dub techno, gqom, UK funky, electro swing, darkwave / EBM, Baltimore club, tropical house, Hi-NRG, Latin freestyle, Berlin school, witch house, midtempo bass, Brazilian bass, speed garage and Latin trap.
  - *A new Footwork & Juke group:* footwork (160, triplet-feel kicks, chopped vocal stabs), Chicago juke / ghetto house, soulful footwork (jazzy chops, Rhodes, sax) and dark experimental footwork (interlocking toms and hand drums).
  - *Classic:* Afrobeat (70s), dub, corridos tumbados (3/4, tuba and requinto), bachata, merengue, samba, gypsy jazz (la pompe, no drums), New Orleans brass band, shoegaze, post-rock, pop-punk / emo, doom / stoner metal, ragtime / stride piano, bhangra, musical theatre and anime opening.
- **Signature grooves are protected.** The variety pass used to mix generic extra drum patterns into every genre - which could put a kick on 1 and 3 under reggae's one-drop or dilute dembow, clave and footwork. 46 rhythm-defined genres now always keep their own drum patterns.
- Without the sound library, nylon guitar now falls back to the acoustic guitar instead of an electric one.
- **🤖 Daisy Bell:** a button (and `python studiolab.py daisy`) that renders "Daisy Bell (A Bicycle Built for Two)" (1892, public domain) sung by a creepy early-computer voice - a new formant singing synthesizer that pronounces the lyrics on a dead-steady, vibrato-free pitch, bit-crushed and doubled - over an old-computer music-box waltz (the vowels carry the voice, consonants sit about 10 dB under them, and each consonant lands just before the beat so the sung note is on time). The second chorus winds down like a machine losing power: slower and slower, sinking in pitch.
- README and genre docs updated for all of the above.

## 1.50.0
- Hopecore redone from accordion-led references: 118–140 BPM (no more drum & bass), mostly major, lush 7th / add9 chords on electric piano, intricate two-octave "cascade" arpeggios in triplets (accordion doubled an octave up on celesta), a warm sub, and soft low drums (gentle kick, quiet snare, barely-there hats) that sit out of the long intro and the breakdown; no big drops, quieter master.
- The old fast, chopped-break version is kept as "Hopecore breaks (fast)".
- New arp mode `cascade` (two-octave ripple up and down the chord).

## 1.49.0
- Walking bass "skips" (from big-band / swing MIDIs): about one beat in five gets a soft triplet ghost pickup into it, like a real upright player. New style key `walk_skips` (default 0.2; walk-mode genres).
- Synthwave / dark synthwave (night-drive ref): half-time kick, 8th-note bass that rests on the downbeat, v–iv–III–i descent.
- Motown / 60s pop (brassy-pop ref): two-step kick and bass, iii–ii sway.

## 1.48.0
- Liquid DnB lead run-ups (from a liquid-anthem lead MIDI): before a long held lead note that follows a gap, a fast 16th-note arpeggio sweeps up through the key in thirds into it. New style key `lead_runs` (probability); on for liquid_euphoric and liquid_dancefloor.

## 1.47.1
- Electric bass no longer sounds like a plucked string: the built-in `ebass` (used by ~30 genres, and the stand-in for finger/pick bass when the sampled sound library isn't installed) is now a sustained P/J-style body with a short finger transient, holding for the full note length. Level-matched to the old sound.

## 1.47.0
- Reference-MIDI pass (≈30 files): new grooves and progressions for future bass (bouncy kick), hard trance (one-chord vamp, offbeat bass), trap (i–bVI sway), 2000s R&B (sparse syncopated kicks and matching bass, IV–vi–I, i–ii dorian vamp), synthpop (skippy kick, ii–V–I–vi), jam band (stop-time boogie bass, dotted vamp bass, two-chord vamps), folk jam / soft rock (push-kick bass), bluegrass (two-beat bass), disco (up to 130 BPM, i–iv vamp, driving and pushed bass), disco-funk (vi–IV–I, post-disco kick), nu-disco (bVI–i sway, boogie bass), funk (one-chord vamp, double-kick pickups) and smooth funk (busy 16th bass).

## 1.46.2
- More reference-MIDI patterns: i–bIII sway, bVI–bIII–i–bVII, offbeat tambourine, octave-bounce 8th bass and a 128 BPM floor for eurodance; i–bIII–ii–i dorian sway and a sparse dotted bass for melodic / deep house; i–i–bIII–iv loop and dotted rolling bass for progressive / uplifting trance.

## 1.46.1
- Patterns learned from reference MIDIs: 2-step kick/bass and i–bVI–bIII–v for UK garage; 8th-note "train" and shuffle-boogie bass lines plus I–IV–ii–V for jam band / 80s jam rock; V–ii–ii–I anthem loop for 90s alt rock; ii–I–V noir-ballad loop for soft rock; vi–I sway for downtempo.

## 1.46.0
- **Parts no longer squeal too high.** Every melodic part (lead, arp, chords, pad) now stays in its instrument's comfortable range. If the middle of a part sits above or below its instrument's range, the whole part moves by octaves and keeps its shape. Ranges are set for 60+ instruments: sax, trumpet, brass, trombone, horn, flute, clarinet, oboe, violin, cello, guitars, pianos, mallets, synth leads and more. Example: your swing song's brass lead moved from around A5 down to A4.
- **Octave control for every part.**
  - **Parts panel:** each part has an "8ve" menu (-2 to +2) next to its volume.
  - **Song editor:** every sound in the song has one too, including section switches and layers.
  - **Saving:** it's saved with your settings (`octaves`).
- New genre **Christmas orchestral - magical (celesta)**, from your MIDI of a family-Christmas sequel's opening titles.
  - **The sound:** a hushed, glittering cue around 95 BPM. A celesta melody way up high doubled by flute, rippling harp, vibraphone and soft piano, low strings, soft sleigh bells, a triangle and one timpani swell.
  - **The harmony:** minor-key magic with the flat sixth, minor iv and a dark Neapolitan chord.
- **Christmas joyful / mischief** use the film-score harmony colour seen in your MIDIs: secondary dominants and the bittersweet borrowed minor iv. Mischief now reaches the flight cue's 154 BPM.

## 1.45.0
- **Two Christmas film-score genres**, from four of your family-Christmas-movie score cues.
  - **Christmas orchestral - joyful:** a lilting 3/4 carol for full orchestra.
    - **The players:** oom-pah celli and basses, pizzicato off-beats, a violin melody doubled by glockenspiel an octave up, celesta sparkle, a children's-choir pad with horns, sleigh bells and timpani.
    - **The shape:** it starts hushed and swells chorus by chorus, with a key change up for the last chorus and a big held final chord.
  - **Christmas orchestral - mischief:** the action cue, a driving 4/4 around 130-140 in a minor key.
    - **The players:** a staccato low-string ostinato, stabbing strings, horn and trombone blasts, chromatic woodwind scurries, a sneaky flute / celesta motif, snare, timpani and sleigh bells.
    - **The shape:** a rising build, the chase, a hushed sneaky break, the chase again, and a low unison hit.
  - **Mastering:** both are mastered gently with the wide dynamics of the references.
- **Fast bass-warp trap**, from your notes on that style:
  - **The 808:** sits on the root more, with occasional slides rather than constant ones.
  - **The texture:** the whole mix is a little more saturated ("nuked"), and the lead and arp get heavier reverb and delay.
  - **Cowbell stabs:** cowbell is now one of the lead choices.
- A genre can now force its last-chorus key change (`key_change`).

## 1.44.2
- New genre **Bass-warp trap - fast (160)**, from your two 159-162 BPM references and your hard-bass / trap-hat production notes.
  - **The tempo:** full speed, not half-time.
  - **The bass:** dotted 3-3-2 kicks with the 808 bouncing on them in short, sliding, diving and wobbling notes. A clean mono 808 sub plus a parallel, heavily driven copy for the mid growl, both sidechained hard to the kick.
  - **The drums:** gritty bit-crushed snare / clap and hats, and a cowbell now and then.
  - **The switch-ups:** stutters, tape stops, gaps, the 808 leaping up with the sub gone, and a 32-bar stretch of distorted, growling 808 before the clean sub slams back.
- **Bass-warp trap** (the original) retuned from your two songs:
  - **Fewer moves:** fewer slides and octave / fifth jumps, so the 808 sits on the root more and the sub weighs more.
  - **Same production:** the same parallel grit layer, kick sidechain, crushed tops and pitched hat rolls as the fast genre.
  - **Sparser melody:** no automatic doubling of the melody parts.
- **Trap hats can now pitch their rolls up** step by step (genres opt in), and the trap-hat generator now runs in the bass-warp genres (it was being skipped).
- New genre building blocks: per-genre 808 behaviour (`oct808`, `fifth808`, `glide808`, `warp_min`), a whole section of growling 808 (`bass_mod`), and `keep_fx` (effects a genre keeps when its drops land plainly).

## 1.44.1
- New genre **Bass-warp trap (808 switch-ups)**, from your three bass-heavy references (130-150 BPM in half-time, analysed in 2-bar blocks).
  - **The 808:** a monstrous, ultra-low 808 (down to B0, 70-90% of the energy) that never sits still. The roots flip every two bars and notes slide into each other. Held notes **warp**: pitch dives of up to an octave, octave rises, 2-3 semitone wobbles and growls (the 808 can now do all four).
  - **The switch-ups:** every few bars, the drums drop out, the 808 and kick play alone, sudden gaps hit, or new drum patterns take over. The 808 **leaps two octaves up with the sub gone** for 8 bars, then slams back down.
  - **Around it:** a no-sub breakdown, and a quiet, eerie bell / choir melody under it all.
- New genre building block: a section can move its bass up to a set register (`bass_up`).

## 1.44.0
- **The song editor can change drums.**
  - A **Drum kit** menu swaps the whole kit.
  - Every drum part has its own sound menu (a different snare, a rim or clap instead, a shaker for the hats ...) and can be switched off, the main kick and snare included. Before, drums only had a "playing" tick box, and the main kick / snare couldn't be changed at all.
- **Fix: the "1-2" flam on pads.** A struck instrument (piano, e-piano, guitar) was sometimes layered with a swelling one (string machine, supersaw, strings) on the same chords. The struck note landed on the beat and the swell peaked a 16th later, which you heard as a doubled, slightly late hit.
  - Layering now only pairs sounds of the same kind.
  - A pad under struck chords swells in slowly instead of landing late.
- **Two new liquid drum & bass genres**, modelled on nine of your liquid DnB reference tracks, analysed bar by bar.
  - **The shape:** a 16-32 bar intro, a short build, ~64-bar drops in 16-bar phrases with a switch-up at each phrase end, a beatless keys breakdown, a second drop and a DJ outro.
  - **The details:** the sub only arrives in the drops, the mid-bass pumps in 8ths and 3-3-2 figures, the chords change every bar, and there are rolling ghost-snare two-step breaks and 16th-note bleeps.
  - **Liquid DnB - euphoric (piano & bleeps):** major keys, bright piano, strings and a singing lead.
  - **Liquid DnB - dancefloor roller:** minor keys, a reese that trades with a clean sub every 4 bars, brass stabs.
  - **Mastering:** both are mastered louder, like the records.
- New genre **Boogie blues-rock (slide)**, from your four bar-band boogie references.
  - **The feel:** a heavy 0.62 shuffle at 95-125 BPM in E, G, A or D (open-tuning keys), with 12-bar choruses.
  - **The riff:** the bass and an overdriven rhythm guitar lock on the boogie riff, climbing root-3-5-6 in one bar and coming back down from the flat 7th in the next.
  - **The solos:** a distorted slide guitar answers and takes a solo chorus, and a tenor sax takes another. The mix is dry and mid-heavy, and the song ends on a hit.
- **Interface tidy-up.**
  - **Parts** (was Sound) puts every part's sound, 🎲, mute and **volume** on one row, and the drums the same way (kit, my samples, per-drum mutes, drum volume). The separate "Part levels" block is gone, and **↺ Volumes** resets them.
  - A new **Arrangement** card takes build-ups, build style, transition FX, instrument rotation, counter-melody, layered sounds and ending out of the crowded Feel card.
  - **Basics** (tempo, seed, key, scale, length, structure, reference, chords) moved to the bottom, above the Preview buttons.
- New genre building blocks: `bass_cycle` (bass patterns bar by bar), boogie bass notes (`3` `5` `6` `7`), `roots` (allowed keys), a per-part `presence` EQ (amp-style scoop and bite), `switch_db`, and a per-genre limiter allowance (`max_gr`).

## 1.43.3
- **Band genres sound like a band at transitions.**
  - Rock, jazz, swing, funk, Latin, country, folk, blues, soul and gospel, world, and the acoustic side of pop no longer get studio transition FX: reverse-cymbal "tssss" swells, cymbal-roll swells, risers, noise washes, tape stops, impacts or filter sweeps. Their transitions are the band's own: fills, stops and a crash on the downbeat.
  - That crash is now 4 dB lower, so it sits inside the kit.
  - Hip-hop and produced styles (electro-funk, soca, new jack swing, modern R&B, pop, modern country) keep their FX, and so does every electronic genre.
- **Surf rock, spooky surf and the monster TV theme have no cymbal FX at all.**
- New genre **90s pop house / dance-pop**, from your two references (a 123 BPM club-mix radio edit and a 133 BPM dance-pop single).
  - **The groove:** a full four-on-the-floor from bar 1 with a clap backbeat, shuffled 16th hats and off-beat open hats, a bouncing octave synth bass, sidechained string pads, syncopated chord stabs and a plucked arp.
  - **The song:** verse and chorus at radio length with no EDM build-ups, one breakdown where the bass drops out, and a hard stop.

## 1.43.2
- **Surf rock no longer sounds double-time.**
  - Tempo is now 132-156.
  - The tremolo-picked lead comes in bursts instead of nonstop 16ths.
  - The floor tom plays quarters, and bass and rhythm guitar play quarters and 8ths.
- New genre **Spooky surf - monster TV theme**, modelled on your 60s monster-sitcom theme reference (analysed at 152 BPM in E).
  - **The riff:** a low chromatic crawl (root, a half step up, back, a half step down) played by the bass and a twangy guitar together, with brass stabs over it.
  - **The bridge:** a brass melody in the relative major (III-VII-VI), then a sax-section stretch.
  - **The ending:** the riff theme twice more, then a big stab.
  - **No swaps:** the line-up stays fixed, with no instrument rotation or automatic doubling.
- **Genres can pin each section's chords** (`section_progs`), and **bass patterns can play chromatic neighbours** (`u` = a half step up, `d` = a half step down).
- **Fix: "pick bass" and "finger bass" played as a synth pluck** when the General MIDI sound bank isn't installed. They now fall back to the electric bass.

## 1.43.1
From your exported songs (jazz, funk, rock, bossa nova, lo-fi, drum & bass, house, spooky surf), each re-created from its seed and measured against your reference tracks.
- **Fix: the genre's own instrument sometimes never played.** Instrument rotation (other sounds for verses / breaks) treated lo-fi's "B" sections and jazz's "head" as verses. The swapped-in sound then covered the whole song: your lo-fi had two guitars and no Rhodes, and your jazz had no main lead. The genre's own sound now always keeps the sections where it plays most.
- **Rotation swaps stay in the same instrument family:** keys with keys, guitars with guitars, synth leads with synth leads, horns with winds. No more twang guitar in a house verse or piano in a surf arp. The "Lots" rotation setting still allows any swap.
- **Mixes rebalanced against your references:**
  - **Jazz:** the upright bass was over half the mix. It's now 5 dB lower and high-passed, the kick is feathered, and piano and horns are up.
  - **House:** less sub in the kick, more bass, chords and pads.
  - **Funk:** brighter hats, kick and bass down, keys up.
  - **Lo-fi:** softer kick, more hats.
  - **DnB:** chords high-passed, bass up.
- New genre **Surf rock (60s)**: the regular, sunny version of spooky surf. A floor-tom surf beat, twangy guitar tremolo-picked on the low strings in spring reverb, strummed rhythm guitar, root-fifth bass, combo organ or sax for a chorus, and a drums-only tom break.

## 1.43.0
Genre research, round 2 (your reference tracks), your genre-spec review, and genre traits.
- **Genre traits ("Character").**
  - Every genre now carries twelve rule categories: arrangement, density, human feel, melodic behaviour, bass personality, drop / payoff, variation, context, texture & space, rhythmic feel, harmony and energy curve.
  - Most are read from each genre's own rules. Deep dubstep, classic house, jump-up, gospel and a few others are declared by hand.
  - Change any trait in the new **Character** card (or `--trait density=sparse` on the command line) and it steers the song. For example: sparse / dense / evolving parts, a slow-build or peaks-and-valleys energy curve, robotic vs loose feel, sub-only / walking / 808 bass, sudden vs long-build drops, dry vs massive reverb, static vamps or jazz extensions, and switch-up bass changes every 2 bars.
  - **🎲 Surprise me** changes two of them per song.
  - With no traits chosen, songs are exactly as before.
- **Moog bass is now a sustained bass.** The filter opens on the attack and settles half-open, so held notes stay full in house, synthwave, liquid and pop. The plucked, snap-shut version is now its own sound, **Moog-style bass (plucked, funk)**, used by G-funk, nu-disco, neo-soul, synth-funk and the funk & disco genres.
- **Fix: pianos turning up as leads in synth genres.** Piano is no longer a lead alternative in 22 synth-led electronic genres (trap, drill, trance, garage, chillstep ...). Piano-led genres keep it.
- **From the reference tracks:**
  - **Tango** gets loud / soft section dynamics and a 108-132 tempo.
  - **Bossa nova** runs 116-148.
  - **New jack swing** keeps its drums constant through the whole song.
  - **Cumbia** keeps the whole band constant and adds an accordion solo section.
  - **Soca** is full power from start to finish.
- **New genres:**
  - **Groovy soca** (the slower lane, 114-132).
  - **Baroque organ** (toccata form, pipe organ, free tempo).
  - **Jump-up DnB:** a rubbery talking wobble bass that switches every few bars.
  - **Dark synthwave:** slower, minor, a pulsing analog bass.
  - **Modern gospel:** choir, organ, piano and 808, with a bridge and a lifted last chorus.
  - **Neurofunk (lighter):** clearer chords and a hummable lead.
- **From your spec review:**
  - **Hauntology variants:** warmer scales, slower tempos, more tape wobble and a texture layer. The original Hauntology is unchanged.
  - **Swing:** acid and progressive house get a touch of swing.
  - **Chord length:** long progressive and cinematic genres sometimes hold each chord for two bars.
  - **Low drums:** timpani, taiko and other lowest drums are labelled as the genre's "kick-role" part in the editor and the spec.
  - **Deep dubstep:** the sound briefs spell out half-time (kick on 1, snare on 3) and the sub vs mid-bass balance.
- **No artist names:** genre descriptions and labels no longer name artists, songs or albums.
- **docs/GENRE_SPEC.md:** every genre's full technical rules, now with its traits, for review by you or another AI.

## 1.42.0
Genre research, round 1: production guides and genre write-ups checked against the genre settings.
- **Sunny melodic house**: now follows your three melodic-house references. It uses their radio-edit shape: keys and pads with the hats joining, kick and sub without hats, 16 bars in full, a 12-bar kick-out breakdown carried by hats, keys and the lead, kick and sub alone, then the last 24 bars.
- **Amapiano**: 108-115 BPM (112 at the centre). The log drum now bends between root and fifth into the kick's gaps, and the shakers are accented.
- **Reggaeton**: drops take everything out but the bass, then come back on the snare.
- **Dancehall**: modern riddim tempo (92-106), a verse / chorus song form, and a second off-beat rim pattern.
- **Jersey club**: 130-142 BPM, with the real five-kick bar (spaced 4-4-3-3-2 sixteenths) and the kick-on-1-plus-cluster variant. The snare / clap is on 3, the hats sit on the off-beats, and a bed-squeak-style hit is added.
- **Baile funk** and **afrobeats**: build-ups and tempo adjusted to the sources.
- **Hardstyle**: its classic song shape. A DJ intro with kick and reverse bass, a mid-intro with the lead motif, a long melodic break, a snare-roll pre-drop, the climax, a harder mid-outro, then the outro.
- New genre **Funk 150 / mandelao**: the 150 BPM Brazilian funk wave, with the tamborzao sped up, clipped claps, tom and rim fills, a blown-out 808, and beat drop-outs for chants.

## 1.41.0
- **Every genre now suggests several sounds per part.** I audited all 198 genres. Each part's dropdown now starts with **"Suggested for this genre"**: the genre's own sound first, then 2-3 idiomatic alternatives (e.g. upright → acoustic / finger bass for jazz; distorted → overdriven guitar for rock; oboe / flute / horn for orchestral leads). 180 genres gained alternatives. Genre-defining sounds stay put: the 808 in trap / drill / phonk, the log drum in amapiano, the piano in Solo Piano.
- **Re-roll sounds.**
  - **🎲 Re-roll sounds** in the Sound panel picks a different suggested sound for every part. A 🎲 next to each part tries another one for that part, and **↺ Genre sounds** goes back.
  - **🎲 New sounds** on every result plays the exact same song on different sounds.
  - The song editor has the same re-roll, and its dropdowns list the genre's suggestions first.
- **The Sound panel is reorganised:** the part sounds come first, then drums & tone.
- **Drum kits for 28 more genres:** e.g. a brushed kit for folk jam and holiday, a big 80s kit for sophisti-pop, a dead 70s kit for psych pop, a rock kit for boogie rock and nu-metal, a vintage kit for surf and soul-sample rap, and a re-played funk break for 90s new-age chant.
- **Plugin hints:** band and folk genres no longer tell you to load a BBC orchestra violin for a fiddle. Piano parts point to a piano plugin.
- **The dubstep wobble is slower by default** (half-bar, beat and 8th-note wubs; 16ths only where a genre asks for them), and the fastest bass-house / bassline / riddim rates are toned down.
- Fix: a genre's own sound now always leads its list, even when it has several parts on the same layer (epic orchestral pads).

## 1.40.1
- **A better dubstep wobble bass.**
  - **Bigger tone:** a fat unison saw + square stack with a little FM grit.
  - **Movement:** a resonant filter sweeps exponentially, so each cycle says "wow", with a vowel formant riding along.
  - **Clean low end:** the bass is driven hard, then split above ~120 Hz so the clean sine sub underneath never pumps.
  - **LFO shapes:** smooth, saw ("WAAow"), choppy square or triangle, still synced to 8ths / 16ths / triplets / slow swells.
- New genre **Hard trance / hands-up**, built from your references: a pounding 909 at ~140, a rolling 16th bass on the root, hard supersaw / hoover riffs, acid, and short snare-roll breakdowns between long main sections.

## 1.40.0
- **Fixed: a pad that played smeared, off-beat notes.** When a slow, swelling sound (warm pad, string pad, choir) landed on a part that plays short chord stabs, the notes never reached full volume and rang on after the beat. Those parts now hold each chord from its beat until the chord changes.
- **Fixed: a click / "something before the kick" on Classic jungle breaks.** Recorded drum hits now have their pre-roll trimmed and short fades at both ends, kicks and break hits are never humanised (a layered kick no longer flams against the break), and reversed snares now swell into the beat and end on it.
- **Song editor.** Every result and every Library song has an ✏️ **Edit** button. It opens the song with its section timeline and **every sound playing in it**: main parts, extras, layers, the sounds of other sections, and build-up and fill drums. Change any of them or switch it off, then preview or render. The notes stay the same.
- **Open a past project by dropping it on the window**: its MP3 / WAV / MIDI / plugin guide or its `_settings.json`. It opens in the editor, or is rebuilt from its settings if the audio is gone.
- **The Sound panel also lists everything your last song used**, so every sound you hear can be found and changed.
- **31 new genres modelled on your reference tracks.** For each reference I measured bar by bar where the kick, sub, hats and keys come in and drop out, so the song forms, breakdowns and builds follow the records instead of a generic template:
  - bass house, minimal club pop, future garage, glitchy IDM pop, UK bass / 130, nu-disco / disco lounge
  - lo-fi bedroom rock, 90s new-age chant, mid-90s smooth rap, 80s sophisti-pop, early dubstep, acoustic folk-rock jam
  - garage-house pop, hard trap (brass & strings), wonky / beat-scene bass, experimental field ambient, late-90s trance-pop, West-coast slap rap
  - UK bassline, mid-fi synth-funk / chillwave, 90s Italo piano house, futuristic hip-hop bounce, soul-sample hip-hop, Tokyo deep house
  - psychedelic synth-pop, 80s boogie rock, grime, spooky 60s surf, nu-metal, beat-switch trap (with dead-silent bars between beats), mallet melodic house
- **Deep Dubstep follows its references more closely.**
  - It starts with an intro that has no kick.
  - The first section is long, and the 16-bar breakdown is half pads and half kick + sub.
  - The first drop rolls slowly; the second switches up to tight 8th / 16th bass movement.
- **Liquid DnB, melodic house and future bass now use song forms taken from your references.** Liquid DnB has a long intro with no kick and a drums-out lift before the drop. Melodic house has a long beatless intro, kick + sub without hats, and a long kick-out break.
- Genres can name their own build-ups and transitions. Many of the new ones build by taking things away instead of speeding up snare rolls.
- README: new screenshots, and short excerpts of eight genres to listen to.

## 1.39.1
- **Deep Dubstep rebuilt from your four reference tracks.**
  - The sub now sits on one note (the root, now and then the flat 2nd) for long stretches.
  - A mono mid-bass growls in strict 8ths and 16ths, or swells slowly.
  - Kick on 1, snare on 3, skippy percussion thrown into dub echoes, and a long drums-only intro.
  - Like the references, there are no snare-roll build-ups: the drop just lands, or everything stops for a beat first. Drops have no risers, reverse cymbals or impacts.
  - The mix is mono and sub-heavy.
- The previous Deep Dubstep is kept unchanged as **Deep Dubstep - sparse & eerie** (`deep_dubstep_minimal`).
- Genres can now name their own build-ups and transitions (`build_family`, `transition_moves`, `plain_drops`).
- New genre **UK road rap**, built from your reference: a dark half-time London rap beat at 146-156 BPM, with a huge mono 808 sub sliding between the root, the leading tone and the fifth, steady 8th hats with short rolls, sparse kicks, and a harmonic-minor piano line over low strings and choir, leaving room for the vocal.

## 1.39.0
- **No more ffmpeg / console windows popping up on Windows.** Every helper program (the MP3 encoder, the plugin worker, git updates, the Defender scan, sample-library tools) now runs hidden.
- **Build-ups you control.** A new **Build-ups** switch: On, Subtle (natural band-style lead-ins, no EDM ramps) or Off. A new **Transition FX** switch: Varied, Fewer, Drum fills only (no riser / cymbal / impact sounds) or Off (straight cuts). Both are saved with presets and available on the command line (`--builds`, `--transition-fx`).
- **More varied, more natural build-ups.** Ten new styles: groove + short fill, ride-cymbal crescendo, stop-time hits, marching snare, tom groove, mallet cymbal roll, kick pulse, noise wash, tape stop, and nothing at all. Each build in a song is now a different one, and snare and clap rolls ramp up in several different shapes instead of the same speed-up every time.
- **No more reverse cymbal before every chorus.** Each transition is now one of several lead-ins: a reverse cymbal, a mallet roll, a noise wash, a tape stop, a moment of silence, just a crash, or nothing. The same lead-in never comes twice in a row. Drops alternate between an impact and a falling noise sweep.
- **Better jungle and funk breaks.** Chops now keep the backbeat, because snare slices land on 2 and 4. There is a set of classic jungle re-edits, and phrase ends get snare rushes that rise in pitch, reversed snares, stutters and pitch-downs. The break also gets the 12-bit sampler grit, and its pitch rises with the tempo like a sped-up record.
- **Genres sorted into sub-groups** inside each tab (House & Disco, Techno & Trance, Dubstep & Bass, Drum & Bass / Breaks & Hard, Hip-Hop / Trap & Phonk, Jazz, Swing & Big Band, Country / Folk & Blues, Solo Piano, Classical Eras ...). Click a group header to collapse it. docs/GENRES.md is grouped the same way.
- New genre **Solo Piano Miniature**, built from your reference track: one soft, felt-muffled upright in wide close-mic stereo, a rocking 8th-note left hand swaying between two chords, and a plain singing melody, at about 78 BPM.
- New genre **Funky breaks / glitch electro**, built from your two references: a chopped, swung funk break at 122-132 BPM with edits, a rubbery sliding bass, a warped gliding lead, palm-muted guitar riffs doubled by the bass, and Rhodes stabs.

## 1.38.1
- **No more double-time genres.** Salsa was playing its whole two-bar clave inside one bar at 180 BPM - it now plays at the right speed (its patterns are written in cut time, so the tempo shows ~85-105). The hot tom-tom big band now sits around 100-120 BPM, swing 110-160, 50s big band 120-150, western swing 110-160.
- Bebop, soul jazz, modal jazz and both big bands now swing their eighth notes (they were swinging sixteenths).
- Checked every genre's tempo against its patterns: the fast ones are only the genres that are fast for real (drum & bass, jungle, breakcore, gabber, hardstyle, punk, metal, bebop, hopecore ...); dubstep, trap and similar keep their half-time feel.

## 1.38.0
**New genres from your reference tracks** (named for the style, not the artist):
- **Deep dubstep - rollers**: 140 half-time and steppers, a huge rolling sub, sparse skippy percussion into dub echoes, an optional squelchy acid line - mono and heavy.
- **Melodic deep house (sunny, piano & strings)**: warm 122-124 groove, shakers and congas, rolling melodic bass, bright piano, lush strings, long breakdowns.
- **90s club house (New York)**: swung 909 / sampled drums, tambourine, deep bass, short filtered minor chord stabs on the offbeats.
- **Bedroom / indie pop**: bouncy drum machine, warm synth bass, chorused clean guitar, bubbly plucks and bells, loud and dreamy.
- **80s electro-funk / boogie**: slow heavy DMX groove, big claps, Minimoog bass, poly-synth stabs, and a new **talk-box style synth** lead that glides.
- **Ambient beat (dark, sub-heavy)**: half-time drums tucked under washed-out pads, a long 808 sub, distant bells.
- **90s video game (PS1-era)**: sample-based breaks, slap/synth bass, ROM strings and brass stabs, all through a crunchy 22 kHz console sound.
- **90s alt rock**: jangly clean verses, distorted double-tracked power-chord choruses, pick bass, big dry room kit.
- **Jam-band rock (80s, upbeat)**: two drummers left and right, chiming rhythm guitar, melodic bass, 80s keys and organ, noodling lead and long solo jams.
- **Hopecore (euphoric breaks)** and **Hopecore (dreamy, slow)**.
- **Swing-era big band (hot, tom-tom)**: a fast 1930s minor-key flag-waver on the floor-tom groove, riffing brass, sax section, clarinet lead, a drum break and a shout chorus.
- **50s big band (brassy, smooth)**: a medium-up swinging major-key chart - walking bass, ride and hi-hat on 2 and 4, piano comping, sax section, trumpet and trombone hits building to a shout chorus.
- **Four more hauntology moods** (the original Hauntology is unchanged): *wobbly melody, slow beat* (a detuned synth tune drifting on tape over a dusty beat), *beatless tape lullaby* (quiet, muffled, no drums), *campfire guitar haze* (looping acoustic guitars over a loose 90 BPM beat) and *cold dystopian synths* (slow, stark, minor, cold analog arpeggios).
- Also **Soca / calypso** (steel pan, iron, brass hits), **Raga** (tanpura drone, sitar with meend, tabla; alap - jor - gat - jhala) and **Japanese zen** (koto, shakuhachi-style flute, taiko).

**Drum kits**
- **Drum & bass kits**: modern DnB layers a tight electronic two-step kick and a crisp snare over a break (the break's kick filtered so the layered kick owns the low end) - *Modern DnB (fast funk break)*, *jungle break rollers*, *Neurofunk* (hard, distorted, compressed break), *Liquid*, *Jungle* (raw jungle break, crisp piccolo snare) and a *DnB drum machine*. DnB, liquid, neurofunk and jungle now use them by default.
- Two more re-played breaks (**tight funk**, **heavy funk**) and five more drum machines: **CR-78**, **TR-606**, **TR-707**, **DMX** (8-bit) and a **distorted phonk 808** (old sample-based machines get their real bit depth and sample rate).
- Two more free real kits, **Karoryfer Unruly Drums** (a tight modern studio kit and a dirty one), and **Karoryfer Frankensnare** - real snares that replace a kit's own: a crisp steel piccolo (DnB), an ash piccolo (jungle), a dead muffled 70s snare (soft rock) and a huge one for a **Big 80s kit** with gated reverb. Both CC0, in 🎻 Real instruments.
- Every kit is in the drum kit menu; genres were assigned their natural kit (pop and modern country: modern studio kit, soft rock: dead 70s snare, acid house: 606, phonk: distorted 808, jazz rap: heavy funk).

**New free plugin: RipplerX** (GPL-3.0, official GitHub release zip): physically modelled marimba, vibes, kalimba, harp, music box, bells, tubular bells and gongs - used for those parts in any genre once installed from 🎚 Genre VSTs.

**Genres made more authentic**
- **Funk**: clavinet chords, 16th "chicken-scratch" muted guitar, horn stabs on the accents only.
- **Bluegrass**: Scruggs banjo rolls with the drone string, the **mandolin chop** on 2 and 4, boom-chick guitar with **G-runs**, and the band taking **breaks in turn** (banjo, mandolin, fiddle, guitar).
- **Celtic jig**: AABB tune form, **bodhrán**, **tin whistle** doubling the fiddle, a soft pipe drone.
- **Tango**: A-B-A form, the 3-3-2 síncopa in piano and bass, the chan-chan ending.
- **City pop**: its own syncopated finger-bass lines. **Bossa nova**: the batida guitar figure.
- **Techno**: the modern **rumble** (kick into a dark reverb, ducked) and slow filter sweeps over 16-32 bars.
- **Synthwave**: 80s song form with a **sax / guitar solo**, tom fills. **Reggaeton**: dembow variations, nylon guitar riff, 808 slides.
- **G-funk**: the high gliding **whine** lead. **Drum & bass**: the reese bass now slowly moves.
- **Salsa**: son form with montuno and **mambo** horn section, the anticipated **tumbao** bass, **timbales** and paila.
- **Ambient**: **tape loops of different lengths** that drift against each other. **Lo-fi / boom bap**: chords **chopped like a sampled record**, sampler grit, ducked under the kick.
- New instruments: mandolin, tin whistle, uilleann pipes, pipe drones, sitar, tanpura, koto, bodhrán, timbales, tabla.
- Genres with a designed kit (hardstyle, gabber, deep dubstep ...) no longer have it randomly swapped for another kit, and ensemble genres keep each instrument on its own part.

**App**
- **Every part is customizable**: the Sound panel now also lists each genre's extra parts (horn stabs, a second guitar, the tin whistle, solo instruments ...) - change their sound or switch them off. A genre's extra parts keep their own sound instead of being reshuffled.
- The **Parts** panel is gone: each sound has a small **mute** box next to it (and kick / snare / hats / FX next to the drum kit).
- The window no longer scrolls away from the editor when you turn a knob or press a key - the page itself is locked; only the columns scroll.

## 1.37.0
- **Fixed: the app did not start on Python 3.9, 3.10 or 3.11** (one line of the DAW export used syntax only Python 3.12 understands). The tests now also run on Python 3.9.
- The Windows and Mac start files say clearly when Python is missing or too old (with the download link) instead of failing silently; so does the app itself when it is started without a console window.
- **🔁 Loop it** in the section editor: up to 8 bars of a section, repeating seamlessly (the reverb tail wraps round to the start), to listen while trying new takes or sounds.
- Bassoon and contrabassoon parts in the Cinematic Journey now each pick their own saved sound (a "contrabassoon" sound was being chosen for the normal bassoon part).
- Under the hood (no change to how anything sounds - verified note-for-note on every genre): every genre is now defined in one place in `styles.py` (instrument pools and menu names included) instead of being patched again in later sections; `compose.py` is split into `theory.py`, `figures.py`, `arrange.py` and `windows.py`.
- New feature tests (metal riffs, key-tuned hard kicks, classical forms and cadences, montuno, Leslie / amp / dub delay, seamless loops); CI runs the test suites in parallel, adds a lint check and a Python 3.9 job.
- README: genres, real instruments, all the plugins (Dragonfly Reverb, Airwindows), the loop button and a short developer guide.

## 1.36.0
The genres that needed the most work (everything except vocals):
- **Metal, symphonic metal, punk**: real riffs instead of strummed chords - palm-muted chugs, gallops, ringing power chords and the metal riff notes (b2, minor 3rd, tritone), with the bass doubling the riff. Choruses switch to driving open power chords. A new **high-gain amp** (boost, two clipping stages, scooped mids, 4x12 cab, slightly different left / right like a double-tracked guitar) on both the synth and the recorded guitar; double-kick and gallop kick patterns.
- **Hardstyle / gabber**: a proper **hard dance kick** - punchy click over a long distorted body that is **tuned to the song's key** (hardstyle) or clipped nearly square (gabber). Hardstyle's reverse bass now swells between the kicks.
- **Psytrance**: short, tight, key-tuned kick and a clipped rolling 16th bass with no sidechain pumping (the bass sits between the kicks).
- **Rave hardcore**: rave stabs instead of the vocal-synth arp.
- **Reggae / ska / dancehall**: **dub mixing** - the snare, rim, skank and melody get "thrown" into a tape echo at phrase ends (band-limited repeats that darken and saturate), plus a **spring reverb** tank.
- **Hammond organs** now go through a modelled **Leslie** rotary speaker (horn + drum rotor, doppler and swirl, tube growl): fast for gospel, soul jazz, funk and jam band; slow "chorale" for rock, blues, soul ballads, reggae.
- **House**: a new **M1-style house piano** (the bright, glassy 90s piano-house sound) for chords and piano riffs.
- **Tech house**: rolling, interlocking percussion - bongos, congas, tambourine, rim shots and accented shakers.
- **Vaporwave**: slower, sampler grit (SP-1200 style), chorused Rhodes, heavier tape warble, darker top.
- **Salsa**: a real **piano montuno** (syncopated chord tones in octaves, alternating with the clave) and horn hits. **Afrobeats**: highlife-style picked guitar patterns over Rhodes. **Tango**: a new **bandoneon**.
- **Rebuilt instruments**: accordion (three reeds, musette beating, bellows push), banjo (metal fingerpick, drum-head resonances), pedal steel (volume-pedal swell, bar slides, glassy pickup), and the amapiano **log drum** (hollow tuned knock that drops in pitch, closing filter, glides).
- **Classical genres are written in real forms**: Baroque - binary dance form (with ornamented repeats) or a Baroque prelude; Classical period - **theme & variations** (ornamented, Alberti, theme in the bass, tutti) or a compact **sonata form**; Romantic - a lyric slow movement (the theme sinks to the celli, then climaxes); Impressionism - an arch form with harp shimmer. Sections end on written-out V-I cadences with the melody landing on the tonic.
- **New genre: Minuet & trio** (3/4): minuet, ornamented repeat, trio, minuet da capo.

## 1.35.1
Genre VSTs downloads fixed:
- **"Microsoft Defender found a threat: CmdTool: Failed with hr = 0x80004005" was wrong**: that message means Defender's scanner couldn't run (usually Defender is switched off or another antivirus is in charge) - it never found anything. Studio Lab read it as a threat and refused every plugin. A scan that can't run is now reported as "could not scan - not a threat" and the install continues with the other checks (checksum, and VirusTotal if you set it up). Only a real detection (exit code 2 / "found N threats") blocks an install.
- **Airwindows downloaded the ARM build** ("Windows-arm64ec.zip") on normal PCs; ARM builds are now never picked on x64.
- **Removed from the download list: Six Sines, Monique, OB-Xf and Odin 2** - no genre actually played them (no sounds were written for them). If you installed them, they show as "retired" with a Remove button.

## 1.35.0
- **Three more free real drum kits** in 🎻 Real instruments (CC0, Karoryfer Samples - same checked download as the others), each in the Kit menu and the default for the genres it suits:
  - **70s soul / funk kit** (Gogodze Phu Vol II, 28 MB): dry and warm, recorded to sound like early-70s records - funk, Motown, soul jazz, blues, reggae, disco-funk, gospel.
  - **Jazz brushes kit** (Swirly Drums, 15 MB): played with brushes - jazz, swing, bebop, modal jazz, bossa nova, soul ballads, quiet storm, country waltz, western swing.
  - **Big vintage rock kit** (Big Rusty Drums, 6 MB): an oversized 1980s kit with a 24" kick - rock, indie, punk, jam band.
  - A kit without cymbals (the 70s kit) borrows the studio kit's.

## 1.34.1
Drums no longer sound clipped:
- **Drum bus**: its glue compression and saturation used to depend on how loud the drums arrived - and they arrived 6-9 dB too hot, so every kick and snare was flattened by 2-3 dB (up to 6 dB in trap). It now works at a fixed level, compresses gently above the kit's own average with a slower attack, and only rounds the very top of a peak: hits keep their punch (about 0.5 dB lost instead of 2-3).
- **Master limiter**: it was cutting drum peaks by 4-11 dB (up to 17 dB, and limiting half the time in phonk / hardstyle) to reach the loudness targets. It's now capped at ~3 dB on the loud peaks, rare extreme peaks are rounded off sample-by-sample first, and limiting happens about 1% of the time. Songs come out 1-2 LUFS quieter than before instead of distorted.
- Every drum sound now fades over its last few milliseconds, so none can end on a click (the "hard" kit kick and the 8-bit kick did).

## 1.34.0
Dubstep, more authentic:
- **Dubstep (classic UK)**: dark chord stabs and horror-movie bells over the wobble and sub (the soft synth lead is gone).
- **Brostep**: a new **screech bass** (high, harsh FM with a whine-up bend and sweeping formant - the Skrillex sound); the drop now trades growl -> wobble -> growl -> screech, with a supersaw lead for the breakdowns (no more rave hoover or 8-bit sounds).
- **Melodic Dubstep**: reese / growl / wobble basses under supersaw leads (no plain saw bass or vocal-synth lead).
- **New: Riddim** - a new **riddim bass** (hollow square / saw, hard tempo-synced triplet chops, own sub) repeating its 2-bar phrase over sparse half-time drums and a creepy bell.
- **New: Chillstep** - slow half-time at 140, lush reverb pads, piano, delayed plucks and a gentle rolling wobble.
- Each wobble genre can now set its own wobble rates (riddim chops in triplets, chillstep rolls slowly).
- All dubstep styles keep their signature sounds instead of the variety setting swapping them.

## 1.33.0
House & trance with their real sounds:
- **House**: the bouncy **M1-style organ bass** (new sound, the 90s NYC / Robin S bass), offbeat **piano** stabs (real Steinway), organ hits, warm pads - instead of a saw bass, supersaw pad and plucks.
- **Tech house**: a rolling, rubbery filtered saw bass and percussive chord stabs.
- **Trance / uplifting / progressive trance**: gated warm pads (the trance gate in the drops) instead of a string ensemble.
- **Brighter, wider supersaw** (JP-8000 style: seven saws spread wider, a stronger centre voice, brighter and high-passed) - trance, progressive house, big room, future bass and everything else that uses it.
- House, deep / tech / progressive / melodic house, acid house, all trance styles, techno, melodic techno and big room now keep their signature sounds instead of the variety setting swapping them, and section rotation only uses each genre's own sounds (no more 8-bit pulse in a progressive house break).
- **Report a problem → 📋 Copy synth parameter list**: lists the knobs of the genre synths you have installed (OB-Xf, Odin 2, Monique, Six Sines, Surge XT, Dexed, Vital ...) so genre presets can be written for your exact plugins.

## 1.32.1
- **Vinyl crackle is off by default** in every genre (lo-fi, boom bap, hauntology, vaporwave ...). Switch it on any time with Mix & master → Vinyl crackle → On. The tape wobble and dusty tone of those genres stay.

## 1.32.0
Rap, hip-hop & R&B, round two - plus Airwindows:
- **Sampler grit**: Boom Bap, Lo-fi, Memphis Phonk and the new Jazz Rap run their loops (chords, melody, pads) through an SP-1200-style stage - 26 kHz sample-and-hold, 12-bit grain and the dull top end - so they sound sampled off a record instead of played.
- **808s**: kept in the real sub register (E1 ... A2, slides included) instead of drifting up into the mids, with a longer, more audible trap slide.
- **New genres**: **Jazz Rap** (A Tribe Called Quest / Nujabes: dusty swung break, real upright walking under jazzy Rhodes, vibes and muted-trumpet phrases), **Cloud Rap** (Clams Casino / Yung Lean: washed-out reverb pads, choir haze, bells drowned in echo, soft 808), **90s R&B Slow Jam** (Jodeci / Boyz II Men: DX e-piano 9ths, finger snaps, deep sub, strings, clean guitar).
- **Airwindows Consolidated** (MIT, 500+ effects - tape, console, saturation, lo-fi, reverbs) is a new Genre VSTs pack, downloaded from its official GitHub release (the zip, never the installer) with the usual checks. Pick it as a part effect in Sound.

## 1.31.0
Every genre checked against the new real instruments:
- **Two new free real-bass libraries** in 🎻 Real instruments (CC0, Karoryfer Samples): **Electric bass** (Growlybass, a Squier Jazz bass, sustained + staccato, 46 MB) and **Upright double bass** (Meatbass, pizzicato, 29 MB).
  - 24 genres that played a generic "plucked string" synth bass now play the real electric bass (rock, metal, punk, funk, disco, Motown, blues, ska, soul, gospel, pop, fusion ...); jazz, swing, bossa nova, bluegrass, folk, Celtic, western, salsa and chamber pop get the upright. Every upright / acoustic-bass part in any genre uses the real one.
- **Real electric guitar everywhere**: every synth "electric guitar" / palm-muted guitar part (~45 genres - funk, reggae, Motown, R&B, jazz, city pop, afrobeats, cumbia ...) now plays the real twang guitar when it's installed; parts that were distorted (rock, metal, punk, blues and indie leads) go through a new **guitar amp + cabinet** stage. Bossa nova, Celtic jig, soft rock and holiday strum the real acoustic.
- **No more robotic "vox" synth** except in genres built on vocal chops (UK garage, future bass, Jersey club, baile funk, the phonk family, future funk, rave, melodic dubstep, hyperpop). Elsewhere (deep house, tech house, dubstep, jungle, afrobeats, dancehall, K-pop, teen pop, liquid DnB, new beat ...) it's replaced by the genre's own lead.

## 1.30.1
- **Smooth Jazz now has a soaring soprano sax**: a new **Soprano sax** sound soaring up high in long held notes with a delayed, widening vibrato and scoops into every phrase, over lush 80s DX electric piano and pads, fretless-style bass and soft reverb-washed drums; slow ballad tempos, romantic major-key progressions and a key change for the last chorus in most songs. The sax stays a soloist (no doubling).
- New expressive vibrato for held notes on recorded instruments (used by the soprano sax).

## 1.30.0
- **Smooth jazz**, three new genres (Classic tab):
  - **Smooth Jazz**: the real tenor sax scooping into its notes over Rhodes 9th / major-7th chords, fretless-style bass, cross-stick drums, soft pads and the real acoustic guitar.
  - **Smooth Jazz-Funk** (Grover Washington Jr., George Benson, Spyro Gyra): slap bass groove, jazz-guitar melody in octaves, sax answers, electric piano and brass.
  - **Quiet Storm** (Sade, Luther, late-night radio): slow and intimate - soft Rhodes, breathy sax, fretless bass, brushed snare, swelling strings.
  - They stay on jazz progressions (ii-V-I, I-vi-ii-V, iv-VII-III ...) instead of borrowing generic pop ones.

## 1.29.0
Real guitars, real slides, more harmonica:
- **Two new free real-guitar libraries** in 🎻 Real instruments (CC0 public domain, Karoryfer Samples, same download safety as the others):
  - *Acoustic guitar* (Shinyguitar, microphone recording, 56 MB): the strummed and picked acoustic in Country, Modern Country, Country Waltz, Bluegrass and Folk.
  - *Twang electric guitar* (Black And Green Guitars, 157 MB): real "twang" picking plus staccato for chicken-pickin' - the country lead and fills in Country, Modern Country and Outlaw Country.
  - Both show up as "Acoustic guitar (real)" / "Twang electric guitar (real)" in every Sound dropdown.
- **Real slides and bends**: country melodies now actually glide up into their notes (a whole or half step), on the recorded fiddle, harmonica and guitar as well as the synths - instead of a separate grace note.
- **More harmonica**: harmonica answers the melody in Outlaw Country (and sometimes Country), alongside the pedal steel.
- Country styles no longer fall back to the General MIDI steel guitar or the synth "electric guitar" for their acoustic parts.

## 1.28.0
Country, made authentic - and four more country styles:
- **Country (classic / honky-tonk)** reworked: upright bass in a boom-chick with walk-ups (was a generic pluck), strummed acoustic with **honky-tonk piano** (a detuned piano, an octave up) doubling it, **chicken-pickin' Telecaster** fills (new "Telecaster twang" sound), real fiddle on the melody, pedal steel swells and pedal-steel answers.
- **Slides**: country melodies now slide up into their longer notes from a step below - the fiddle / steel / Telecaster inflection that makes it sound country.
- **New styles**: **Modern Country** (Nashville pop: big drums, 16th acoustic strum, Telecaster riffs, steel), **Country Waltz** (3/4 Tennessee-waltz: oom-pah-pah, weeping fiddle and steel), **Outlaw Country** (Johnny Cash / Waylon freight-train boom-chicka-boom, palm-muted guitar, slapback baritone twang, harmonica), **Western Swing** (Bob Wills: swung dance band, twin fiddles, steel, sixth-chord piano, walking bass).
- Country genres keep their signature sounds (fiddle, steel, twang) instead of the variety setting swapping them out.
- New sound for any part: **Telecaster twang guitar**.

## 1.27.0
Rap, hip-hop and R&B overhaul, plus Boards of Canada-style hauntology:
- **Fixed sounds**: Boom Bap's melody is a jazzy sax/flute/horn line (was a synth string pad) over sine bass doubled by upright; R&B's lead is clean guitar (was a robotic vowel synth); Trap's chords are dark piano (was a pluck). The vowel-synth "vox" is gone from Trap and R&B pools.
- **Signature sounds stay put**: in rap / hip-hop / R&B genres the variety setting now keeps each genre's own sound most of the time (it used to swap it ~75% of the time), section rotation leaves the lead/hook alone, and Boom Bap no longer pulls in orchestral strings, horns or harp.
- When a bell has to be replaced, a genre now gets its own sound for that part instead of a generic category synth (no more random saw leads in trap).
- **New genres**: G-Funk (West Coast), Neo-Soul, New Jack Swing / 90s R&B, Alternative R&B (dark), Rage, Plugg / Pluggnb.
- **Hauntology II (sunlit tape)** and **Hauntology III (dark film haze)**: Boards of Canada-inspired variations. The original Hauntology is unchanged.
- **Every Sound dropdown now lists every sound**: the ones that suit the part first, then "Other built-in sounds (any part)" and "Other real instruments (any part)".

## 1.26.0
- **Every song has a name**, at the front of every exported file before the technical tag - e.g. `Ashes-of-the-North_cinematic_journey_D-minor_88bpm_seed3.mp3` (MP3, WAV, MIDI, parts, stems, DAW packs, settings and guides).
  - Type your own in **Basics → Song name**, or leave it empty for an invented name that fits the genre and mood (the same settings always give the same name, so a preview and its full song match).
  - The name is also written into the MP3's title tag and the MIDI file's title, and shown on each result card and in the Library.

## 1.25.0
- **🎬 Cinematic Journey - Dark & Low**, a second mode next to the original (top of the Orchestral tab): the same story, acts, presets and controls, told from the bottom of the orchestra. Celli carry the theme (trombones double it at the big moments), bassoons replace flute and oboe, the violins drop to their low string and the high harmonics are gone, piano notes get deep octaves underneath, every bass note is thickened by contrabassoon and tuba, low brass / timpani / bass drum hit harder, the choir sings a dark "ooh", tempo sits a little slower (72-86) and the mix leans on the low end with the top rolled off.

## 1.24.1
- Cinematic Journey: the climax's violins were written an octave too high (up to A7, a thin whistle). They now sing in their bright upper register with the violas an octave below, the high "harmonics" strings and woodwinds sit lower too, and every part is kept inside its instrument's natural range.
- Each Journey player's Sound dropdown has **🔇 Off (silent)** to leave that instrument out.

## 1.24.0
Cinematic Journey, more epic:
- **Key change in the climax**: the second half of Glory lifts a whole step (switchable).
- **Grand pause**: a suspended-cymbal roll swells to the edge, one beat of total silence (just the hall ringing), then the climax hits with everything.
- **Choir**: "ooh" entering under the second half of Resolve, full "aah" in Glory, a held "ooh" in the final chord (your orchestra plugin's choir if you saved one, otherwise the General MIDI or built-in choir).
- **Brass rips** into the climax's phrases and **trombone falls** at their ends; trombone marcato hits are now their own part.
- **Deeper low end**: contrabassoon and contrabass trombone under the tuba; optional **hybrid sub booms**.
- **Harp glissandi** sweeping into the Resolve, out of the grand pause and down into the Reflection; **suspended-cymbal swells** into each act.
- **Theme development**: the trombones foreshadow the theme (twice as slow, pianissimo) in Tension; in Resolve the horns answer the violins in canon.
- **New Battle act** (optional, between Resolve and Glory): spiccato strings, staccato brass, the theme as a battle cry, taiko, snare rolls, anvils, timpani.
- **Climax style**: Concert hall or Trailer (adds the taiko ensemble, snare rolls and anvils).
- **Story presets**: Hero's journey, Tragedy (no glory, dark ending), Triumph (short tension, long trailer climax), Elegy (piano, strings, reflection).
- **Every player has its own Sound dropdown** for the Journey (25 parts: violins I, violas, celli, basses, each horn/brass/woodwind section, harp, choir, timpani ...), so nothing is locked.
- **BBC SO articulations**: new sections in Set up my orchestra (violins legato, violas, basses, trombones, low brass marcato, tuba, bassoon) - each passage uses the matching patch.
- The Journey card shows whether the Dragonfly concert-hall reverb is installed.

## 1.23.0
- **🎬 Cinematic Journey - the ultimate orchestral generator** (top of the Orchestral tab). A through-composed score for full symphony orchestra and solo piano, written act by act instead of from loops:
  - **Tension**: double basses on a dark pedal, celli (then violas) in muted creeping ostinatos, soft timpani rolls, icy notes at the bottom of the piano, a barely-there tremolo.
  - **Sorrow**: the solo piano sings the song's theme (with "sighing" appoggiaturas) over soft-vibrato string pads and gentle horn swells; octaves the second time.
  - **Resolve**: violins and violas take the theme in long legato, spiccato ostinatos and rising scalar runs drive forward, horns in noble lines, trumpets join, trombones and tuba alternate weighty chords with short marcato statements, a timpani roll throws the door open.
  - **Glory**: massive tutti - violins high, violas, celli and horns on the theme, trumpet fanfares, sforzando low brass, thundering timpani, bass drum and cymbals, cascading piano arpeggios, flute/oboe counter-melody and high string harmonics.
  - **Reflection**: the piano alone again over high shimmering strings and distant soft brass. **Resolution**: full strings and warm low brass hold one long, luminous (bittersweet major or dark minor) chord that fades into silence.
  - **Tempo follows the story** (78-92 BPM base): accelerando into the climax, a held breath before it, allargando at its end, a long final ritardando - plus adjustable phrase rubato. MIDI export carries every tempo change.
  - **Dynamics from near-silence to fortissimo**, also sent as mod-wheel (CC1) curves when an orchestra plugin plays it.
  - Every part is its own section/articulation (violins, violas, celli, basses, sustain, tremolo, spiccato, horns, trumpets, trombones, tuba, flute, oboe, clarinet, timpani, piano), so the free real orchestra plays all of them - or your **BBC Symphony Orchestra** sections, with one tick in the Journey card.
  - Controls: which acts to include, piano focus, rubato, dynamic range, final chord, woodwind counter-melodies. Length (Short ... Extended) and seed work as usual.
- **Report a problem → 📋 Copy technical summary**: one short block with versions, libraries, failed jobs with their settings and errors, Python tracebacks and the end of the log - ready to paste into a chat. Same privacy rules as the full report.
- Finished songs no longer end with long dead silence (more than 2.5 s after the last sound is trimmed with a fade).

## 1.22.0
- **No more long silent intros**: the finished mix now starts at most 1 second before the music is audible (very quiet fade-ins and empty bars are trimmed with a short fade). Stems and MIDI keep the full timeline.
- **Five new SUPER EPIC orchestral genres** (Orchestral tab): *Epic Orchestral*, *Epic Battle*, *Epic Choir*, *Heroic Anthem* and *Symphonic Finale*. Every one stacks the full low end - double basses, celli an octave up, trombones/tuba under the horns - with taiko, timpani, orchestral crashes, choir and soaring violins. They use the real orchestra (or your orchestra plugin) when installed.
- **New orchestral section sounds** in the Sound dropdowns: violins (section), violas, double basses, trombones, tuba, bassoon, tubular bells.
- **Tempa Dubstep is now "Deep Dubstep (dark, minimal)"**: proper 140 BPM half-time - kick on 1, snare+clap on 3, shuffled rims and shakers with dub delay, sub-heavy sine bass with wobble, sparse stabs, 16-bar intros, 32-bar drops, a breakdown and second drop. Old saved settings using the old name still work.

## 1.21.0
- **Two new free real-instrument libraries** (🎻 Real instruments, CC0 / public domain, Versilian Community Sample Library):
  - *Pianos & keys* (433 MB): a **Steinway grand piano** that now plays every genre's piano part, a **Yamaha upright** for lo-fi, boom bap, blues, soul and other vintage styles, a Flemish **harpsichord**, a **pipe organ** for baroque and film styles, and a Yamaha TX81Z FM piano.
  - *Harp, mallets, sax & more* (398 MB): **concert harp, marimba, vibraphone, xylophone, glockenspiel, tubular bells, kalimba, tenor sax** (sustain + staccato), **harmonica, ocarina** and **sleigh bells** - used automatically wherever a genre plays them, and all selectable in the Sound dropdowns.
- **Dragonfly Reverb** (GPL-3, Michael Willis) is a new Genre VSTs pack - same safety checks as the others (official GitHub release, checksum, Defender, VirusTotal, no installers). When it's installed, each genre's reverb runs through the right one: **hall** for orchestral, trance, ambient and other big spaces, **plate** for pop, soul, R&B and the 80s styles, **room** for rock, funk, jazz, boom bap and acoustic bands. Level-matched to the built-in reverb, which is still used if the plugin ever fails.
- **CHOW Tape Model and BYOD** are recognised: they're only offered with installers (which Studio Lab never runs), so install them yourself from chowdsp.com and pick them as part effects.
- Plugin effects can now be given settings (used for the genre reverbs).

## 1.20.0
Every genre checked against the full Studio Lab genre bible (all 114). Most already matched; these changed:
- **Salsa** gets the real Afro-Cuban section: clave on claves, bongó martillo, güiro, timbale cáscara and a campana (real recordings when the percussion library is installed). **Cumbia** gets its guira scrape.
- **Hardstyle** plays a real reverse bass: a swell into each off-beat after the kick, cut dead before the next one.
- **Acid house**: the overdriven 303 is the lead too, rave stabs instead of organ, a dry raw mix.
- **Dark UK dubstep**: sparse vocal / soft leads instead of festival hoovers, a less aggressive kit.
- **Downtempo** keeps its glassy bells; **deep house** plays warm Rhodes / organ 7th-9th chords; **baile funk** gets distorted drums and a louder, rawer master.
- **Braindance / IDM** plays a heavily chopped Fast funk break; **country** has a train-beat snare.
- **Chorus** (Juno / Rhodes style) on Italo disco, synth-pop, synthwave, city pop, fusion, vaporwave and R&B keys.
- **Classical feel**: limited vibrato in Baroque, rubato in film piano, neoclassical and chamber; ambient gets tape drift; spaghetti western can use a whistled lead.

## 1.19.2
- **Pick individual orchestra instruments.** With the free real orchestra installed, every part's Sound dropdown has a "Real orchestra (no setup)" group with 19 instruments: violins, violas, cellos and double basses as sections, a solo violin, the whole string section as sustain / spiccato / pizzicato / tremolo, French horn, trumpet, trombone, tuba, a brass section, flute, piccolo, oboe, clarinet and bassoon. The VST window lists them too.
- The VST window explains why BBC Symphony Orchestra / LABS appear as a single plugin: they keep their instruments in their own browser and don't expose them to other programs.

## 1.19.1
- **The classic phonk cowbell is back.** The phonk lead no longer has forced overdrive, bit-crushing or an added echo on it: by default it's the classic pitched 808 cowbell with light saturation. Each song picks from five cowbells - classic (most often), raw 808 (dry, short), long ring (sustained with a slight chorus), distorted and crushed - and you can choose any of them as the Lead instrument.

## 1.19.0
- **🩺 Report a problem** (header button): saves one text file - or copies it to the clipboard - with Studio Lab's version, Python / OS and library versions, your settings, sound libraries, every plugin found and why any failed to load, the genre VST packs, recent songs and installs with their errors and warnings, and the recent log. API keys, your user name, home folder and e-mail addresses are removed automatically. Add a note about what happened and send the file for help.
- **Everything the app prints is now kept in `logs/studiolab.log`** (rotates at 2 MB), so errors are still there after the window closes.
- **Studio Lab opens in its own app window** - no browser tabs or address bar - using Microsoft Edge / Chrome app mode (part of Windows, nothing to install), or a native window if `pywebview` is installed. Closing the window quits Studio Lab. On Windows the launcher no longer leaves a console window open. Prefer a browser tab? Report a problem → App window → Browser tab, or start with `--browser`.
- **Create desktop shortcut** (Report a problem window): a Studio Lab shortcut that starts the app with no console.
- **Genre list:** `docs/GENRES.md` lists all 114 genres by category with id, tempo range and current description (`python tools/genre_list.py` regenerates it).

## 1.18.1
- **A real orchestra with no setup.** When the free Strings and Brass & woodwinds libraries (🎻 Real instruments) are installed, they play every orchestral part automatically - no plugin, no saving sounds per section. Your orchestra plugin (BBC Symphony Orchestra, LABS ...) is only used if you tick "use my orchestra plugin instead" in VST instruments. Songs whose orchestral parts fell back to General MIDI now point to the one-click download instead of the plugin setup.

## 1.18.0
Genres checked against the electronic and multi-genre production bibles (tempo, feel, rhythm grid, sound, arrangement).
- **13 new genres:**
  - *Electronic:* Italo Disco (LinnDrum-style kit with a gated-reverb snare, octave synth bass, Juno/DX7-style arps), New Beat (slow, stomping 100-115 BPM EBM/acid), Hardcore / Gabber (170-195 BPM distorted pitched kicks, hoovers), Breakbeat Hardcore / Rave (Classic jungle breaks over a 4/4 kick, piano stabs, hoovers), Future Funk (swung disco groove, heavy sidechain, vocal chops, slap-style bass).
  - *Jazz:* Bebop (180-260 BPM, rapid ii-V changes, bebop lines, rootless comping), Cool / Modal Jazz (long stretches on one mode, space, muted trumpet), Soul Jazz / Hard Bop (organ trio), Jazz Fusion (straight 16ths, electric bass, Rhodes, synth and overdriven guitar).
  - *Classical:* Classical period (melody over Alberti bass, 4+4 phrases, horns, timpani), Romantic Orchestra (rubato, rich chromatic harmony, horns, swelling dynamics), Impressionism (lydian / modal colours, harp, flute, piano washes, flexible pulse), Minimalism (steady pulse, repeating marimba / piano cells, slow harmony).
- **New musical behaviour:** Alberti-bass accompaniment; jazz snare comping ("dropping bombs") in Bebop, Modal, Jazz and Swing; Romantic rubato (phrases push, then broaden into the cadence); the 80s **gated-reverb snare** on the LinnDrum-style kit (synthwave, synthpop, city pop, Italo); a real campana cowbell for salsa and cumbia when the percussion library is installed.
- **Fixes to existing genres:** house 120-127 BPM with moderate (not pumping) sidechain and conga fills; deep house and psytrance now flow continuously instead of build → drop, deep house with gentler sidechain; progressive house gets long evolving builds and strip-down breakdowns; uplifting trance 134-140, psytrance 140-148, big room 126-130, synthwave 90-112; jungle swings harder; the reggae skank sits on every "and".

## 1.17.0
- **Every genre has its own drum kit, and you can switch kits** (Sound → Drum kit, grouped):
  - *Drum machines:* TR-808 (rap, trap, drill), TR-909 (house), Trance 909 (rolling kick, open hats), Techno 909 (hard, rumble), 80s LinnDrum-style (synthwave, synthpop, city pop), punchy EDM, hardstyle, soft.
  - *Real kits* (from the free drum library): studio, **rock (big room - new mic: 🎻 Real instruments → Update, +51 MB)**, vintage lo-fi.
  - *Re-played breaks:* jungle-style (jungle, DnB, breakcore - chopped and re-sequenced jungle-style), fast funk (liquid DnB), laid-back funk (boom bap), bongo funk, swung soul-shuffle shuffle (downtempo, trip-hop), big-room rock big room. These are the classic drum *patterns* played on the real kit (tuned like a sped-up record where the genre does that), not copies of the original recordings - so the songs stay yours. To use a break recording you own, load its hits under My sounds and tick "my samples".
  - Genre defaults: jungle/DnB → jungle break, liquid → fast funk break, boom bap → laid-back funk break, downtempo → soul-shuffle groove, lo-fi/vaporwave → vintage, trap/drill/rap/reggaeton → 808, house → 909, techno → Techno 909, trance → Trance 909, rock/metal/punk/indie → rock kit, funk/disco/soul/jazz/pop → studio kit, synthwave → LinnDrum-style. The result card shows which kit played.
- **Far fewer bells.** Bell, celesta, glockenspiel and music-box sounds now only appear in genres where they're idiomatic (trap melodies, film & orchestral, holiday, fantasy, horror, braindance); marimba / kalimba / vibes / steel drum only in afro, latin, jazz, bossa, lo-fi and organic styles - and even there only occasionally unless they're the genre's own sound. Everywhere else the part plays the genre's proper sound (trance: gated saw pluck arps and a supersaw lead; techno: stabs; DnB/jungle: rave stabs; garage: organ ...). An instrument you pick yourself is always kept.
- **Trance sounds like trance:** a new 9-voice supersaw lead with an octave-down layer, a filter that opens on every note and delayed vibrato; bigger hall reverb and dotted-8th delay on lead and arps; the classic 16th-note trance gate on the pad during drops (breakdowns stay open).
- **Genre fixes from an audit of all 101 genres:** trap now uses an 808 kit (it used the generic one); disco and funk play an electric bass instead of a synth saw; metal, punk and rock never rotate in pianos or synths; ambient never gets a gritty FM bass.

## 1.16.0
- **Real instrument libraries** (🎻 Real instruments): free, multi-sampled recordings that replace the General MIDI sounds wherever a genre uses them:
  - *Orchestral strings* (537 MB) - violin, viola, cello and bass sections with sustain, spiccato, pizzicato and tremolo, plus a solo violin. Each note comes from the section that plays that register, and violins/violas are doubled an octave down by the section below for real ensemble weight.
  - *Brass, woodwinds & timpani* (406 MB) - French horn, trumpet, trombone, tuba, flute, oboe, clarinet, bassoon, piccolo (sustain + staccato), timpani. "Brass" parts play a real section split by register.
  - *Percussion* (33 MB) - real congas, bongos, shakers, tambourine, claps, cowbell, claves, guiro, woodblock, triangle, cabasa - used in every genre that has them.
  - *Acoustic drum kits* (78 MB) - Virtuosity Drums, a real kit (kick, snare, cross-stick, rimshot, hats, ride, crash, toms) with a clean studio sound and a vintage lo-fi mic used by lo-fi / boom-bap. Used by funk, disco, rock, jazz, soul and other acoustic styles.
  - Every note uses the nearest recorded pitch, a velocity layer that matches how hard it's played and a different round-robin take each time; short notes switch to spiccato / staccato automatically.
  - All CC0 / public domain (Versilian Studios), downloaded from the official GitHub repos at a fixed version; every file must match its published git checksum, and only audio is stored. Songs made with them are entirely yours.
- **Build-ups don't all sound the same any more.** Each genre now has a family of fitting build-ups and every song - and every build inside a song - picks a different one. Five new build types that aren't snare rolls: accelerating hats, clap build, tom run, half-time-then-snap, and drums-out (riser and filter only). Band, pop and film styles never get EDM risers.
- **Fills into choruses and drops vary too** in electronic genres: snare fill, tom fill, hat roll, a clap flam, or a one-beat silence.
- **Vinyl crackle setting** (Sound → Vinyl crackle: genre default / off / on; `--vinyl on|off`). Phonk no longer has vinyl crackle by default.

## 1.15.0
- **Phonk rebuilt to sound like real phonk:**
  - *Drift Phonk* now runs at 145-165 BPM (was 135-155) with dark, root-heavy minor / phrygian / harmonic-minor harmony instead of moving chord progressions.
  - The lead is a **heavily distorted pitched 808 cowbell** (overdriven and lightly bit-crushed so it cuts like a synth lead) playing a short **3-7 note riff on loop**, in the low register real phonk uses.
  - Clipped, growling 808s that sustain, with lighter sidechain so the low end stays dominant; looser, slightly swung hats with rolls.
  - Lo-fi grit everywhere: vinyl crackle, tape saturation and wobble, rolled-off highs, a crushed master; pitched-down vocal chops and a horror-style choir pad.
  - **New phonk arrangement:** sparse intro (cowbell + atmosphere) → main → main → breakdown (bass + atmosphere) → denser drop → degrading outro. No long EDM build-ups; songs land around 1:30-3:00.
  - *House Phonk* gets the distorted 808 bass, crushed cowbell and grit; *Memphis Phonk* (66-92 BPM) gets the crushed cowbell and a horror pad.
- **New genre: Brazilian Phonk** - baile-funk bounce (syncopated tamborzão kick/snare and congas) under phonk grit: distorted cowbell riff, heavy distorted sub, vocal shouts.

## 1.14.1
- **Phonk leads sound like phonk.** Drift Phonk, House Phonk and Memphis Phonk now always play the melody on the pitched cowbell, in its real register (around A3-A4, about an octave lower than before). Instrument rotation no longer swaps the cowbell for a saw lead in some sections.

## 1.14.0
- **Four new genres:**
  - *Dubstep (classic UK / Tempa)* - half-time 140, a heavy clean sub as the main voice, sparse shuffled 2-step drums, dub delays and reverb, dark minor/phrygian moods and lots of space. Soundsystem dubstep, not brostep.
  - *Progressive Trance (emotional)*: simple emotive chords, a big singable supersaw or pluck lead, long builds, a piano breakdown and a clean, wide drop.
  - *Organic Melodic House*: warm four-on-the-floor with shakers and congas, piano, flute, harp and soft strings; hypnotic and spacious, no big drops.
  - *Disco Funk (70s)* - KC & the Sunshine Band-style: dry punchy four-on-the-floor, a syncopated bass hook, chicken-scratch guitar, horn riffs, claps, congas and tambourine.
  - The melodic genres default to simpler, more repetitive melodies (until you move the Simplicity / Repetition knobs yourself).
- **Instruments change between song sections.** Drops/choruses, verses and breakdowns can each use a different genre-fitting instrument for a part, so one song doesn't use the same sounds all the way through.
- **Less sameness between generations.** Instruments you heard in your last few songs of a genre are used less often when you press Generate again, and genres pick from a wider pool of pads and basses.
- **More realistic orchestra from the built-in library.** Section sounds (strings, brass, choir, horns) now play as an ensemble of slightly detuned, slightly offset players spread across the stereo field; sustained strings, brass and winds swell into notes instead of switching on; and repeated notes rotate between three takes (round robin).
- **Why orchestral parts don't use your orchestra plugin.** BBC Symphony Orchestra and LABS have no presets Studio Lab can choose from, so they're only used once you save a sound per section ("Set up my orchestra…"). When a song's orchestral parts fell back to the built-in library, the result now says so and has a "Set up now" link.

## 1.13.0
- **More free instruments in Genre VSTs:** Six Sines (6-operator FM), OB-Xf (Oberheim-style poly), Odin 2 (hybrid synth) and Monique (morphing mono synth) - all free and open-source, from their official GitHub releases. They show up in every part's Sound menu once installed.
- **Safety checks before anything is installed:**
  - only open-source projects, straight from the official GitHub release; installers are never run - only the plugin files are unpacked;
  - the download must match the SHA-256 GitHub publishes for it;
  - Microsoft Defender scans the download and the unpacked plugin (Windows);
  - **VirusTotal (optional, free API key):** ~70 antivirus engines check the exact file and its plugin binaries; it's installed only if **not one** engine flags it. Files VirusTotal hasn't seen yet are sent for analysis first. Tick "only install with a VirusTotal result of 0 detections" to refuse anything without a result.
  - Each installed plugin shows which checks it passed.
- The VirusTotal key stays in your local settings.json.

## 1.12.0
- **Chords sound like chords.** About 1 in 5 chord / pad hits had two notes a semitone apart, so a chord came out as neighbouring notes rubbing. Chord colours (sus2, sus4, add9, 9th, 6th) are now only used on chords where they really form that chord (no sus4 tritones or minor-9th grinds), voice leading avoids clustered inversions, and a 7th / 9th that still lands next to another chord note moves up an octave, where it rings open. Clusters went from ~21% of chord hits to ~0.1%.
- **Strummed chords stay together** (lo-fi, folk, country, soft rock, ambient, vaporwave): swing and humanize now move a strummed chord as one, instead of re-ordering or smearing its notes.
- **New controls:**
  - *Simplicity* knob - strip a song back: plain triads, no secondary dominants or sus chords, fewer and longer melody notes, held chords, roots-only bass, no counter-melody or doubling, fewer fills, ghost notes and 16th hats (the arp drops out at the top of the range).
  - *Repetition* knob - from a melody that keeps developing to a catchy loop that keeps returning to its opening idea.
  - *Melody range* knob - narrow and chant-like to wide with big leaps (always in key).
  - *Chord speed* - chords last twice as long, or change twice as often.
  - Command line: `--simplicity`, `--repetition`, `--melody-range`, `--chord-speed`.

## 1.11.0 - the biggest one yet: 96 genres, 14 new instruments, knobs, genre-fit scores
- **Every genre audited.** Each genre was measured (tempo, kick and snare placement, swing, bass movement, harmonic rhythm, lead register, phrasing, song length) and checked against how the genre really sounds. The fixes:
  - **Leads sit in the right register in every key.** They used to be up to an octave too high in keys like B♭ or B, so they came out shrill. They're now centred around E5–E6 (a little higher for trap bells and trance) and always above the chords.
  - **Sung-style leads breathe** at the end of each phrase instead of playing non-stop (country, soul ballad, waltz and others).
  - **Song lengths match each genre** (future bass, dubstep, jazz, swing, waltz and R&B were too short or too long).
  - **Upright bass** is now the bass of jazz, swing, bluegrass, bossa nova, folk, holiday, Celtic and western.
- **Genre-fit score** on every result card, based on a production reference guide. Hover it to see what was checked: tempo range, four-on-the-floor / half-time / two-step / backbeat skeleton, swing, the clean sub in bass music, 808 slides, the genre's signature sound. Every genre passes its own checks in the tests.
- **Phonk rebuilt:**
  - **Drift Phonk** (135–155 BPM) now has a detuned, distorted phonk cowbell, a crushed long-sliding 808, a harder clipped kick, dark phrygian / phrygian-dominant melodies (with the flat 2nd and flat 6th), Memphis-style vocal chops and a louder, grittier master.
  - New **House Phonk** (four-on-the-floor) and **Memphis Phonk** (slow, lo-fi, cassette grit).
- **Bass music, done properly:**
  - **Dubstep (Dark / UK)**: 138–142, sparse, sub-heavy.
  - New **Brostep**: growl, wobble and FM basses take turns bar by bar in the drop.
  - New **Melodic Dubstep**: the drop carries the melody.
  - New **Liquid DnB** and **Neurofunk**.
  - Dubstep and DnB styles always have a clean mono sine sub under the mid-bass.
- **Trance arrangement:** DJ intro and a long beatless breakdown as the emotional peak, then the climax.
- **More new genres:** Braindance / IDM, Hauntology (warped-tape analog nostalgia, with a deeper tape wobble), Uplifting Trance, Melodic Deep House, Jam Band, Teen Pop ('99, with its last-chorus key change), 70s Soft Rock and Luxury Rap.
- **14 new instruments:** Juno-style poly synth, Prophet/OB synth brass, Moog bass, glass pad, Solina string machine, Wurlitzer, vibraphone, upright bass, palm-muted guitar, harmonica, trumpet, pedal steel, growl bass and phonk cowbell. Each is added to the genres it belongs in, and each plays a recorded version when the sound library has one.
- **New scales:** phrygian dominant (phonk, dark electronic) and melodic minor (jazz).
- **Knobs:** every slider is now a rotary knob. Drag up or down (Shift for fine control), scroll or use the arrow keys; double-click resets.
- **Switch parts off from any result card** (**On / off**): no lead for an instrumental bed, no drums for a loop. You get the same take minus that part, note for note. The **Parts** panel is now open by default.
- Layered instruments now copy the tuned notes (they could differ slightly from the part they doubled).
- Note: songs from earlier versions may sound different with the same seed.

## 1.10.0 - 21 more genres, layered sounds, real dynamics
- **21 new genres (82 total):** Waltz (3/4), Celtic Jig (6/8), Soul Ballad (12/8), Gospel, Country, Bluegrass, Motown / 60s Soul, R&B / Neo-soul, Big Band Swing, Ska, Punk, Indie Rock, Salsa, Cumbia, Tango, Dancehall, Afro House, Melodic Techno, K-pop, Jersey Club and Baile Funk. Each has its own drums, bass lines, harmony and pool of authentic instruments.
- **Time signatures besides 4/4:** 3/4, 6/8 and 12/8 genres with triplet-grid rhythms throughout (drums, bass, chords, melody, fills, vocal guide). MIDI exports carry the real time signature and tempo.
- **Layered sounds:** a part can be played by two instruments at once, chosen from the genre's own pool and different in every song. For example: a supersaw lead with a bell an octave up, violins doubled by flute an octave up or celli an octave down, saw bass with a sub under it, piano chords with strings inside them. Under **Layered sounds**: genre decides, more, or off.
- **Counter-melodies:** in orchestral, chamber, pop, gospel, Motown, country, tango and other genres, a second line (celli, horns, clarinet, strings) answers the lead in its gaps and moves under its long notes. Under **Counter-melody**: genre decides, always, or never.
- **Real dynamics for orchestra plugins:** saved orchestra sounds (BBC Symphony Orchestra, LABS ...) get mod-wheel (CC1) and expression (CC11) curves, so long notes swell and relax, quiet sections sit lower, and builds rise. The curves are in the MIDI export too.
- **Played softer and harder:** recorded instruments and plugins are played with lower velocity in quiet sections and higher in big ones, and phrases lean toward their third bar. They now change tone with the music, not just volume.
- **Voice leading:** chords and pads move each note to the nearest note of the next chord, like a pianist or string section, instead of jumping between fixed shapes.
- **Moving bass lines:** in pop, folk, country, baroque, chamber, Motown and others, the bass steps into the next chord on the last beat.
- **Richer harmony:** occasional secondary dominants (e.g. II major leading to V), the borrowed minor iv before home, the major V in minor keys, and sometimes a major chord at the end of minor-key orchestral and classic pieces.
- **🎻 Set up my orchestra** (VST screen): pick your orchestra plugin and set up each section in one place (strings legato / spiccato / tremolo / pizzicato, violins, celli, horns, trumpets, low brass, woodwinds, harp, celeste, timpani, choir). Studio Lab names each sound so every genre finds it.
- **Re-roll ×4:** tick ×4 next to Re-roll and click a part to get four versions of just that part over the exact same song.
- **Result cards** show friendly instrument names, layers and the counter-melody, the time signature, and tags for what makes each take different (lead style, counter-melody, layered parts, secondary dominants, voicings, key change).
- New instruments: accordion / bandoneon and banjo (plus recorded accordion, bandoneon, banjo, steel-string guitar, fiddle and brass section with the sound library).
- Command line: `--counter on|off`, `--layering off|more`.
- Note: songs from earlier versions may sound different with the same seed.

## 1.9.0 - strings, orchestra and more variety
- **10 new genres built around strings and orchestra:** Neoclassical, Chamber / String Quartet, Baroque, Fantasy RPG, Hybrid Trailer, Orchestral Hip Hop, Symphonic Metal, Holiday, Spaghetti Western and Chamber Pop (61 total).
- **Your orchestra plugin is used everywhere it fits.** Save sounds from BBC Symphony Orchestra, LABS or any sampler with names like "BBC strings legato", "BBC strings spiccato", "BBC strings tremolo", "BBC celli", "BBC horns", "BBC low brass", "BBC oboe", and each part picks the right one by section and articulation: long string pads take legato, ostinatos take spiccato, pizzicato parts take pizzicato. This works in any genre, not just orchestral ones. If you saved several matching sounds (two string libraries, say), songs alternate between them.
- **New instruments:** spiccato (short) strings, tremolo strings, solo cello, harpsichord, clarinet, oboe, trailer braam and sleigh bells. With the sound library installed they play real recorded cello, viola, contrabass, trumpet, trombone and more.
- **Each genre now picks from several authentic instruments per part** instead of always using the same one (or a random sound from a generic list). Trance leads vary between supersaw, saw and pluck leads; cinematic leads between horns, brass, violin, cello and choir; funk bass between synth, slap and finger bass. The genre's signature sound is still the most likely pick. Each song also gets its own take on the synth tone (filter, detune, resonance).
- **Genre VSTs vary too:** each song picks among all the suitable patches of the plugins you have, instead of always the first. More patches: Juno strings, fat square bass and square lead (TAL-NoiseMaker); wide pad, dark supersaw and bright pluck (Surge XT); and more DX7 voices (brass, strings, piano, harpsichord, flute, synth lead, voice, chimes) in Dexed.
- **Everything stays in tune with the chords:** held melody, arpeggio and vocal-guide notes that rubbed a semitone against the chord underneath now move to the nearest note that fits. This mostly affected trap, drill and phonk bell melodies over harmonic-minor chords, and arpeggios over sus chords. Measured across all genres, these clashes dropped from 6.5% of held notes to about 1%. What's left is intentional: blue notes in blues, funk and boom bap, and bebop approach notes in jazz and bossa nova.
- Sus chords: the pad and arpeggio now follow the chords when they switch to a sus chord (they used to keep the 3rd and clash).
- More authentic orchestral writing: spiccato ostinatos in Cinematic and Adventure, tremolo strings in Dark Tension, open voicings in orchestral styles, and celli / contrabass on orchestral bass lines with the sound library.
- Fixed: MIDI and DAW exports gave parts that played recorded instruments or plugins the piano program (GM 0). They now get the right one, e.g. cello or trumpet.
- Note: songs from earlier versions may sound different with the same seed.

## 1.8.1
- **Fixed the "buh-duh" figure that showed up in every genre:** melodies drew extra rhythms from one shared bank full of quick 16th-note pairs. Each genre family now has its own phrasing - sung lines (pop, rock, folk), syncopated (funk, house, Afro styles), long and breathing (film, ambient, lo-fi, jazz) and busy (psytrance, DnB, trap ...), where quick pairs belong.
- Bass "approach" notes (a step into the next chord, just before it) are now occasional instead of constant; jazz and bossa bebop approach notes are rarer.
- Fixed: in choruses and drops, chords kept stacking octaves on every hit instead of doubling the top note once.

## 1.8.0 - more genre, less sameness
- **Build-ups that fit the genre.** Every genre used to get the same snare roll + riser. Now: snare roll + riser for trance and big room; filter sweep with the kick dropping out for house, techno and acid; kick roll for hardstyle; triplet rolls for future bass and hyperpop; stutters and silence for dubstep and breakcore; the band dropping out for amapiano, Afrobeats, reggaeton and UK garage; a snare lift (no EDM riser) for pop and rock pre-choruses; swells for film music. Pick one yourself under *Build-ups*.
- **Arrangements that fit the genre.** Techno, minimal, tech house and acid house use a DJ-style arrangement (parts enter one by one, one long breakdown); drum & bass, amapiano and UK garage get their own song shapes.
- **Lead lines built the way each genre builds them:** arpeggios (trance, synthwave, chiptune), low riffs (rock, metal, funk, blues), hypnotic ostinatos (techno, minimal, acid), bell motifs (trap, drill, phonk), call & response (Afrobeats, amapiano, reggae, reggaeton), vocal-chop stabs (house, garage, future bass) and sung-style hooks. Each song picks one of the styles that suit its genre. Choose under *Lead style*.
- **Better hooks:** every phrase has a shape (arch, rise, fall, wave), motifs come back as sequences instead of exact copies, fewer repeated notes, and mid-phrase endings stay open instead of always landing on the home note.
- Measured across all 51 genres: lead lines are far less alike between genres (similarity 0.91 -> 0.74), with more than twice as many melodic leaps.
- Command line: `--lead arp|riff|ostinato|bell|call|chops|hook`, `--build roll|filter|triplet|kick_roll|stutter|pause|lift|swell`.

## 1.7.0
**Songs sound more like records**
- **Fills and transitions:** a fill into every chorus, drop and climax (tom fills for band styles, snare fills for electronic), plus a reverse-cymbal swell. Choruses and drops open up with wider chords.
- **Real endings:** band, jazz, hip-hop and film styles end on a final chord with a crash instead of fading out (club tracks keep their DJ-friendly fade). Choose under *Ending*.
- **Groove feel:** each genre plays with its own timing - lazy late snares in boom bap and lo-fi, laid-back reggae skanks, pushed Afro hats, dembow push, house late hats, jazz ride on top. Choose under *Groove feel*.
- **Tighter low end:** in electronic styles bass notes that land a hair off the kick now hit with it; *Bass rhythm → Follow the kick drum* locks any style's bass to the kick.
- **Vocal guide:** every song gets a singable melody (verses low, choruses higher, breaths between phrases, the chorus repeats). It's always in the MIDI exports (with "la" lyric markers); tick *hear it in the song* to play it.

**Faster to get what you want**
- **New seed on every press:** pressing Preview (or 4 Variations) again makes a new song. *Full song* right after a preview renders that preview's song. Tick 🔒 next to the seed to keep it while you tweak.
- **Keep parts:** 🔒 on a result's drums, bass, chords, melody or harmony keeps that part in your next previews.
- **♥ parts you like:** Surprise me learns from them (and reuses parts and instruments you loved).
- **A/B compare:** pick two results, flip between them at the same moment, loudness-matched.
- **References from note files:** 🎯 Match a reference now takes MIDI (.mid), MusicXML (.musicxml/.mxl from MuseScore, Sibelius, Dorico ...) and Studio Lab settings files, not just audio - and reads the chord progression, mode, swing, energy and complexity too. Command line: `--reference song.mid`.

**Plugins & DAWs**
- **Effect plugins per part:** run any part through one of your effect plugins (reverbs, delays, saturators ...).
- **Plugin presets:** .vstpreset files for your instruments appear in the Sound menus.
- **DAW pack export:** aligned stems, per-part MIDI, full-song MIDI with key signature, vocal guide, a REAPER project and step-by-step import notes for Ableton Live, FL Studio, Logic, Cubase, Studio One and Bitwig - zipped.
- **Verified downloads:** Genre VST downloads are checked against the SHA-256 checksum the project publishes; a file that doesn't match is not installed.
- The status line shows progress while Studio Lab checks newly installed plugins.

**Fixes**
- Typing a progression containing a 7 (e.g. `1-6-3-7`) no longer fails.
- MIDI exports now carry a key signature.
- Note: each part's per-song palette now comes from its own seed (that's what makes 🔒 parts work), so a seed may sound a bit different than in earlier versions.

## 1.6.0
- **Pick your installed plugins in the Sound menus.** Every part's menu now has an *Installed plugins* group: genre patches for the synths Studio Lab knows (TAL-NoiseMaker · Juno pad, Surge XT · Supersaw, Dexed · DX7 E.Piano, JC303 · 303 acid ...) and the default sound of any other instrument plugin on your computer. Studio Lab checks each plugin once in the background to tell instruments from effects.
- **Genre melody languages:** leads now phrase like the genre's players - blue notes and slides in blues, rock and funk; pentatonic lines in folk, Afrobeats, amapiano, reggae, lo-fi and pop; bebop chromatic approach notes in jazz and bossa nova.
- **Authentic chord voicings:** rootless jazz-piano voicings for jazz, bossa nova, lo-fi and boom bap; drop-2 voicings for city pop, deep house, UK garage, funk and disco; jazz and neo-soul styles always use 7th / 9th chords.
- **New controls:** *Melody style*, *Chord voicing* and *Chord colour* (Sound), and *Part levels* for drums, bass, chords, pad, arp and lead (Mix & master). Saved in presets. Command line: `--melody`, `--voicing`, `--chord-color`, `--level lead=-3`.
- Plugins that won't load now say why: program file missing (antivirus), 32-bit Python, ARM PC, or the plugin's own error. Once a plugin fails, the other parts using it skip it instead of each retrying.

## 1.5.1
- **Installed plugins are found and used automatically.** Studio Lab scans your plugin folders at start-up (and every few minutes); no more ticking plugins in *My plugins* or switching genre VSTs on. Matching parts simply play through what you have.
- Your own saved VST sounds are used by name: call a sound "Serum supersaw", "Vital lead", "Keyscape Rhodes" or "BBC strings" and parts of that kind use it in any style.
- **Safety:** the DISTRHO plugin pack was removed from the downloads after an antivirus alert on one of its effects (SoulForce, which Studio Lab never used). Downloads now unpack only the plugins Studio Lab needs, installer programs are never run, and nothing changes macOS download flags. Already-installed Nekobi/Kars can be removed from *Genre VSTs*.
- A plugin that fails to load (e.g. its program file was removed by antivirus software) is no longer retried on every render; *Genre VSTs* lists it with the reason, and it's tried again once it's reinstalled.
- Installs are checked for completeness before they're reported as installed.
- Command line: installed plugins are used by default; `generate --no-vst-rig` turns that off.

## 1.5.0
- **🎚 Genre VSTs:** one-click download of free, open-source instruments - Surge XT, Dexed (DX7), JC303 (TB-303) and DISTRHO Nekobi + Kars - straight into the plugins folder. No installers to click through where the project ships plain plugin files; the newest release for your computer is picked automatically.
- **Genre rigs:** with *Play parts through genre VSTs* on, each part is played by the plugin that defines its genre's sound: 303 acid lines for acid house and techno, Surge XT supersaws for trance and big room, Juno-style TAL-NoiseMaker basses, pads and leads for synthwave and synth-pop, DX7 electric piano, clav and marimba for city pop, lo-fi and funk. Lo-fi and vaporwave patches come out darker, trance and hyperpop brighter.
- Works with plugins you already have: TAL-NoiseMaker is used automatically; for sample players like BBC Symphony Orchestra or LABS, save a sound named e.g. "BBC strings" and orchestral parts use it.
- "Download what this style needs" shows exactly which plugin each part will use, and the best one you're missing.
- Patches only use settings the plugin really has; if a plugin version doesn't match, that part keeps its built-in sound instead of playing the wrong instrument. Sounds you pick yourself under *Sound* are never replaced.
- Fixed: mono VST instruments (many synths) failed to render and always fell back to the built-in sound.
- Command line: `python studiolab.py vsts --for acid_house` (download + show the rig), `generate --vst-rig`, `vsts --params Plugin.vst3` (list a plugin's parameter names).

## 1.4.0
- **🎻 Real instruments:** one-click download of a free library of recorded instruments (GeneralUser GS). Orchestral and Classic styles now play real strings, brass, woodwinds, timpani, harp, pianos, guitars, bass guitars and acoustic drum kits - in previews, full songs and LMMS projects.
- More authentic genres: overdriven/distorted guitars and power chords for rock & metal, upright bass and brushes for jazz and bossa nova, slap bass for funk and city pop, orchestra kit + pitched timpani for orchestral styles.
- Orchestral, jazz, folk, bossa and blues get a gentle master that keeps the dynamics (no club-style pumping or saturation).
- Electronic styles swap only obviously acoustic parts (piano, guitar, flute, sax...) for recordings; synths stay synths.
- New "Real instruments" button; the library is kept across updates.

## 1.3.0
- **🎹 VST instruments (experimental):** play any part with your own VST3 / Audio Unit instruments. One-click setup, then create sounds from the plugin's own window and pick them under *Sound* as "VST: …".
- Plugins run in a separate process — if one crashes or misbehaves, that part falls back to the built-in sound and the result card shows a warning.
- Drop `.vst3` files into the `plugins` folder, or just install them normally (system plugin folders are scanned).
- Waveform projects get the VST-rendered audio in the stems; LMMS projects use the closest built-in patch for those parts.
- Instrument names on result cards are now friendlier.

## 1.2.0
- **Section editor:** click any section on a song's timeline to re-roll it (whole section, or just drums/bass/chords/melody), make a subtle variation, change its length, move, duplicate or remove it, or mute parts inside it. Hear just that section, then render the full song. Everything else stays exactly the same.
- **Much more variety:** a bigger chord-progression library, separate verse, drop and break progressions, chord colours (7ths, add9, sus, 6ths), varied melody phrasing and occasional key changes. Each song also picks its own instruments, tones, groove patterns, drum kit and arrangement. A new **Variety** slider controls how adventurous this gets.
- **16 new genres:** Afrobeats, Amapiano, Reggaeton, Moombahton, UK Drill, Hyperpop, Vaporwave, Eurodance, Breakcore, City Pop, Bossa Nova, Blues, Metal, Folk, Adventure/Fantasy and Dark Tension (51 total).
- **New instruments:** log drum, marimba, kalimba, steel drum, saxophone, flute, clavinet, plus finger snap, tambourine and woodblock.
- **Easier genre blending:** every style has a checkbox; tick several to blend, and the ★ marks the lead style.
- **Drag MIDI into your DAW:** each part has its own draggable MIDI file (Chrome/Edge).
- **Reference matching:** drop in a song you like to match its tempo, key, loudness and brightness.
- **Sample pack export:** bar-exact loops of every part, one-shots and MIDI loops.
- **My sounds:** use your own drum samples, or one recorded note as a playable instrument (also carried into LMMS projects).
- **👍 / 👎 ratings:** Surprise me now leans toward what you like.
- **Security:** the app only answers your own browser on your own computer. A per-launch secret blocks other websites, and file access is limited to the app's own folders.

## 1.1.0
- **My plugins**: tick the VST/AU plugins you own, or scan your plugin folders to detect them automatically.
- Each full song comes with a PLUGIN_GUIDE listing which plugin to load on each part. It favours plugins you own and only suggests ones your DAWs can load (LMMS takes VST2 + SF2; Waveform takes VST/VST3/AU).
- Download links for the best free instruments and effects.
- MIDI and Waveform track names include the suggested plugin.

## 1.0.0
- First release.
