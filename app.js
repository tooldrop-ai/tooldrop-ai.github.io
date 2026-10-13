(()=>{"use strict";
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],root=document.documentElement;
const store={get(k,d){try{return JSON.parse(localStorage.getItem(k))??d}catch{return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch{}}};
const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
const isMac=/Mac|iPhone|iPad/.test(navigator.platform||navigator.userAgent);
if(!isMac)$$("kbd").forEach(k=>{if(k.textContent==="⌘K")k.textContent="Ctrl K"});else $$("kbd").forEach(k=>{if(k.textContent==="Ctrl K")k.textContent="⌘K"});

/* theme */
$("#theme")?.addEventListener("click",()=>{const t=root.dataset.theme==="dark"?"light":"dark";root.dataset.theme=t;try{localStorage.setItem("td-theme",t)}catch{}});

/* reveal on scroll */
const io="IntersectionObserver"in window&&!reduce?new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}}),{rootMargin:"0px 0px -6% 0px"}):null;
$$(".reveal").forEach((el,i)=>{if(io){el.style.transitionDelay=Math.min(i%8,6)*40+"ms";io.observe(el)}else el.classList.add("in")});

/* card spotlight */
document.addEventListener("pointermove",e=>{const c=e.target.closest?.(".card");if(c){const r=c.getBoundingClientRect();c.style.setProperty("--mx",(e.clientX-r.left)+"px")}},{passive:true});

/* favorites */
let favs=new Set(store.get("td-favs",[]));
const syncFavs=()=>{$$("[data-fav]").forEach(b=>{const on=favs.has(b.dataset.fav);b.setAttribute("aria-pressed",on);const l=$(".fl",b);if(l)l.textContent=on?"In My stack":"Save to My stack"});const n=$("#stack-n");if(n)n.textContent=favs.size};
document.addEventListener("click",e=>{const b=e.target.closest("[data-fav]");if(!b)return;e.preventDefault();const s=b.dataset.fav;favs.has(s)?favs.delete(s):favs.add(s);store.set("td-favs",[...favs]);b.classList.remove("pop");void b.offsetWidth;b.classList.add("pop");syncFavs();if(state)apply()});
syncFavs();

/* directory filtering (home only) */
const grid=$("#grid");let state=null;
const cards=grid?$$(".card",grid):[];
function apply(push){const {q,cat,price,sort,stack}=state;const terms=q.toLowerCase().trim().split(/\s+/).filter(Boolean);let n=0;
 const list=[...cards].sort(sort==="new"?(a,b)=>b.dataset.date.localeCompare(a.dataset.date)||a.dataset.name.localeCompare(b.dataset.name):(a,b)=>a.dataset.name.localeCompare(b.dataset.name));
 list.forEach(c=>{const text=c.textContent.toLowerCase();const ok=(!cat||c.dataset.cat===cat)&&(!price||c.dataset.price===price)&&(!stack||favs.has(c.dataset.slug))&&terms.every(t=>text.includes(t));
  const was=!c.classList.contains("hide");c.classList.toggle("hide",!ok);if(ok){n++;if(!was&&!reduce){c.classList.remove("enter");void c.offsetWidth;c.classList.add("enter")}}grid.appendChild(c)});
 $("#count").textContent=stack?`${n} in My stack`:`${n} of ${cards.length} tools`;
 const em=$("#empty");em.hidden=n>0;em.firstChild.textContent=stack&&!favs.size?"Your stack is empty — tap the ☆ on any tool to save it. ":"No tools match. ";
 $$("#cats .chip").forEach(b=>b.setAttribute("aria-pressed",b.dataset.c===cat));$("#stack").setAttribute("aria-pressed",stack);
 const p=new URLSearchParams();q&&p.set("q",q);cat&&p.set("cat",cat);price&&p.set("price",price);sort!=="az"&&p.set("sort",sort);stack&&p.set("view","stack");
 const url=location.pathname+(p.toString()?"?"+p:"")+location.hash;history.replaceState(null,"",url)}
