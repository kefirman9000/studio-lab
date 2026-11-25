"""(2.23) Studio Lab's own DX7-style patches for Dexed, written as plain FM settings.

Dexed starts on a bank of synth patches (no bass, electric piano, marimba, bells ...), so asking it for a classic patch
by name never worked and every Dexed part fell back to the built-in sound. Instead of shipping a factory bank, each
patch here sets every voice parameter itself: a neutral baseline (no pitch envelope, no LFO, no key scaling, all
operators off) plus the operators the sound needs, designed from FM basics (stacked modulator -> carrier pairs, a
modulator that decays fast for a bright attack and a round body, inharmonic ratios for bells and mallets).

Values are given in DX7 units and converted to the plugin's 0-1 range here.
"""

RANGES = {'algorithm': (1, 32), 'feedback': (0, 7), 'transpose': (-24, 24), 'lfo_speed': (0, 99), 'lfo_delay': (0, 99),
          'lfo_pm_depth': (0, 99), 'lfo_am_depth': (0, 99), 'p_mode_sens': (0, 7), 'cutoff': (0, 1), 'resonance': (0, 1),
          'output': (0, 1)}
OP_RANGES = {'eg_rate_1': (0, 99), 'eg_rate_2': (0, 99), 'eg_rate_3': (0, 99), 'eg_rate_4': (0, 99), 'eg_level_1': (0, 99),
             'eg_level_2': (0, 99), 'eg_level_3': (0, 99), 'eg_level_4': (0, 99), 'output_level': (0, 99),
             'f_coarse': (0, 31), 'f_fine': (0, 99), 'osc_detune': (-7, 7), 'l_scale_depth': (0, 99),
             'r_scale_depth': (0, 99), 'rate_scaling': (0, 7), 'a_mod_sens': (0, 3), 'key_velocity': (0, 7)}


def _norm(lo_hi, v):
    lo, hi = lo_hi
    return max(0.0, min(1.0, (float(v) - lo) / (hi - lo)))


def op(coarse=1, fine=0, level=99, rates=(99, 50, 50, 70), levels=(99, 90, 0, 0), vel=2, detune=0, rate_scale=2, amod=0):
    return dict(f_coarse=coarse, f_fine=fine, output_level=level, osc_detune=detune, key_velocity=vel,
                rate_scaling=rate_scale, a_mod_sens=amod,
                eg_rate_1=rates[0], eg_rate_2=rates[1], eg_rate_3=rates[2], eg_rate_4=rates[3],
                eg_level_1=levels[0], eg_level_2=levels[1], eg_level_3=levels[2], eg_level_4=levels[3])


def voice(algorithm, ops, feedback=0, lfo=None, transpose=0):
    """Every Dexed parameter for one patch, ready for a rig's params ({name: 0-1 value or option word})."""
    g = dict(algorithm=algorithm, feedback=feedback, transpose=transpose, lfo_speed=35, lfo_delay=0, lfo_pm_depth=0,
             lfo_am_depth=0, p_mode_sens=0, cutoff=1.0, resonance=0.0, output=1.0)
    g.update({k: v for k, v in (lfo or {}).items() if k != 'wave'})
    out = {k: _norm(RANGES[k], v) for k, v in g.items()}
    out.update({'monomode': 'POLY', 'osc_key_sync': True, 'lfo_key_sync': True, 'lfo_wave': (lfo or {}).get('wave', 'TRIANGE')})
    for i in range(1, 5):
        out[f'pitch_eg_rate_{i}'] = 1.0
        out[f'pitch_eg_level_{i}'] = _norm((0, 99), 50)
    for n in range(1, 7):
        o = ops.get(n)
        on = o is not None
        o = o or op(level=0)
        for k, v in o.items():
            out[f'op{n}_{k}'] = _norm(OP_RANGES[k], v)
        out[f'op{n}_mode'] = 'RATIO'
        out[f'op{n}_l_key_scale'] = '-LN'
        out[f'op{n}_r_key_scale'] = '-LN'
        out[f'op{n}_l_scale_depth'] = 0.0
        out[f'op{n}_r_scale_depth'] = 0.0 if n % 2 else _norm((0, 99), 20)    # modulators soften up the keyboard
        out[f'op{n}_switch'] = f'OP{n} SWITCH ON' if on else f'OP{n} SWITCH OFF'
    return out


