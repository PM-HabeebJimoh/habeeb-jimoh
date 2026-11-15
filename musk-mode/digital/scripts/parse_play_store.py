import re, sys, os, glob, html, csv
rows=[]
for f in glob.glob(os.path.join(sys.argv[1],'*.html')):
    s=open(f,encoding='utf-8',errors='ignore').read()
    pid=os.path.basename(f)[:-5]
    t=re.search(r'<title[^>]*>([^<]*)</title>',s); title=html.unescape(t.group(1)).replace(' - Apps on Google Play','').strip() if t else ''
    dl=re.search(r'>([\d\.,]+[KMB]?\+)</div><div[^>]*>Downloads',s) or re.search(r'"([\d,]+\+)"\s*,\s*\d+',s)
    rc=re.search(r'>([\d\.,]+[KMB]?) reviews<',s)
    rt=re.search(r'aria-label="Rated ([\d\.]+) stars',s)
    dev=re.search(r'"author":\s*\{"@type":"Person","name":"([^"]+)"',s) or re.search(r'href="/store/apps/dev(?:eloper)?\?id=[^"]+"[^>]*><span>([^<]+)</span>',s)
    upd=re.search(r'Updated on</div><div[^>]*>([^<]+)<',s)
    desc=re.search(r'<meta name="description" content="([^"]{0,300})',s)
    rows.append(dict(id=pid,title=title,developer=html.unescape(dev.group(1)) if dev else '',downloads=dl.group(1) if dl else '',
        reviews=rc.group(1) if rc else '',rating=rt.group(1) if rt else '',updated=upd.group(1) if upd else '',
        nigeria_in_text=('nigeria' in s.lower()[:400000]) , desc=html.unescape(desc.group(1)) if desc else ''))
def dln(x):
    m=re.match(r'([\d\.,]+)([KMB]?)\+',x or '')
    if not m: return 0
    return float(m.group(1).replace(',',''))*{'':1,'K':1e3,'M':1e6,'B':1e9}[m.group(2)]
rows.sort(key=lambda r:-dln(r['downloads']))
w=csv.DictWriter(open(sys.argv[2],'w',newline=''),fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows[:70]: print(f"{r['downloads']:>8} {r['reviews']:>7} {r['rating']:>4} {r['updated'][:12]:>12} | {r['title'][:55]} | {r['developer'][:30]}")
