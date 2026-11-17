"""Write docs/GENRE_SPEC.md: every genre's full technical rules (tempo, scales, feel, song form, drum / bass / chord /
melody patterns, instruments and their alternatives, drum kit, build-ups, mix) - for review by people or other AIs."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sgcore.styles import STYLES, CATEGORIES, FORMS, POOLS, label  # noqa: E402
from sgcore.genre_groups import group_of, order  # noqa: E402
from sgcore.arrange import GENRE_BUILD, BUILD_FAMILY  # noqa: E402
from sgcore import drumkits  # noqa: E402
from sgcore.traits import infer, CATEGORIES as TRAIT_CATS  # noqa: E402

LEGEND = '''## How to read the patterns

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
'''


def fmt_pats(p):
    if isinstance(p, dict):
        return '; '.join(f'**{k}** ' + ' / '.join(f'`{x}`' for x in v) for k, v in p.items())
    if isinstance(p, (list, tuple)):
        return ' / '.join(f'`{x}`' for x in p)
    return f'`{p}`'


def form_of(st):
    f = st.get('form')
    sections = FORMS.get(f) if isinstance(f, str) else f
    if not sections:
        return f'`{f}`'
    rows = []
    for name, bars, layers, opts in sections:
        o = ', '.join(k if v is True else f'{k}={v}' for k, v in (opts or {}).items())
        rows.append(f'{name} {bars} [{", ".join(sorted(layers))}]' + (f' ({o})' if o else ''))
    return f'`{f}`: ' + ' -> '.join(rows)


def main():
    out = [f'# Studio Lab - technical genre rules ({len(STYLES)} genres)', '',
           'Generated from the code (`sgcore/styles.py` and friends) - this is exactly what the generator follows. '
           'Every genre lists its tempo, scales, feel, song form, patterns, sounds and mix.', '', LEGEND]
    skip = {'name', 'category', 'desc', 'tracks', 'drums', 'bass', 'chord_rh', 'lead_rh', 'progs', 'bpm', 'scales', 'form',
            'master', 'gm_hint', 'riffs', 'arp'}
    for cat in CATEGORIES:
        out += [f'# {cat}', '']
        for g in order(cat):
            ks = [k for k in STYLES if STYLES[k]['category'] == cat and group_of(k) == g]
            if not ks:
                continue
            out += [f'## {g}', '']
            for k in ks:
                st = STYLES[k]
                out += [f'### {label(k)} (`{k}`)', '', st['desc'], '']
                out.append(f"- **Tempo** {st['bpm'][0]}-{st['bpm'][1]} BPM" + (f" · meter {st['meter']}" if st.get('meter') else '')
                           + f" · **scales** {', '.join(st.get('scales') or [])} · swing {st.get('swing', 0.5)}"
                           + (f" (unit {st['swing_unit']})" if st.get('swing_unit') else '') + f" · humanise {st.get('human', 0)}")
                if st.get('progs'):
                    out.append(f"- **Progressions** {st['progs']}" + (f" · chord_bars {st['chord_bars']}" if st.get('chord_bars') else '')
                               + (f" · chord size {st['chord_size']}" if st.get('chord_size') else ''))
                out.append(f'- **Song form** {form_of(st)}' + (f" · form_scale {st['form_scale']}" if st.get('form_scale') else ''))
                if st.get('drums'):
                    out.append(f"- **Drums** {fmt_pats(st['drums'])}")
                kit = drumkits.GENRE_KIT.get(k)
                out.append(f"- **Drum kit** {kit or '(synth preset)'} · preset `{st.get('kit', 'default')}`"
                           + (f" · break chops {drumkits.CHOP[k]}" if k in drumkits.CHOP else ''))
                if st.get('bass'):
                    out.append(f"- **Bass** {fmt_pats(st['bass'])} · mode `{st.get('bass_mode', 'pattern')}` · lowest note {st.get('bass_lo')}")
                elif st.get('bass_mode'):
                    out.append(f"- **Bass** mode `{st['bass_mode']}` · lowest note {st.get('bass_lo')}")
                if st.get('chord_rh'):
                    out.append(f"- **Chord rhythm** {fmt_pats(st['chord_rh'])}")
                if st.get('arp'):
                    out.append(f"- **Arp** {st['arp']}")
                if st.get('lead_rh'):
                    out.append(f"- **Lead rhythm** {fmt_pats(st['lead_rh'])}")
                if st.get('riffs'):
                    out.append(f"- **Riffs** {fmt_pats(st['riffs'])}")
                bfam = st.get('build_family') or BUILD_FAMILY.get(GENRE_BUILD.get(k, 'roll'), [])
                out.append(f"- **Build-ups** default `{GENRE_BUILD.get(k, '(category default)')}` · choices {bfam}"
                           + (f" · transitions {st['transition_moves']}" if st.get('transition_moves') else '')
                           + (' · drops land plainly' if st.get('plain_drops') else ''))
                pools = POOLS.get(k) or {}
                tr = infer(k, st)
                out.append('- **Traits** ' + ' · '.join(f'{c} `{tr[c]}`' for c in TRAIT_CATS))
                out.append('- **Instruments**')
                for t in st['tracks']:
                    alt = pools.get(t['name']) if t['name'] == t['layer'] else None
                    extra = ' · '.join(f'{a}={t[a]}' for a in ('pan', 'rev', 'dly', 'sc') if t.get(a))
                    role = 'kick role - the genre\'s low drum' if t['layer'] == 'kick' and t['name'] != 'kick' else t['layer']
                    out.append(f"  - {t['name']} ({role}): `{t['inst']}` {t.get('db') if t.get('db') is not None else ''} dB"
                               + (f' · {extra}' if extra else '') + (f" · alternatives {alt[1:]}" if alt and len(alt) > 1 else ''))
                m = st.get('master') or {}
                out.append(f"- **Mix** {m} · reverb {st.get('reverb')} · sc_depth {st.get('sc_depth')}")
                other = {a: v for a, v in st.items() if a not in skip and not callable(v) and a not in ('swing', 'swing_unit', 'human',
                         'chord_bars', 'chord_size', 'kit', 'bass_lo', 'bass_mode', 'form_scale', 'meter', 'build_family',
                         'transition_moves', 'plain_drops', 'reverb', 'sc_depth')}
                if other:
                    out.append(f"- **Other rules** {other}")
                if st.get('gm_hint'):
                    out.append(f"- **Sound brief** {st['gm_hint']}")
                out.append('')
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'GENRE_SPEC.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(path, sum(len(x) for x in out) // 1024, 'KB')


if __name__ == '__main__':
    main()
