# second.py <save.sav.gz>...: per game, the median turn of each player's 2nd city and cities per player at the save
import sys,re,csv,gzip,statistics as st
for fn in sys.argv[1:]:
    p=None;hdr=None;founded={};nat={}
    for l in gzip.open(fn,'rt').read().splitlines():
        m=re.match(r"\[player(\d+)\]",l)
        if m: p=int(m.group(1));hdr=None
        if l.startswith('nation='): nat[p]=l
        if l.startswith('c={'): hdr=next(csv.reader([l[3:].rstrip('}')]));continue
        if hdr and l[:1].isdigit():
            d=dict(zip(hdr,next(csv.reader([l])))); founded.setdefault(p,[]).append(int(d['turn_founded']))
        if l=='}': hdr=None
    pl=[k for k in nat if 'Animal' not in nat[k] and 'Barbarian' not in nat[k]]
    sec=[sorted(founded.get(k,[]))[1] if len(founded.get(k,[]))>1 else None for k in pl]
    got=[x for x in sec if x is not None]
    n=[len(founded.get(k,[])) for k in pl]
    print(fn.split('/')[-2], 'players',len(pl),'2nd city by T40:',len(got),'median turn',st.median(got) if got else '-', 'range',(min(got),max(got)) if got else '-', 'cities',sum(n),'mean %.1f'%(sum(n)/len(pl)))
