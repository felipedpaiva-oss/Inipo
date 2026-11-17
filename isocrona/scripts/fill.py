import json,urllib.request,time,sys
SRC={"lat":45.80889,"lon":9.07222}
CO={"auto":{"country_crossing_cost":0,"country_crossing_penalty":0}}
def route(lat,lon,radius=None):
    t={"lat":lat,"lon":lon}
    if radius: t["radius"]=radius
    q={"locations":[SRC,t],"costing":"auto","costing_options":CO,"units":"km","directions_type":"none"}
    for k in range(3):
        req=urllib.request.Request("https://valhalla1.openstreetmap.de/route",data=json.dumps(q).encode(),headers={"Content-Type":"application/json"})
        try:
            s=json.loads(urllib.request.urlopen(req,timeout=120).read())["trip"]["summary"]
            return round(s["time"]/60,1),round(s["length"],1)
        except urllib.error.HTTPError as e:
            if e.code==400: return None,None
        except Exception as e: print("ERR",e,file=sys.stderr)
        time.sleep(3*(k+1))
    return None,None
# 1) Swiss places
pl=json.load(open("ch_places.json"))
for p in pl:
    if p["min"] is None:
        p["min"],p["km"]=route(p["lat"],p["lon"]); time.sleep(1.05)
json.dump(pl,open("ch_places.json","w"),ensure_ascii=False)
print("swiss done; still null",sum(p['min'] is None for p in pl),file=sys.stderr)
# 2) grid frontier flood
D=json.load(open("grid.json")); dl,do=D["dlat"],D["dlon"]
idx={(round(p[0]/dl),round(p[1]/do)):p for p in D["pts"]}
checked=set()
while True:
    front=[]
    for (i,j),p in idx.items():
        if p[2] is None and (i,j) not in checked:
            if any((n:=idx.get((i+a,j+b))) and n[2] is not None and n[2]<=5400 for a in (-1,0,1) for b in (-1,0,1)): front.append((i,j))
    if not front: break
    for k in front:
        checked.add(k); p=idx[k]
        m,_=route(p[0],p[1],2000); time.sleep(1.05)
        if m is not None: p[2]=m*60
    print("frontier",len(front),"newly timed",sum(idx[k][2] is not None for k in front),file=sys.stderr)
json.dump(D,open("grid.json","w"))
