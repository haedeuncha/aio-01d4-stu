import './style.css';
import {defaults,labels,modes,sanitize,type Settings,type World} from './shared';
import {createPets,step,sprite,enter,clamp,type Pet} from './engine';
import {cache,loadSprites,type Frame} from './sprites';
const api=window.desktop,view=new URLSearchParams(location.search).get('view');
const panel=view==='settings',preview=!api;
if(panel)document.title='치이카와 · 설정';
document.body.className=panel?'panel':preview?'preview':'';
let settings:Settings={...defaults};
let world:World={bounds:{x:0,y:0,width:innerWidth,height:innerHeight},work:{x:0,y:0,width:innerWidth,height:innerHeight},pointer:{x:innerWidth/2,y:innerHeight/2},windows:[],fullscreen:false,tracker:'웹 미리보기 — Windows 기능 비활성'};
if(api){const init=await api.initial();settings=init.settings;world=init.world;}else{try{settings=sanitize(JSON.parse(localStorage.getItem('chiikawa')||'{}'))}catch{}}
let pets=createPets(world,settings.size),following=true,drag:Pet|undefined,hit=false,ready=false;
const canvas=document.querySelector<HTMLCanvasElement>('#world')!,ctx=canvas.getContext('2d')!,status=document.querySelector<HTMLElement>('#status')!,controls=document.querySelector<HTMLElement>('#controls')!;
function set(patch:Partial<Settings>){if(api)api.set(patch);else{apply(sanitize({...settings,...patch}));localStorage.setItem('chiikawa',JSON.stringify(settings))}}
function apply(s:Settings){const changed=s.mode!==settings.mode;settings=s;if(changed){following=true;for(const p of pets){p.surface=undefined;enter(p,'walk');p.cooldown=3+p.seed}}if(s.hidden){cancelAnimationFrame(raf);raf=0;ctx.clearRect(0,0,innerWidth,innerHeight);api?.hit(false)}else start();renderControls()}
function act(a:string){if(a==='resume'){following=true;set({mode:'pointer'})}if(a==='gather'){pets=createPets(world,settings.size);following=true}if(api)api.action(a as 'gather'|'resume'|'quit')}
function renderControls(){if(!(panel||preview))return;controls.hidden=false;controls.innerHTML=`<div class="eyebrow">LITTLE FRIENDS, EVERY DAY</div><h1>오늘도, 함께 있을게요.</h1><p>바탕화면 한쪽에 찾아온 네 명의 작은 친구들.<br>지금 기분에 맞는 시간을 골라 주세요.</p><div class="modes">${modes.map((m,i)=>`<button data-mode="${m}" class="${settings.mode===m?'selected':''}">${['🌷','🐾','☁️','🌙'][i]} ${labels[m]}</button>`).join('')}</div><label>애니메이션<select id="fps"><option value="60" ${settings.fps===60?'selected':''}>부드럽게 · 60 fps</option><option value="30" ${settings.fps===30?'selected':''}>절전 · 30 fps</option></select></label><label>친구 크기 · ${settings.size}px<input id="size" aria-label="캐릭터 크기" type="range" min="64" max="160" value="${settings.size}"></label><div class="actions"><button data-action="gather">여기로 모여</button><button data-action="resume">다시 따라와</button><button id="hide">${settings.hidden?'친구 표시':'잠깐 숨기기'}</button></div><small>Ctrl + Alt + M · 모드 변경　 G · 모으기<br>H · 숨김 / 표시　 Q · 종료<br>클릭하거나 드래그하면 모두 따라오기를 멈춥니다.<br>${world.tracker}</small>`;
 controls.querySelectorAll<HTMLButtonElement>('[data-mode]').forEach(b=>b.onclick=()=>set({mode:b.dataset.mode as Settings['mode']}));controls.querySelectorAll<HTMLButtonElement>('[data-action]').forEach(b=>b.onclick=()=>act(b.dataset.action!));controls.querySelector<HTMLSelectElement>('#fps')!.onchange=e=>set({fps:Number((e.target as HTMLSelectElement).value) as 30|60});controls.querySelector<HTMLInputElement>('#size')!.onchange=e=>set({size:Number((e.target as HTMLInputElement).value)});controls.querySelector<HTMLButtonElement>('#hide')!.onclick=()=>set({hidden:!settings.hidden});
}
let raf=0,last=0;
function resize(){const dpr=devicePixelRatio;canvas.width=Math.round(innerWidth*dpr);canvas.height=Math.round(innerHeight*dpr);canvas.style.width=innerWidth+'px';canvas.style.height=innerHeight+'px';ctx.setTransform(dpr,0,0,dpr,0,0);if(preview){world.bounds.width=world.work.width=innerWidth;world.bounds.height=world.work.height=innerHeight}}
addEventListener('resize',resize);resize();
interface Drawn{pet:Pet;f:Frame;x:number;y:number;w:number;h:number;flip:boolean}
let drawn:Drawn[]=[];
function find(x:number,y:number){return [...drawn].reverse().find(d=>{let u=(x-d.x)/d.w;const v=(y-d.y)/d.h;if(u<0||u>=1||v<0||v>=1)return false;if(d.flip)u=1-u;return d.f.alpha[(Math.min(d.f.width-1,Math.floor(u*d.f.width))+Math.floor(v*d.f.height)*d.f.width)*4+3]>32})?.pet}
function updateHit(){const value=!!drag||!!find(world.pointer.x-world.bounds.x,world.pointer.y-world.bounds.y);if(value!==hit){hit=value;api?.hit(hit)}}
function draw(now:number){raf=0;if(settings.hidden||panel||!ready)return;if(now-last<1000/settings.fps-1){raf=requestAnimationFrame(draw);return}const dt=last?Math.min(.05,(now-last)/1000):0;last=now;ctx.clearRect(0,0,innerWidth,innerHeight);drawn=[];
 for(const p of pets){step(p,dt,world,settings.mode,settings.size,following);const s=sprite(p),f=cache.get(`${p.id}/${s.kind}`)![s.frame];const scale=settings.size/Math.max(f.width,f.height),w=f.width*scale,h=f.height*scale,x=p.x-world.bounds.x-w/2,y=p.y-world.bounds.y-h;ctx.save();ctx.translate(x+(s.flip?w:0),y);ctx.scale(s.flip?-1:1,1);ctx.drawImage(f.canvas,0,0,w,h);ctx.restore();drawn.push({pet:p,f,x,y,w,h,flip:s.flip})}
 updateHit();raf=requestAnimationFrame(draw);
}
function start(){if(ready&&!panel&&!settings.hidden&&!raf){last=0;raf=requestAnimationFrame(draw)}}
canvas.addEventListener('pointerdown',e=>{const p=find(e.clientX,e.clientY);if(!p)return;following=false;api?.action('pause');drag=p;p.surface=undefined;enter(p,'drag');canvas.setPointerCapture(e.pointerId);api?.hit(true)});
canvas.addEventListener('pointermove',e=>{if(preview)world.pointer={x:e.clientX,y:e.clientY};if(drag){drag.x=clamp(e.clientX+world.bounds.x,world.bounds.x+settings.size/2,world.bounds.x+world.bounds.width-settings.size/2);drag.y=clamp(e.clientY+world.bounds.y+settings.size/2,world.bounds.y+settings.size,world.bounds.y+world.bounds.height)}updateHit()});
function release(){if(drag){enter(drag,'rest');drag.cooldown=6;drag=undefined;updateHit()}}
canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);canvas.addEventListener('lostpointercapture',release);
api?.onSettings(apply);api?.onWorld(w=>{const changed=w.tracker!==world.tracker;world=w;updateHit();if(changed)renderControls()});api?.onAction(a=>{if(a==='gather'){pets=createPets(world,settings.size);following=true}if(a==='resume')following=true;if(a==='pause')following=false});
document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(raf);raf=0}else start()});
renderControls();
if(!panel){try{await loadSprites(m=>status.textContent='친구들을 깨우는 중 · '+m);status.textContent='';ready=true;start()}catch(e){status.textContent='이미지를 불러오지 못했습니다: '+String(e);console.error(e)}}
