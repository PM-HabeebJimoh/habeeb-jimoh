import re, sys, os, csv, glob, html
rows, seen = [], set()
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.html'))):
    q = os.path.basename(f).split('__')[1][:-5].replace('+',' ')
    s = open(f, encoding='utf-8', errors='ignore').read()
    for name, price in re.findall(r'data-product-name="([^"]+)" data-product-price="([\d\.]+)"', s):
        name = html.unescape(name)
        if name in seen: continue
        seen.add(name); rows.append(dict(site='medplusnig.com', query=q, title=name, price_ngn=float(price)))
w = csv.DictWriter(open(sys.argv[2],'w',newline=''), fieldnames=['site','query','title','price_ngn']); w.writeheader(); w.writerows(rows)
print(len(rows),'products')
