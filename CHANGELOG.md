# Changelog

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
