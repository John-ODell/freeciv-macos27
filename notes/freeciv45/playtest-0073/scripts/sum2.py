import re,sys
L=open(sys.argv[1]+'/drive.log').read().split('\n')
for l in L:
    m=re.match(r'== (\w+)\s+turn (\d+)',l)
    if m: print(); print(m.group(1),'T'+m.group(2),end=' ')
    for k in ('window active','other windows','centre tile','minimap visible','chooser','no own city','city [A-Z]'):
        if k in l and 'drive' not in l: print('|',l.strip()[:80].replace('city overlay',''),end=' ')
    if 'city overlay [' in l: print('| overlay open',end=' ')
