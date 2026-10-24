# variant.py <in.sav.gz> <out.sav.gz> <player section> <L> <T> <F> <S>: set the four civics sliders
# (value and target) of one player and take it off AI control, so it cannot re-tune them.
import gzip, sys
src, dst, sec = sys.argv[1], sys.argv[2], sys.argv[3]
vals = sys.argv[4:8]
lines = gzip.open(src, 'rt', encoding='utf-8').read().split('\n')
start = lines.index('[%s]' % sec)
end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith('['))
for i in range(start, end):
    if lines[i] == 'flags="ai","FirstCity"':
        lines[i] = 'flags="FirstCity"'
    if lines[i].startswith('multiplier={'):
        for k in range(4):
            row = lines[i + 1 + k].split(',')
            row[0] = row[1] = vals[k]
            lines[i + 1 + k] = ','.join(row)
        break
gzip.open(dst, 'wt', encoding='utf-8').write('\n'.join(lines))