if(grid){const p=new URLSearchParams(location.search);
 state={q:p.get("q")||"",cat:p.get("cat")||"",price:p.get("price")||"",sort:p.get("sort")==="new"?"new":"az",stack:p.get("view")==="stack"};
 $("#q").value=state.q;$("#price").value=state.price;$("#sort").value=state.sort;
 let t;$("#q").addEventListener("input",e=>{clearTimeout(t);t=setTimeout(()=>{state.q=e.target.value;apply()},90)});
 $("#price").addEventListener("change",e=>{state.price=e.target.value;apply()});$("#sort").addEventListener("change",e=>{state.sort=e.target.value;apply()});
 $("#cats").addEventListener("click",e=>{const b=e.target.closest(".chip");if(b){state.cat=b.dataset.c;apply()}});
 $("#stack").addEventListener("click",()=>{state.stack=!state.stack;apply()});
 $("#reset").addEventListener("click",()=>{state={q:"",cat:"",price:"",sort:state.sort,stack:false};$("#q").value="";$("#price").value="";apply()});
 apply();if(location.search&&!location.hash&&(state.q||state.cat||state.price||state.stack))$("#tools").scrollIntoView()}

/* submit form: put tool name in issue title */
const sf=$("#submit-form");sf?.addEventListener("submit",()=>{$('[name="title"]',sf).value="[Tool] "+$("#f-name").value.trim()});

