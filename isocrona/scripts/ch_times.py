import json,urllib.request,time,math,sys
SRC={"lat":45.80889,"lon":9.07222}
CO={"auto":{"country_crossing_cost":0,"country_crossing_penalty":0}}
G="geonames/"
def hav(a,b,c,d):
    R=6371;p=math.radians
    x=math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2
    return 2*R*math.asin(math.sqrt(x))
adm1={l.split('\t')[0]:l.split('\t')[1] for l in open(G+"admin1CodesASCII.txt",encoding='utf8') if l.startswith("CH.")}
adm2={l.split('\t')[0]:l.split('\t')[1] for l in open(G+"admin2Codes.txt",encoding='utf8') if l.startswith("CH.")}
pl=[]
for l in open(G+"CH.txt",encoding='utf8'):
    f=l.rstrip('\n').split('\t')
    if f[6]!="P" or int(f[14] or 0)<=0: continue
    lat,lon=float(f[4]),float(f[5])
    if hav(SRC["lat"],SRC["lon"],lat,lon)>148: continue
    pl.append({"id":f[0],"name":f[1],"lat":lat,"lon":lon,"pop":int(f[14]),"canton":adm1.get("CH."+f[10],f[10]),"district":adm2.get(f"CH.{f[10]}.{f[11]}","")})
print(len(pl),"places",file=sys.stderr)
def post(q):
    for k in range(4):
        req=urllib.request.Request("https://valhalla1.openstreetmap.de/sources_to_targets",data=json.dumps(q).encode(),headers={"Content-Type":"application/json"})
        try: return json.loads(urllib.request.urlopen(req,timeout=120).read())
        except Exception as e: print("ERR",e,file=sys.stderr); time.sleep(3*(k+1))
for i in range(0,len(pl),99):
    b=pl[i:i+99]
    d=post({"sources":[SRC],"targets":[{"lat":p["lat"],"lon":p["lon"]} for p in b],"costing":"auto","costing_options":CO,"units":"km"})
    for p,x in zip(b,d["sources_to_targets"][0]):
        p["min"]=round(x["time"]/60,1) if x.get("time") is not None else None
        p["km"]=round(x["distance"],1) if x.get("distance") is not None else None
    time.sleep(1.1)
json.dump(pl,open("ch_places.json","w"),ensure_ascii=False)
