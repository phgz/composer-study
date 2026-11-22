"""Each work's facts from score-reader, for the profiles: its kinds, forces, years and catalogue numbers, as score-reader's `facts`
works them out (from its labels, numbers, collections and what each source says of itself) and its catalogue holds them. Needs a
score-reader checkout with its collections fetched; writes one JSON file the profiles read.

Usage: python3 -I study/facts.py <score-reader> <ready-read copy> -o facts.json"""
import argparse, json, sys


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('score_reader'); ap.add_argument('ready'); ap.add_argument('-o', required=True); a = ap.parse_args()
    sys.path.insert(0, a.score_reader)
    from score_reader import facts as K, sources as S, catalogue as C
    out = {}
    for composer in S.composers():
        try: fs = K.facts(composer, a.ready); keys = {w['id']: w.get('keys') or [] for w in C.load(composer)['works']}
        except Exception as e: print(f'{composer}: {type(e).__name__}: {e}'); continue
        for f in fs: out[f['id']] = dict(composer=composer, kind=f.get('kind') or [], forces=f.get('forces'), year=f.get('year'),
                                         parts=f.get('parts'), keys=keys.get(f['id'], []))
    json.dump(dict(catalogue_version=C.VERSION, works=out), open(a.o, 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(out), 'works;', sum(1 for v in out.values() if v['kind']), 'with a kind;', sum(1 for v in out.values() if v['year']), 'with a year')


if __name__ == '__main__': main()
