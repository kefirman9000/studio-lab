"""Find out which instrument an orchestra plugin has loaded, by reading its saved state.

Sample players such as BBC Symphony Orchestra (Spitfire's player) keep their instrument list in their own browser and
don't publish it to the host, so a host can't list "Violins 1, Celli, Horns ..." up front. What a host *can* read is
the plugin's state - the same blob a DAW stores in a project - and that names the loaded instrument and articulation.

So detection works like this (see vst_worker 'scan' mode): the plugin window opens once, you click through the
instruments you want in its own browser, and every time the loaded instrument changes Studio Lab reads the state,
names it from what it finds inside ("Violins 1", "Spiccato") and saves it as a sound for the matching parts. One window,
every section - no naming, no reopening.

decode_strings() is deliberately format-agnostic: JUCE plugins (Spitfire's are JUCE-based) and the JUCE VST3 host wrap
state as 'VC2!' + size + XML, often with the plugin's own blob base64- or zlib-encoded inside; anything else is scanned
for readable text. identify() then matches that text against the instrument and articulation names the libraries use.
"""
import base64
import gzip
import re
import struct
import zlib

# (name as the plugin shows it, the words Studio Lab's parts look for - see vstrigs.SOUND_WORDS / ORCH_HINT)
INSTRUMENTS = [
    ('Violins 1', 'violins'), ('Violins 2', 'violins II'), ('Violin 1', 'violins'), ('Violin 2', 'violins II'),
    ('Violins', 'violins'), ('Violas', 'violas'), ('Viola', 'violas'), ('Celli', 'celli'), ('Cellos', 'celli'),
    ('Cello', 'celli'), ('Basses', 'basses'), ('Double Basses', 'basses'), ('Contrabasses', 'basses'),
    ('Strings', 'strings'), ('String Ensemble', 'strings'),
    ('Piccolo', 'piccolo'), ('Flutes', 'flute'), ('Flute', 'flute'), ('Alto Flute', 'flute alto'),
    ('Bass Flute', 'flute bass'), ('Oboes', 'oboe'), ('Oboe', 'oboe'), ('Cor Anglais', 'oboe cor anglais'),
    ('Clarinets', 'clarinet'), ('Clarinet', 'clarinet'), ('Bass Clarinet', 'clarinet bass'),
    ('Contrabass Clarinet', 'clarinet contrabass'), ('Bassoons', 'bassoon'), ('Bassoon', 'bassoon'),
    ('Contrabassoon', 'contrabassoon'), ('Woodwinds', 'woodwinds'),
    ('Horns', 'horns'), ('Horn', 'horns'), ('Trumpets', 'trumpets'), ('Trumpet', 'trumpets'),
    ('Tenor Trombones', 'trombones'), ('Trombones', 'trombones'), ('Tenor Trombone', 'trombones'),
    ('Bass Trombones', 'low brass trombones'), ('Bass Trombone', 'low brass trombones'),
    ('Contrabass Trombone', 'low brass trombones'), ('Cimbasso', 'low brass tuba'), ('Tuba', 'tuba'),
    ('Contrabass Tuba', 'tuba'), ('Brass', 'brass'), ('Low Brass', 'low brass'),
    ('Timpani', 'timpani'), ('Harp', 'harp'), ('Celeste', 'celeste'), ('Celesta', 'celeste'),
    ('Glockenspiel', 'glockenspiel'), ('Xylophone', 'xylophone'), ('Marimba', 'marimba'),
    ('Vibraphone', 'vibraphone'), ('Tubular Bells', 'tubular bells'), ('Crotales', 'bells crotales'),
    ('Untuned Percussion', 'percussion'), ('Percussion', 'percussion'), ('Choir', 'choir'),
]
ARTICULATIONS = [
    ('Legato', 'legato'), ('Long Sul Tasto', 'long'), ('Long Sul Pont', 'long'), ('Long Flautando', 'long'),
    ('Long CS', 'long'), ('Long Harmonics', 'long'), ('Long Flutter', 'long'), ('Long Cuivre', 'long'),
    ('Long Sfz', 'long'), ('Long', 'long'), ('Sustain', 'long'), ('Spiccato', 'spiccato'),
    ('Staccatissimo', 'staccato'), ('Staccato', 'staccato'), ('Short Spiccato', 'spiccato'), ('Short Staccato', 'staccato'),
    ('Short Marcato', 'marcato'), ('Marcato', 'marcato'), ('Short', 'short'), ('Pizzicato', 'pizzicato'),
    ('Pizz', 'pizzicato'), ('Bartok', 'pizzicato'), ('Tremolo', 'tremolo'), ('Trills', 'tremolo'), ('Col Legno', 'short'),
    ('Swells', 'long'), ('Rolls', 'tremolo'), ('Hits', 'short'),
]
# fields whose values are most likely the loaded patch (checked before free text)
KEY_FIELDS = ('instrumentname', 'instrument', 'patchname', 'patch', 'presetname', 'preset', 'name', 'articulation',
              'articulationtext', 'technique', 'instrumenttext')


def _printable(b, n=4):
    return [m.decode('latin-1') for m in re.findall(rb'[\x20-\x7e]{%d,}' % n, b)] + \
        [m.decode('utf-16-le', 'ignore') for m in re.findall(rb'(?:[\x20-\x7e]\x00){%d,}' % n, b)]


JUCE_B64 = '.ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+'
_JUCE_IDX = {c: i for i, c in enumerate(JUCE_B64)}


