# Changelog

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
- **Groove feel:** each genre plays with its own timing - lazy J Dilla snares in boom bap and lo-fi, laid-back reggae skanks, pushed Afro hats, dembow push, house late hats, jazz ride on top. Choose under *Groove feel*.
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
