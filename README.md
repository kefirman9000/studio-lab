<p align="center">
  <img src="docs/screenshot-1.png" alt="Studio Lab" width="100%">
</p>

<h1 align="center">Studio Lab</h1>

<p align="center"><i>A small creative lab for sound ideas.</i></p>

---

<p align="center">
  <img src="docs/screenshot-2.png" alt="Studio Lab - session" width="100%">
</p>

<p align="center">
  <img src="docs/screenshot-3.png" alt="Studio Lab - detail" width="420">&nbsp;&nbsp;
  <img src="docs/screenshot-4.png" alt="Studio Lab - plugins" width="520">
</p>

## Getting started

You need **Python 3.9 or newer** ([python.org](https://www.python.org/downloads/); on Windows tick *Add python.exe to PATH* while installing). The start files check this and tell you if your Python is missing or too old. Then download this repository (green **Code** button → **Download ZIP**) and unzip it, or clone it.

| | |
|---|---|
| **Windows** | Double-click `Start Studio Lab (Windows).bat` |
| **macOS** | Double-click `Start Studio Lab (Mac).command` (first time: right-click → Open) |
| **Linux** | `pip install -r requirements.txt && python3 studiolab.py` |

The app opens in your browser. Everything runs locally on your machine.

*Optional:* install [ffmpeg](https://ffmpeg.org/download.html) for MP3 export. Without it, songs are saved as WAV (everything else works the same).

## Genres

158 genres in three groups - Electronic, Classic and Orchestral - from house, techno, trance, dubstep, drum & bass, hard dance and hopecore to hip hop, R&B, rock, 90s alt rock, metal, punk, jazz, big band, smooth jazz, country, bluegrass, reggae, salsa, soca, Afrobeats and raga, and from Baroque, Classical and Romantic forms (theme & variations, sonata, minuet & trio) to film scores and the **Cinematic Journey** orchestral generator. Each genre has its own instruments, drum patterns, grooves, song forms and mix. The full list, with what each one does, is in [docs/GENRES.md](docs/GENRES.md).

## Real instruments

Click **🎻 Real instruments** to download free recorded instruments (all public domain / CC0, checked by checksum): an orchestra (strings, brass, woodwinds, harp, mallets), a Steinway grand and an upright, guitars, an electric and an upright bass, percussion, and six real drum kits - a studio kit, a 70s soul kit, a brushed jazz kit, a big rock kit, a modern studio kit and a dirty one - plus a collection of real snares (crisp DnB piccolo, dead 70s, huge 80s). The drum kit menu also has drum machines (808, 909, CR-78, 606, 707, DMX, LinnDrum ...), re-played breaks and dedicated drum & bass kits. Each genre picks the parts and the kit that suit it; anything not downloaded is played by the built-in synths.

## Privacy

Everything runs on your own computer. The app opens a page only your own browser can reach (127.0.0.1), protected by a secret that changes every launch. Nothing is uploaded anywhere. The only internet use is the optional update check and downloads you start yourself (instruments, sound library).

## Updating

Click **⟳ Updates** in the top-right corner. Your files, presets and settings are kept.
(If you cloned with git, `git pull` works too.)

## Genre VSTs

Studio Lab finds the plugins installed on your computer and uses them automatically. Click **🎚 Genre VSTs** to download free, open-source plugins - **Surge XT**, **Dexed**, **JC303** and **RipplerX** (modelled mallets, bells and harp) instruments, plus **Dragonfly Reverb** (halls, rooms, plates) and **Airwindows Consolidated** (mixing effects) - and play each genre through the plugin that defines its sound: a 303 for acid, supersaws for trance, a DX7 electric piano for city pop. Plugins you already own, like TAL-NoiseMaker, are used too; save sounds from any plugin with names like "Serum supersaw" or "BBC strings" and matching parts use them.

**Orchestra plugins** (BBC Symphony Orchestra, LABS, Kontakt ...): save one sound per section and articulation - e.g. "BBC strings legato", "BBC strings spiccato", "BBC strings pizzicato", "BBC celli", "BBC horns", "BBC low brass", "BBC flute" - and every part that plays strings, celli, horns or woodwinds uses the right one, in any genre. Try the orchestral genres: Neoclassical, Chamber, Baroque, Fantasy RPG, Hybrid Trailer, Cinematic, Waltz, Orchestral Hip Hop, Symphonic Metal. The easiest way to set this up is **🎹 VST → 🎻 Set up my orchestra**, which walks you through each section. Long notes then swell with the mod wheel (CC1), just as a player would ride it.

```
python studiolab.py vsts --for trance      # download what trance needs, show which plugin plays each part
python studiolab.py generate --style trance
python studiolab.py generate --style house --melody blues --voicing drop2 --level lead=-3
```

Each part's **Sound** menu lists your installed plugins too, so you can put any instrument on any part.

## Tips

- Press **▶ Preview** again for a new song; tick 🔒 next to the seed to keep one while you tweak.
- Click a section on a result's timeline to edit it: **▶ Hear this section** plays it with a short lead-in, **🔁 Loop it** repeats up to 8 bars of it seamlessly while you try new takes or sounds.
- On a result, 🔒 keeps a part (drums, bass, chords, melody) for your next previews, ♥ teaches *Surprise me* what you like, and **A/B** compares two results.
- **🎯 Match a reference** takes audio, MIDI, MusicXML or a Studio Lab settings file.
- Export a **DAW pack** for Ableton Live, FL Studio, Logic, Reaper and others.

```
python studiolab.py generate --style rock --reference song.mid --groove laidback --ending hit --formats wav,daw
```

## Works with

- [LMMS](https://lmms.io) (free)
- [Waveform Free](https://www.tracktion.com/products/waveform-free) (free)
- Any DAW that reads MIDI or WAV

## Command line

```
python studiolab.py generate --help
```

## Development

```
pip install -r requirements.txt
python -m tests.features      # genre features (riffs, tuned kicks, classical forms, effects) - about a minute
python -m tests.smoke         # every genre renders (python -m tests.smoke --shard 1/3 for a third of them)
python -m tests.genres        # genre authenticity checks
```

Every genre is defined in one place: its `style(...)` call in `sgcore/styles.py` (patterns, instruments, mix, and its `pools=` of alternative sounds). Composition lives in `sgcore/compose.py`, with music theory in `theory.py`, idiomatic figures (riffs, montunos, variations) in `figures.py`, build-ups and endings in `arrange.py` and previews / loops in `windows.py`; sound is in `instruments.py`, `render.py` and `dsp.py`.

## License

MIT

## Support

If you enjoy Studio Lab, you can support its development through [GitHub Sponsors](https://github.com/sponsors/kefirman9000).