/* tools data (palette + random) */
let data=null;const load=()=>data?Promise.resolve(data):fetch("/tools.json").then(r=>r.json()).then(d=>(data=d.map(t=>({...t,slug:t.name.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")})),data));
$("#random")?.addEventListener("click",()=>{const pool=cards.length?cards.filter(c=>!c.classList.contains("hide")):[];if(pool.length){location.href="/tool/"+pool[Math.floor(Math.random()*pool.length)].dataset.slug+".html";return}load().then(d=>location.href="/tool/"+d[Math.floor(Math.random()*d.length)].slug+".html")});

/* command palette */
const dlg=$("#palette"),pq=$("#pal-q"),pl=$("#pal-list");let sel=0,res=[];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function renderPal(){const q=pq.value.toLowerCase().trim();const sc=t=>{const n=t.name.toLowerCase();if(!q)return 1;if(n.startsWith(q))return 4;if(n.includes(q))return 3;if(t.category.toLowerCase().includes(q))return 2;return (t.description+" "+t.pricing).toLowerCase().includes(q)?1:0};
 res=data.map(t=>[sc(t),t]).filter(x=>x[0]).sort((a,b)=>b[0]-a[0]||a[1].name.localeCompare(b[1].name)).slice(0,30).map(x=>x[1]);sel=Math.min(sel,Math.max(res.length-1,0));
 pl.innerHTML=res.length?res.map((t,i)=>`<li role="option" id="po${i}" aria-selected="${i===sel}"><a href="/tool/${t.slug}.html"><strong>${esc(t.name)}</strong><span class="muted small">${esc(t.description.slice(0,60))}${t.description.length>60?"…":""}</span><span>${esc(t.category)}</span></a></li>`).join(""):`<li class="muted" style="padding:14px">No matches for “${esc(pq.value)}”</li>`;
 pq.setAttribute("aria-activedescendant",res.length?"po"+sel:"");$("#po"+sel)?.scrollIntoView({block:"nearest"})}
function openPal(){if(!dlg||dlg.open)return;load().then(()=>{dlg.showModal();pq.value="";sel=0;renderPal();pq.focus()}).catch(()=>{const q=$("#q");q?q.focus():location.href="/#tools"})}
$$("[data-palette]").forEach(b=>b.addEventListener("click",openPal));
document.addEventListener("keydown",e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){e.preventDefault();dlg?.open?dlg.close():openPal()}
 else if(e.key==="/"&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)&&!dlg?.open){e.preventDefault();openPal()}});
pq?.addEventListener("input",()=>{sel=0;renderPal()});
pq?.addEventListener("keydown",e=>{if(e.key==="Escape"){e.preventDefault();dlg.close();return}if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();sel=(sel+(e.key==="ArrowDown"?1:-1)+res.length)%Math.max(res.length,1);renderPal()}else if(e.key==="Enter"&&res[sel]){e.preventDefault();location.href="/tool/"+res[sel].slug+".html"}});
dlg?.addEventListener("click",e=>{if(e.target===dlg)dlg.close()});
pl?.addEventListener("mousemove",e=>{const li=e.target.closest("li[role=option]");if(li){const i=+li.id.slice(2);if(i!==sel){sel=i;$$("li[role=option]",pl).forEach((x,j)=>x.setAttribute("aria-selected",j===sel))}}});

/* back to top */
const tt=$("#totop");if(tt){let tick=false;addEventListener("scroll",()=>{if(!tick){tick=true;requestAnimationFrame(()=>{tt.classList.toggle("show",scrollY>900);tick=false})}},{passive:true});tt.addEventListener("click",()=>scrollTo({top:0,behavior:reduce?"auto":"smooth"}))}

/* PWA */
if("serviceWorker"in navigator&&location.protocol==="https:")addEventListener("load",()=>navigator.serviceWorker.register("/sw.js").catch(()=>{}));
})();
/* hero intent rotator */
(()=>{const p=document.querySelector(".intent[data-intents]");if(!p)return;const list=JSON.parse(p.dataset.intents),a=document.getElementById("intent"),t=document.getElementById("intent-t");
if(matchMedia("(prefers-reduced-motion: reduce)").matches||list.length<2)return;let i=0,paused=false;a.addEventListener("mouseenter",()=>paused=true);a.addEventListener("mouseleave",()=>paused=false);a.addEventListener("focus",()=>paused=true);a.addEventListener("blur",()=>paused=false);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async function loop(){await sleep(2600);while(true){if(paused||document.hidden){await sleep(400);continue}
 const cur=t.textContent;for(let k=cur.length;k>=0;k--){t.textContent=cur.slice(0,k);await sleep(22)}
 i=(i+1)%list.length;const[n,h]=list[i];a.href=h;for(let k=1;k<=n.length;k++){t.textContent=n.slice(0,k);await sleep(38)}await sleep(2400)}})()})();
/* badge generator */
(()=>{const sel=document.getElementById("b-tool");if(!sel)return;const code=document.getElementById("b-code"),img=document.getElementById("b-img"),lnk=document.getElementById("b-link"),ok=document.getElementById("b-ok");
const q=new URLSearchParams(location.search).get("tool");if(q&&[...sel.options].some(o=>o.value===q))sel.value=q;
const S="https://tooldrop-ai.github.io/";let md="";
function upd(){const st=document.querySelector('input[name="b-style"]:checked').value,u=`${S}tool/${sel.value}.html`,src=`${S}assets/badges/featured-${st}.svg`;img.src=`/assets/badges/featured-${st}.svg`;lnk.href=u;
 code.value=`<a href="${u}" target="_blank" rel="noopener"><img src="${src}" alt="Featured on ToolDrop" width="220" height="56"></a>`;md=`[![Featured on ToolDrop](${src})](${u})`}
const copy=(txt,msg)=>{(navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(()=>ok.textContent=msg).catch(()=>{code.select();ok.textContent="Press Ctrl/⌘+C to copy"})};
sel.addEventListener("change",upd);document.querySelectorAll('input[name="b-style"]').forEach(r=>r.addEventListener("change",upd));
document.getElementById("b-copy").addEventListener("click",()=>copy(code.value,"Copied HTML ✓"));document.getElementById("b-md").addEventListener("click",()=>copy(md,"Copied Markdown ✓"));upd()})();
