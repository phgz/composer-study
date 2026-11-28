"""Corelli, op. 4 no. 5, Gavotta (dcml/corelli:notes/op04n05d.notes.tsv): the eighths of each bar in which a part has no note
sounding (Wintle: "Over the course of the gavotta, the rests have been progressively banished"). Run with python3 -I."""
import csv, collections
ns = [dict(p=r['part'], t=float(r['onset']), d=float(r['dur']), bar=int(float(r['bar'])))
      for r in csv.DictReader(open('tsv/corelli_op4n5_gavotta.tsv'), delimiter='\t')]
end = max(n['t'] + n['d'] for n in ns); bars = sorted({n['bar'] for n in ns}); B = collections.defaultdict(collections.Counter)
for p in ('staff1', 'staff2', 'staff3'):
    v = [n for n in ns if n['p'] == p]; t = 0.0
    while t < end - 1e-9:
        if not any(n['t'] <= t + 1e-6 < n['t'] + n['d'] for n in v):
            B[max((n['bar'] for n in ns if n['t'] <= t + 1e-6), default=0)][p] += 1
        t += 0.5
print(f'bars {bars[0]} to {bars[-1]}; eighths of silence a bar (violin 1 / violin 2 / bass):')
print(' '.join(f"{b}:{B[b]['staff1']}/{B[b]['staff2']}/{B[b]['staff3']}" for b in bars))