# Algorithm 5: three pairs (2->1, 4->3, 6->5), carriers 1, 3, 5.  Algorithm 32: six carriers (organ).
PATCHES = {
    # tine electric piano: a high-ratio 'tine' pair for the bell attack, a 1:1 pair for the warm body
    'epiano': voice(5, {1: op(1, level=96, rates=(96, 25, 25, 67), levels=(99, 75, 0, 0), vel=2),
                        2: op(14, level=56, rates=(95, 72, 30, 70), levels=(99, 0, 0, 0), vel=5),
                        3: op(1, level=92, detune=2, rates=(95, 28, 25, 67), levels=(99, 80, 0, 0), vel=2),
                        4: op(1, level=68, rates=(95, 40, 30, 70), levels=(99, 60, 0, 0), vel=6)}),
    # marimba: a fast-decaying 4:1 modulator (the wooden knock) over a short sine bar
    'marimba': voice(5, {1: op(1, level=99, rates=(99, 36, 30, 60), levels=(99, 0, 0, 0), vel=3),
                         2: op(4, level=62, rates=(99, 85, 40, 70), levels=(99, 0, 0, 0), vel=5),
                         3: op(4, level=66, rates=(99, 60, 30, 60), levels=(99, 0, 0, 0), vel=3),
                         4: op(1, level=40, rates=(99, 85, 40, 70), levels=(99, 0, 0, 0), vel=4)}),
    # tubular bells: inharmonic 3.5 and 1.41 modulators, long ring
    'bells': voice(5, {1: op(1, level=96, rates=(99, 28, 20, 30), levels=(99, 70, 0, 0), vel=2),
                       2: op(3, fine=50, level=72, rates=(99, 35, 20, 30), levels=(99, 50, 0, 0), vel=3),
                       3: op(1, level=85, rates=(99, 22, 20, 30), levels=(99, 70, 0, 0), vel=2),
                       4: op(1, fine=41, level=66, rates=(99, 40, 20, 30), levels=(99, 40, 0, 0), vel=3)}),
    # bass: the modulator snaps from bright to nearly closed (a round, punchy note - not a held brassy tone)
    'bass': voice(5, {1: op(1, level=99, rates=(99, 45, 30, 70), levels=(99, 90, 85, 0), vel=2),
                      2: op(1, level=58, rates=(99, 80, 45, 70), levels=(99, 30, 20, 0), vel=4),
                      3: op(0, level=72, detune=-2, rates=(99, 45, 30, 70), levels=(99, 90, 85, 0), vel=1)}),
    # drawbar-style organ: six sine carriers at organ footages, flat envelope
    'organ': voice(32, {1: op(0, level=78, rates=(99, 99, 99, 85), levels=(99, 99, 99, 0), vel=0),
                        2: op(1, level=96, rates=(99, 99, 99, 85), levels=(99, 99, 99, 0), vel=0),
                        3: op(2, level=84, rates=(99, 99, 99, 85), levels=(99, 99, 99, 0), vel=0),
                        4: op(3, level=74, rates=(99, 99, 99, 85), levels=(99, 99, 99, 0), vel=0),
                        5: op(4, level=70, rates=(99, 99, 99, 85), levels=(99, 99, 99, 0), vel=0),
                        6: op(6, level=60, rates=(99, 99, 99, 85), levels=(99, 99, 99, 0), vel=0)}),
    # koto / plucked string: a bright 3:1 pluck that dies fast, a 1:1 body
    'koto': voice(5, {1: op(1, level=97, rates=(99, 40, 30, 60), levels=(99, 50, 0, 0), vel=3),
                      2: op(3, level=70, rates=(99, 70, 40, 60), levels=(99, 20, 0, 0), vel=5),
                      3: op(1, level=80, detune=3, rates=(99, 45, 30, 60), levels=(99, 40, 0, 0), vel=3),
                      4: op(1, level=60, rates=(99, 60, 40, 60), levels=(99, 10, 0, 0), vel=4)}, feedback=4),
    # vibraphone: a soft 4:1 strike over a long sine bar, with the motor's tremolo
    'vibes': voice(5, {1: op(1, level=96, rates=(99, 30, 20, 45), levels=(99, 70, 0, 0), vel=2, amod=2),
                       2: op(4, level=48, rates=(99, 75, 30, 50), levels=(99, 10, 0, 0), vel=5),
                       3: op(1, level=80, detune=2, rates=(99, 30, 20, 45), levels=(99, 70, 0, 0), vel=2, amod=2)},
                   lfo=dict(lfo_speed=38, lfo_am_depth=22, wave='SINE')),
    # steel drum: a 2.0 + slightly-off modulator pair, medium ring
    'steeldrum': voice(5, {1: op(1, level=98, rates=(99, 40, 25, 55), levels=(99, 55, 0, 0), vel=3),
                           2: op(2, fine=3, level=64, rates=(99, 60, 30, 55), levels=(99, 25, 0, 0), vel=4),
                           3: op(2, level=70, rates=(99, 50, 25, 55), levels=(99, 30, 0, 0), vel=3),
                           4: op(1, fine=41, level=50, rates=(99, 70, 30, 55), levels=(99, 10, 0, 0), vel=4)}),
    # clavinet: bright, nasal, short - a feedback-driven 3:1 modulator over a damped string
    'clav': voice(5, {1: op(1, level=96, rates=(99, 45, 25, 80), levels=(99, 88, 80, 0), vel=3),
                      2: op(3, level=72, rates=(99, 55, 30, 80), levels=(99, 75, 68, 0), vel=4),
                      3: op(1, level=84, detune=3, rates=(99, 45, 25, 80), levels=(99, 86, 78, 0), vel=3),
                      4: op(5, level=58, rates=(99, 70, 40, 80), levels=(99, 60, 50, 0), vel=4)}, feedback=5),
}
