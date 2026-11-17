import json,math
from shapely.geometry import box,shape,mapping,Polygon,MultiPolygon,Point
from shapely.ops import unary_union
NPM="npm/"
D=json.load(open("grid.json")); dl,do=D["dlat"],D["dlon"]
def iso(th):
    cells=[box(o-do/2,a-dl/2,o+do/2,a+dl/2) for a,o,t in D["pts"] if t is not None and t<=th*60]
    g=unary_union(cells).buffer(0.011,join_style=1).buffer(-0.011,join_style=1).simplify(0.003)
    # drop tiny holes/islands
    polys=list(g.geoms) if isinstance(g,MultiPolygon) else [g]
    polys=[Polygon(p.exterior,[i for i in p.interiors if Polygon(i).area>0.0008]) for p in polys if p.area>0.001]
    return MultiPolygon(polys)
I={th:iso(th) for th in (30,60,90,105)}
xmin,ymin,xmax,ymax=I[105].bounds; pad=0.08
BB=box(xmin-pad,ymin-pad,xmax+pad,ymax+pad); print("bbox",BB.bounds)
# topojson decode
def topo(path,objname):
    T=json.load(open(path)); tr=T.get("transform")
    arcs=[]
    for arc in T["arcs"]:
        x=y=0;pts=[]
        for p in arc:
            if tr: x+=p[0];y+=p[1];pts.append((x*tr["scale"][0]+tr["translate"][0],y*tr["scale"][1]+tr["translate"][1]))
            else: pts.append(tuple(p))
        arcs.append(pts)
    def ring(ix):
        out=[]
        for i in ix:
            a=arcs[i] if i>=0 else arcs[~i][::-1]
            out+= a if not out else a[1:]
        return out
    feats=[]
    for g in T["objects"][objname]["geometries"]:
        def poly(p):
            sh=ring(p[0])
            if len(sh)<4: return None
            return Polygon(sh,[h for h in (ring(r) for r in p[1:]) if len(h)>=4])
        if g["type"]=="Polygon": ps=[poly(g["arcs"])]
        elif g["type"]=="MultiPolygon": ps=[poly(p) for p in g["arcs"]]
        else: continue
        ps=[p for p in ps if p is not None]
        if not ps: continue
        geo=MultiPolygon(ps)
        feats.append((g.get("properties",{}),g.get("id"),geo.buffer(0)))
    return feats
world=topo(NPM+"world-atlas-2.0.2/package/countries-10m.json","countries")
CHM=NPM+"swiss-maps-4.7.0/package/2024/ch-combined.json"
cantons=topo(CHM,"cantons"); lakes=topo(CHM,"lakes"); chc=topo(CHM,"country")
CH=unary_union([g for _,_,g in chc])
def rnd(geom):
    def r(c): return [[round(x,4),round(y,4)] for x,y in c]
    polys=list(geom.geoms) if hasattr(geom,"geoms") else [geom]
    return [[r(p.exterior.coords)]+[r(i.coords) for i in p.interiors] for p in polys if isinstance(p,Polygon) and not p.is_empty]
out={"bbox":BB.bounds,"src":[45.80889,9.07222]}
out["iso"]={str(th):rnd(I[th].intersection(BB)) for th in I}
out["countries"]=[{"name":p.get("name"),"rings":rnd(g.intersection(BB))} for p,_,g in world if g.intersects(BB)]
out["cantons"]=[{"name":p.get("name") or p.get("NAME") or str(i),"rings":rnd(g.simplify(0.002).intersection(BB))} for p,i,g in cantons if g.intersects(BB)]
out["lakes"]=[{"name":p.get("name",""),"rings":rnd(g.simplify(0.001).intersection(BB))} for p,_,g in lakes if g.intersects(BB) and g.area>0.0005]
pl=json.load(open("ch_places.json"))
out["ch"]=[{k:p[k] for k in ("name","lat","lon","pop","canton","district","min","km")} for p in pl if p["min"] is not None and p["min"]<=105]
out["it"]=[c for c in json.load(open("it_cities.json")) if c["min"]<=125 and c["name"]!="Como" and c["pop"]>=60000 or c["name"] in ("Lecco","Varese","Novara","Bergamo","Pavia","Piacenza","Brescia","Vercelli")]
out["it"]=[c for c in out["it"] if BB.contains(Point(c["lon"],c["lat"])) and not c["name"].startswith(("Circo","Quarto","Barriera","Buenos","Parella","Pozzo","Filadelfia","Lingotto"))]
# stats
km2=lambda g: g.area*(111.32**2)*math.cos(math.radians(46.0))
st={}
for th in (30,60,90,105):
    st[th]={"area_total":round(km2(I[th])),"area_ch":round(km2(I[th].intersection(CH))),
            "places_ch":sum(1 for p in pl if p["min"] is not None and p["min"]<=th),
            "pop_ch":sum(p["pop"] for p in pl if p["min"] is not None and p["min"]<=th)}
out["stats"]=st; print(st)
print("cantons props sample",cantons[0][0], "lakes",[l["name"] for l in out["lakes"]][:12])
print("it",[(c["name"],c["min"]) for c in out["it"]])
json.dump(out,open("mapdata.json","w"),ensure_ascii=False,separators=(",",":"))
import os;print(os.path.getsize("mapdata.json"))
