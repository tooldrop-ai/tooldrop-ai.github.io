(()=>{const $=s=>document.querySelector(s),cards=[...document.querySelectorAll("#grid .card")];if(!$("#grid"))return;
const q=$("#q"),price=$("#price");let cat="All";const p=new URLSearchParams(location.search);if(p.get("q"))q.value=p.get("q");
function render(){const s=q.value.toLowerCase().trim(),pr=price.value;let n=0;
cards.forEach(c=>{const ok=(cat==="All"||c.dataset.cat===cat)&&(!pr||c.querySelector(".meta .badge:last-child").textContent===pr)&&(!s||c.textContent.toLowerCase().includes(s));c.hidden=!ok;if(ok)n++});
$("#count").textContent=`${n} of ${cards.length} tools`;document.querySelectorAll(".chip").forEach(b=>{const on=b.dataset.c===cat;b.classList.toggle("on",on);b.setAttribute("aria-pressed",on)})}
$("#cats").addEventListener("click",e=>{const b=e.target.closest(".chip");if(b){cat=b.dataset.c;render()}});q.addEventListener("input",render);price.addEventListener("change",render);
const f=$("#submit-form");f&&f.addEventListener("submit",()=>{let t=f.querySelector('[name="title"]');if(!t){t=document.createElement("input");t.type="hidden";t.name="title";f.append(t)}t.value="[Tool] "+$("#f-name").value});
render()})();
