import json,urllib.request,time,math,sys
SRC={"lat":45.80889,"lon":9.07222}
CO={"auto":{"country_crossing_cost":0,"country_crossing_penalty":0}}
def hav(a,b,c,d):
    R=6371;p=math.radians
    x=math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2
    return 2*R*math.asin(math.sqrt(x))
def post(q):
    for k in range(4):
        req=urllib.request.Request("https://valhalla1.openstreetmap.de/sources_to_targets",data=json.dumps(q).encode(),headers={"Content-Type":"application/json"})
        try: return json.loads(urllib.request.urlopen(req,timeout=120).read())
        except urllib.error.HTTPError as e:
            b=e.read()[:200]; print("HTTP",e.code,b,file=sys.stderr)
            if e.code==400: return None
        except Exception as e: print("ERR",e,file=sys.stderr)
        time.sleep(3*(k+1))
    return None
dlat,dlon=0.03,0.042
pts=[]
lat=44.95
while lat<=47.15:
    lon=7.6
    while lon<=10.6:
        if hav(SRC["lat"],SRC["lon"],lat,lon)<148: pts.append((round(lat,4),round(lon,4)))
        lon+=dlon
    lat+=dlat
print(len(pts),"points",file=sys.stderr)
out=[]
for i in range(0,len(pts),99):
    b=pts[i:i+99]
    q={"sources":[SRC],"targets":[{"lat":a,"lon":o,"radius":2000} for a,o in b],"costing":"auto","costing_options":CO}
    d=post(q)
    if d is None:
        res=[None]*len(b)
    else:
        res=[x.get("time") for x in d["sources_to_targets"][0]]
    out+= [[a,o,t] for (a,o),t in zip(b,res)]
    print(i,len(pts),file=sys.stderr); time.sleep(1.1)
json.dump({"dlat":dlat,"dlon":dlon,"pts":out},open("grid.json","w"))