def juce_b64decode(text):
    """JUCE MemoryBlock::fromBase64Encoding: '<size>.<chars>', 6 bits per char, least significant bits first."""
    m = re.fullmatch(r'\s*(\d+)\.([.A-Za-z0-9+]*)\s*', text)
    if not m:
        return None
    size, chars = int(m.group(1)), m.group(2)
    if size > 64 * 1024 * 1024 or len(chars) < (size * 8 + 5) // 6:
        return None
    val = 0
    for i, c in enumerate(chars[:(size * 8 + 5) // 6]):
        val |= _JUCE_IDX[c] << (6 * i)
    return (val & ((1 << (8 * size)) - 1)).to_bytes(size, 'little') if size else b''


def _unwrap(b, depth=0):
    """Yield every decoded layer of a state blob (bytes)."""
    if depth > 6 or not b:
        return
    yield b
    i = b.find(b'VC2!', 0, 72)
    if i >= 0 and len(b) >= i + 8:                         # JUCE copyXmlToBinary (sometimes after a small header)
        n = struct.unpack('<I', b[i + 4:i + 8])[0]
        yield from _unwrap(b[i + 8:i + 8 + n], depth + 1)
    for m in re.finditer(rb'>\s*(\d{1,9}\.[.A-Za-z0-9+]{8,})\s*<', b):   # JUCE's own base64 (VST3 host: <IComponent>)
        raw = juce_b64decode(m.group(1).decode())
        if raw:
            yield from _unwrap(raw, depth + 1)
    for head in (b'\x78\x01', b'\x78\x5e', b'\x78\x9c', b'\x78\xda'):
        i = b.find(head)
        if 0 <= i < 64:
            try:
                yield from _unwrap(zlib.decompress(b[i:]), depth + 1)
            except Exception:
                pass
    if b[:2] == b'\x1f\x8b':
        try:
            yield from _unwrap(gzip.decompress(b), depth + 1)
        except Exception:
            pass
    for m in re.finditer(rb'[A-Za-z0-9+/=\r\n.]{40,}', b):   # base64 inside XML (the JUCE VST3 host's IComponent etc.)
        s = re.sub(rb'\s', b'', m.group(0))
        for cand in (s, s.replace(b'.', b'+')):              # JUCE's MemoryBlock::toBase64Encoding uses its own alphabet
            try:
                raw = base64.b64decode(cand + b'=' * (-len(cand) % 4), validate=False)
            except Exception:
                continue
            if raw and (raw[:4] == b'VC2!' or raw[:1] == b'<' or raw[:2] in (b'\x78\x9c', b'\x78\xda', b'\x1f\x8b')
                        or len(_printable(raw, 6)) > 3):
                yield from _unwrap(raw, depth + 1)
                break


def decode_strings(raw):
    """Readable text inside a plugin state (bytes or base64 str), field values first: [(field or '', text)]."""
    if isinstance(raw, str):
        try:
            raw = base64.b64decode(raw)
        except Exception:
            raw = raw.encode()
    out, seen = [], set()
    for layer in _unwrap(bytes(raw or b'')):
        try:
            txt = layer.decode('utf-8')
        except UnicodeDecodeError:
            txt = None
        if txt and '<' in txt:                               # XML / JSON-ish: attribute and element values with their names
            for k, v in re.findall(r'([A-Za-z_][\w.-]*)\s*=\s*"([^"]{2,200})"', txt):
                out.append((k.lower(), v))
            for k, v in re.findall(r'<([A-Za-z_][\w.-]*)[^>]*>([^<]{2,200})</', txt):
                out.append((k.lower(), v))
            for k, v in re.findall(r'"([A-Za-z_][\w.-]*)"\s*:\s*"([^"]{2,200})"', txt):
                out.append((k.lower(), v))
        for s in _printable(layer):
            out.append(('', s))
    res = []
    for k, v in out:
        if (k, v) not in seen:
            seen.add((k, v))
            res.append((k, v.strip()))
    return res


def _find(table, text):
    """Longest table name found in text as whole words -> (shown name, words) or None."""
    best = None
    low = ' ' + re.sub(r'[\W_]+', ' ', text.lower()) + ' '
    for name, words in table:
        if ' ' + name.lower() + ' ' in low and (best is None or len(name) > len(best[0])):
            best = (name, words)
    return best


def identify(raw):
    """-> dict(instrument, articulation, words) for a state, or None when no instrument name is found."""
    pairs = decode_strings(raw)
    keyed = [v for k, v in pairs if k.split('.')[-1] in KEY_FIELDS]
    paths = [v for k, v in pairs if re.search(r'\.(zmulti|zpreset|preset|patch)\b', v, re.I)]
    inst = art = None
    for group in (keyed, paths, [v for _, v in pairs]):
        for v in group:
            inst = inst or _find(INSTRUMENTS, re.sub(r'.*[\\/]', '', v) if v in paths else v)
        if inst:
            break
    for group in (keyed, paths, [v for _, v in pairs]):
        for v in group:
            art = art or _find(ARTICULATIONS, v)
    if not inst:
        return None
    return dict(instrument=inst[0], articulation=art[0] if art else None,
                words=(inst[1] + (' ' + art[1] if art and art[1] not in inst[1] else '')).strip())


def sound_name(prefix, info):
    """'BBC violins spiccato (Violins 1 · Spiccato)' - the words first, so every genre's parts find it."""
    shown = info['instrument'] + (' · ' + info['articulation'] if info.get('articulation') else '')
    return f"{prefix + ' ' if prefix else ''}{info['words']} ({shown})"[:60]
