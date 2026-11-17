# Changelog

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
- **Smooth Jazz is now Kenny G style**: a new **Soprano sax** sound soaring up high in long held notes with a delayed, widening vibrato and scoops into every phrase, over lush 80s DX electric piano and pads, fretless-style bass and soft reverb-washed drums; slow ballad tempos, romantic major-key progressions and a key change for the last chorus in most songs. The sax stays a soloist (no doubling).
- New expressive vibrato for held notes on recorded instruments (used by the soprano sax).

## 1.30.0
- **Smooth jazz**, three new genres (Classic tab):
  - **Smooth Jazz** (Kenny G, Dave Koz, Boney James): the real tenor sax scooping into its notes over Rhodes 9th / major-7th chords, fretless-style bass, cross-stick drums, soft pads and the real acoustic guitar.
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
- **Braindance / IDM** plays a heavily chopped Think-style break; **country** has a train-beat snare.
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
  - *Electronic:* Italo Disco (LinnDrum-style kit with a gated-reverb snare, octave synth bass, Juno/DX7-style arps), New Beat (slow, stomping 100-115 BPM EBM/acid), Hardcore / Gabber (170-195 BPM distorted pitched kicks, hoovers), Breakbeat Hardcore / Rave (Amen-style breaks over a 4/4 kick, piano stabs, hoovers), Future Funk (swung disco groove, heavy sidechain, vocal chops, slap-style bass).
  - *Jazz:* Bebop (180-260 BPM, rapid ii-V changes, bebop lines, rootless comping), Cool / Modal Jazz (long stretches on one mode, space, muted trumpet), Soul Jazz / Hard Bop (organ trio), Jazz Fusion (straight 16ths, electric bass, Rhodes, synth and overdriven guitar).
  - *Classical:* Classical period (Mozart / Haydn - melody over Alberti bass, 4+4 phrases, horns, timpani), Romantic Orchestra (rubato, rich chromatic harmony, horns, swelling dynamics), Impressionism (lydian / modal colours, harp, flute, piano washes, flexible pulse), Minimalism (steady pulse, repeating marimba / piano cells, slow harmony).
- **New musical behaviour:** Alberti-bass accompaniment; jazz snare comping ("dropping bombs") in Bebop, Modal, Jazz and Swing; Romantic rubato (phrases push, then broaden into the cadence); the 80s **gated-reverb snare** on the LinnDrum-style kit (synthwave, synthpop, city pop, Italo); a real campana cowbell for salsa and cumbia when the percussion library is installed.
- **Fixes to existing genres:** house 120-127 BPM with moderate (not pumping) sidechain and conga fills; deep house and psytrance now flow continuously instead of build → drop, deep house with gentler sidechain; progressive house gets long evolving builds and strip-down breakdowns; uplifting trance 134-140, psytrance 140-148, big room 126-130, synthwave 90-112; jungle swings harder; the reggae skank sits on every "and".

## 1.17.0
- **Every genre has its own drum kit, and you can switch kits** (Sound → Drum kit, grouped):
  - *Drum machines:* TR-808 (rap, trap, drill), TR-909 (house), Trance 909 (rolling kick, open hats), Techno 909 (hard, rumble), 80s LinnDrum-style (synthwave, synthpop, city pop), punchy EDM, hardstyle, soft.
  - *Real kits* (from the free drum library): studio, **rock (big room - new mic: 🎻 Real instruments → Update, +51 MB)**, vintage lo-fi.
  - *Re-played breaks:* Amen-style (jungle, DnB, breakcore - chopped and re-sequenced jungle-style), Think-style (liquid DnB), Funky Drummer-style (boom bap), Apache-style, Back to Life / Tom's Diner-style shuffle (downtempo, trip-hop), Levee-style big room. These are the classic drum *patterns* played on the real kit (tuned like a sped-up record where the genre does that), not copies of the original recordings - so the songs stay yours. To use a break recording you own, load its hits under My sounds and tick "my samples".
  - Genre defaults: jungle/DnB → Amen, liquid → Think, boom bap → Funky Drummer, downtempo → Back to Life, lo-fi/vaporwave → vintage, trap/drill/rap/reggaeton → 808, house → 909, techno → Techno 909, trance → Trance 909, rock/metal/punk/indie → rock kit, funk/disco/soul/jazz/pop → studio kit, synthwave → LinnDrum-style. The result card shows which kit played.
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
  - *Progressive Trance (emotional)* - Above & Beyond-style: simple emotive chords, a big singable supersaw or pluck lead, long builds, a piano breakdown and a clean, wide drop.
  - *Organic Melodic House* - Nora En Pure-style: warm four-on-the-floor with shakers and congas, piano, flute, harp and soft strings; hypnotic and spacious, no big drops.
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
