(function(){
const D=window.MAPDATA;
const [x0,y0,x1,y1]=D.bbox, K=Math.cos(46*Math.PI/180), S=560;
const W=Math.round((x1-x0)*K*S), H=Math.round((y1-y0)*S);
const P=(lon,lat)=>[((lon-x0)*K*S).toFixed(1),((y1-lat)*S).toFixed(1)];
const NS="http://www.w3.org/2000/svg";
const svg=document.getElementById('map'); svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
const el=(t,a,p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e};
const path=polys=>polys.map(poly=>poly.map(r=>'M'+r.map(c=>P(c[0],c[1]).join(',')).join('L')+'Z').join('')).join('');
const BANDS=[{t:105,c:'var(--b105)',l:'≤ 105 min (tolerância)'},{t:90,c:'var(--b90)',l:'≤ 90 min'},{t:60,c:'var(--b60)',l:'≤ 60 min'},{t:30,c:'var(--b30)',l:'≤ 30 min'}];
const bandOf=m=>m<=30?'var(--b30)':m<=60?'var(--b60)':m<=90?'var(--b90)':'var(--b105-line)';
// base
el('rect',{x:0,y:0,width:W,height:H,fill:'var(--land)'});
const gC=el('g',{});
D.countries.forEach(c=>el('path',{d:path(c.rings),fill:c.name==='Switzerland'?'var(--land-ch)':'var(--land)',stroke:'none'},gC));
const gI=el('g',{});
const layers={};
BANDS.forEach(b=>{layers[b.t]=el('path',{d:path(D.iso[b.t]),fill:b.c,'fill-rule':'evenodd',stroke:b.t===105?'var(--b105-line)':'none','stroke-width':b.t===105?1:0,'stroke-dasharray':'4 3'},gI)});
const gL=el('g',{});
D.lakes.forEach(l=>el('path',{d:path(l.rings),fill:'var(--lake)',stroke:'var(--lake-ink)','stroke-width':.6},gL));
D.cantons.forEach(c=>el('path',{d:path(c.rings),fill:'none',stroke:'var(--border)','stroke-width':.7,'stroke-dasharray':'2 3',opacity:.8}));
D.countries.forEach(c=>el('path',{d:path(c.rings),fill:'none',stroke:'var(--border)','stroke-width':1.6}));
// region labels
[[8.95,46.42,'TICINO'],[9.42,46.62,'GRIGIONI'],[8.45,46.6,'URI'],[8.15,46.3,'VALAIS'],[9.55,45.25,'ITALIA']].forEach(([lo,la,t])=>{const [x,y]=P(lo,la);el('text',{x,y,'text-anchor':'middle','font-family':'var(--mono)','font-size':12,'letter-spacing':'.18em',fill:'var(--muted)',opacity:.85}).textContent=t});
// IT cities
const tip=document.getElementById('tip'), box=svg.parentNode;
function showTip(e,html){tip.innerHTML=html;tip.hidden=false;const r=box.getBoundingClientRect();tip.style.left=(e.clientX-r.left)+'px';tip.style.top=(e.clientY-r.top)+'px'}
const gP=el('g',{});
D.it.filter(c=>!['Cinisello Balsamo','Sesto San Giovanni'].includes(c.name)).forEach(c=>{const [x,y]=P(c.lon,c.lat);
  const d=el('circle',{cx:x,cy:y,r:3.4,fill:'var(--panel)',stroke:'var(--it)','stroke-width':1.4},gP);
  const nm=c.name==='Milan'?'Milano':c.name;
  const t=el('text',{x:+x+6,y:+y+4,'font-size':11.5,fill:'var(--it)',class:'lbl'},gP);t.textContent=`${nm} ${Math.round(c.min)}′`;
  d.addEventListener('pointerenter',e=>showTip(e,`<b>${nm}</b> · ${c.min} min · ${c.km} km`));d.addEventListener('pointerleave',()=>tip.hidden=true)});
// CH places
const LBL=new Set(['Lugano','Bellinzona','Locarno','Mendrisio','Chiasso','Biasca','Airolo','Faido','Mesocco','Roveredo','Ascona','Splügen','Göschenen','Olivone','Cevio','Bosco/Gurin','Hinterrhein','Stabio','Tesserete','Brissago']);
const pts=D.ch.slice().sort((a,b)=>a.pop-b.pop);
pts.forEach(p=>{const [x,y]=P(p.lon,p.lat);
  const c=el('circle',{cx:x,cy:y,r:p.pop>20000?5:p.pop>4000?3.6:2.3,fill:bandOf(p.min),stroke:'var(--panel)','stroke-width':1},gP);
  c.addEventListener('pointerenter',e=>showTip(e,`<b>${p.name}</b> (${p.canton}) · ${p.min} min · ${p.km} km`));c.addEventListener('pointerleave',()=>tip.hidden=true)});
pts.filter(p=>LBL.has(p.name)).forEach(p=>{const [x,y]=P(p.lon,p.lat);
  const t=el('text',{x:+x+7,y:+y+4,'font-size':p.pop>20000?13:11.5,'font-weight':p.pop>20000?600:500,fill:'var(--ink)',class:'lbl'},gP);t.textContent=`${p.name} ${Math.round(p.min)}′`});
// origin
const [ox,oy]=P(D.src[1],D.src[0]);
el('circle',{cx:ox,cy:oy,r:7,fill:'var(--pin)',stroke:'var(--panel)','stroke-width':2.5});
const ot=el('text',{x:ox-10,y:oy+4,'text-anchor':'end','font-size':13,'font-weight':700,fill:'var(--pin)',class:'lbl'});ot.textContent='Como S. Giovanni';
// scale bar 20 km
const kmPx=S/111.32; const sx=18, sy=H-22;
el('rect',{x:sx,y:sy,width:(20*kmPx).toFixed(1),height:4,fill:'var(--ink)'});
el('text',{x:sx,y:sy-6,'font-size':11,'font-family':'var(--mono)',fill:'var(--muted)'}).textContent='20 km';
// legend
const lg=document.getElementById('legend');
BANDS.slice().reverse().forEach(b=>{const btn=document.createElement('button');btn.className='chip';btn.type='button';btn.id='band-'+b.t;btn.setAttribute('aria-pressed','true');
  btn.innerHTML=`<span class="sw" style="background:${b.c}"></span>${b.l}`;
  btn.onclick=()=>{const on=btn.getAttribute('aria-pressed')!=='true';btn.setAttribute('aria-pressed',on);layers[b.t].style.display=on?'':'none'};lg.appendChild(btn)});
const it=document.createElement('span');it.className='chip';it.style.cursor='default';it.innerHTML='<span class="sw" style="background:var(--panel);border-color:var(--it);border-radius:50%"></span>Cidade italiana · tempo em min';lg.appendChild(it);
// stats
const st=document.getElementById('stats');
[[30,'var(--b30)'],[60,'var(--b60)'],[90,'var(--b90)'],[105,'var(--b105)']].forEach(([t,c])=>{const s=D.stats[t];
  st.insertAdjacentHTML('beforeend',`<div class="stat"><span class="k"><span class="sw" style="background:${c}"></span>≤ ${t} min${t===105?' · tolerância':''}</span><span class="v">${s.places_ch} localidades</span><span class="s">${s.area_ch.toLocaleString('pt-BR')} km² na Suíça · ${s.area_total.toLocaleString('pt-BR')} km² no total</span></div>`)});
// table
let lim=90; const tabs=document.getElementById('tabs');
[30,60,90,105].forEach(t=>{const b=document.createElement('button');b.type='button';b.role='tab';b.id='tab-'+t;b.textContent='≤'+t;b.setAttribute('aria-selected',t===lim);
  b.onclick=()=>{lim=t;[...tabs.children].forEach(x=>x.setAttribute('aria-selected',x===b));render()};tabs.appendChild(b)});
const q=document.getElementById('q'); q.oninput=render;
function render(){const s=q.value.trim().toLowerCase();
  const rows=D.ch.filter(p=>p.min<=lim&&(!s||p.name.toLowerCase().includes(s)||p.canton.toLowerCase().includes(s))).sort((a,b)=>a.min-b.min);
  document.getElementById('rows').innerHTML=rows.map(p=>`<tr><td><span class="dot" style="background:${bandOf(p.min)}"></span>${p.name}</td><td>${p.canton==='Grisons'?'Grigioni':p.canton}</td><td class="n">${p.min.toFixed(0)}</td><td class="n">${p.km.toFixed(0)}</td></tr>`).join('');
  document.getElementById('cnt').textContent=`${rows.length} localidades · ordenadas por tempo`}
render();
})();
