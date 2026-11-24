"""The Anticipatory Music Transformer as an ear (Thickstun, Hall, Donahue and Liang, 2023; github.com/jthickstun/anticipation,
Apache 2.0): music in its tokens, so that its surprise at each note can be measured where its weights are (study/amt_score.py).

AMT reads notes, not scores: each note three tokens, its onset (in 10 ms steps from the window's start), its length (10 ms steps, up
to 10 s), and its instrument and MIDI pitch together. Some notes can be given as "controls": each is put into the sequence about
5 seconds before it sounds, so that the notes the model writes know where the given ones are going. Here the outer voices are the
controls and the inner voices the notes it is asked about: each inner note is heard after the inner notes before it, and after the
outer voices up to 5 seconds past it. The sequence is made with AMT's own code (its ops.pad, which puts in a rest each second
nothing sounds, and ops.anticipate), read from a checkout; a window is at most 1023 tokens (341 notes, given or not), its times
counted from its first, as AMT's training cuts them, after the flag that says controls are given.

A note's bits under AMT are those of its pitch, given its onset and length (which come first): the model's probability of that
pitch on any instrument, among the note tokens (those are all AMT can write there).

What is not alike: AMT counts in seconds, so a piece needs a tempo; it was trained on MIDI files, mostly popular music (the Large
model also on transcriptions of recordings); it pays nothing for spelling, and hears no bars or key."""
import os, sys

WINDOW = 341                                                       # notes a window holds (1023 tokens, after the flag)
_A = {}


def anticipation(checkout):
    """AMT's own modules (ops, vocab, config) from a checkout of github.com/jthickstun/anticipation"""
    if 'ops' not in _A:
        if checkout not in sys.path: sys.path.insert(0, checkout)
        from anticipation import ops, vocab, config
        _A.update(ops=ops, vocab=vocab, config=config)
    return _A['ops'], _A['vocab'], _A['config']


def tokens(notes, checkout, control=False, program=0):
    """notes [(onset s, length s, MIDI)] as AMT's triplets, on the General MIDI `program` (0, the piano), in order of onset then
    pitch (lower first)"""
    _, V, C = anticipation(checkout)
    out = []
    for t, d, m in sorted(notes, key=lambda n: (n[0], n[2])):
        tt = int(round(C.TIME_RESOLUTION * t)); dd = max(1, min(int(round(C.TIME_RESOLUTION * d)), C.MAX_DUR - 1))
        tri = [V.TIME_OFFSET + tt, V.DUR_OFFSET + dd, V.NOTE_OFFSET + 128 * program + int(m)]
        out += [x + V.CONTROL_OFFSET for x in tri] if control else tri
    return out


def sequence(notes, given, checkout, given_program=0):
    """the asked notes interleaved with the given ones as AMT's training interleaves them: (tokens, for each asked note in order of
    onset then pitch the index of its triplet). The asked notes are a piano's; the given ones too, or another program's (AMT's
    accompaniment training gives whole instruments, and asks for the others)"""
    ops, V, _ = anticipation(checkout)
    ev = tokens(notes, checkout); ct = tokens(given, checkout, control=True, program=given_program)
    end = max([ops.max_time(ev, seconds=False), ops.max_time(ct, seconds=False)])
    seq, left = ops.anticipate(ops.pad(ev, end), ct)
    if left:                                                       # given notes after the last asked one: after the end's rests
        seq += left
    where = [i // 3 for i in range(2, len(seq), 3) if seq[i] < V.REST]
    assert len(where) == len(notes)
    return seq, where


def window(seq, start, end, checkout):
    """triplets [start, end) as a window: the flag, then its tokens with times counted from its first"""
    ops, V, C = anticipation(checkout)
    w = seq[3 * start:3 * end]
    w = ops.translate(w, -ops.min_time(w, seconds=False), seconds=False)
    if ops.max_time(w, seconds=False) >= C.MAX_TIME: raise ValueError('a window longer than 100 seconds')
    return [V.ANTICIPATE] + w


def windows(seq, scored, checkout, size=WINDOW):
    """windows covering the scored triplets: [(tokens, [position of each scored note's pitch token in them])] in the order of
    `scored`. Each window after the first begins halfway through the one before, so that each note has at least half a window
    before it, or the piece's start; a window is made shorter where its times would pass 100 seconds"""
    n = len(seq) // 3; last = max(scored) + 1
    spans, s, done = [], 0, 0
    while done < last:
        e = min(n, s + size)
        while True:
            try: toks = window(seq, s, e, checkout); break
            except ValueError: e -= 8
        spans.append((s, e, done, toks)); done = e
        s = max(s + 1, (s + e) // 2)
    out = [(toks, []) for _, _, _, toks in spans]; at = {}
    for wi, (s, e, done, _) in enumerate(spans):
        for k in range(done, e): at[k] = (wi, s)
    pos = []
    for k in scored:
        wi, s = at[k]; pos.append((wi, 1 + 3 * (k - s) + 2))
    return [toks for toks, _ in out], pos


def window_ending(seq, scored, checkout, size=WINDOW):
    """one window ending at the last scored note, reaching as far back as it can: (tokens, [position of each scored pitch token])"""
    last = max(scored) + 1; s = max(0, last - size)
    while True:
        try: toks = window(seq, s, last, checkout); break
        except ValueError: s += 8
    if min(scored) < s: raise ValueError('the scored notes do not fit one window')
    return toks, [1 + 3 * (k - s) + 2 for k in scored]
