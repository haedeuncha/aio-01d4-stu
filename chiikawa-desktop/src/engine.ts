import type {Mode,World,Surface} from './shared';
export const ids=['chiikawa','hachiware','usagi','momonga'] as const;
export type State='walk'|'rest'|'snack'|'jump'|'hang'|'climb'|'sleep'|'ceiling'|'drag';
export interface Pet{id:string;x:number;y:number;state:State;age:number;direction:number;surface?:string;side:'left'|'right';cooldown:number;fromX:number;fromY:number;seed:number}
export const clamp=(n:number,a:number,b:number)=>Math.max(a,Math.min(Math.max(a,b),n));
export function createPets(w:World,size:number):Pet[]{return ids.map((id,i)=>({id,x:w.work.x+100+i*(size+16),y:w.work.y+w.work.height,state:'walk',age:0,direction:1,side:'left',cooldown:3+i*2,fromX:0,fromY:0,seed:i}))}
export function enter(p:Pet,state:State){p.state=state;p.age=0;p.fromX=p.x;p.fromY=p.y}
function move(n:number,target:number,dt:number,speed=9){return n+(target-n)*(1-Math.exp(-speed*dt))}
function target(w:World,p:Pet,size:number):Surface|undefined{return w.windows.find(r=>r.width>size*2&&r.y>=w.bounds.y+size&&r.y<w.work.y+w.work.height-size&&r.x>=w.bounds.x&&r.x+r.width<=w.bounds.x+w.bounds.width&&(!p.surface||r.id===p.surface))}
export function step(p:Pet,dt:number,w:World,mode:Mode,size:number,following:boolean){
 dt=Math.min(dt,.05);p.age+=dt;p.cooldown-=dt;
 const floor=w.work.y+w.work.height;
 if(p.state==='drag')return;
 if(mode==='nap'){if(p.state!=='sleep')enter(p,'sleep');p.surface=undefined;p.y=move(p.y,floor,dt);}
 else if(mode==='ceiling'||(mode==='free'&&w.fullscreen)){if(p.state!=='ceiling')enter(p,'ceiling');p.surface=undefined;p.y=move(p.y,w.bounds.y+size,dt);p.x+=p.direction*24*dt;}
 else if(mode==='pointer'){
 p.surface=undefined;if(p.state!=='walk'&&p.state!=='rest')enter(p,'walk');
 const tx=clamp(w.pointer.x+(p.seed-1.5)*(size*.85),w.work.x+size/2,w.work.x+w.work.width-size/2);
 if(following){p.direction=tx>=p.x?1:-1;p.x=move(p.x,tx,dt,2.3);p.y=move(p.y,clamp(w.pointer.y+size,w.work.y+size,floor),dt,2.3)}
 else {if(p.state!=='rest')enter(p,'rest');p.y=move(p.y,floor,dt)}
 }else {
 if(['sleep','ceiling'].includes(p.state))enter(p,'walk');
 let s=p.surface?w.windows.find(r=>r.id===p.surface):undefined;
 if(p.surface&&(!s||s.y<w.bounds.y+size||s.y>floor||s.width<size)){p.surface=undefined;s=undefined;enter(p,'walk');p.cooldown=5}
 if(p.state==='hang'){
  if(s){p.x=move(p.x,p.side==='left'?s.x-size*.3:s.x+s.width+size*.3,dt);p.y=move(p.y,s.y+size*.75,dt)}
  if(p.age>=1)enter(p,'climb');
 }else if(p.state==='climb'){
  if(s){const t=clamp(p.age/.9,0,1);const ease=t*t*(3-2*t);p.x=p.fromX+((p.side==='left'?s.x+size*.55:s.x+s.width-size*.55)-p.fromX)*ease;p.y=p.fromY+(s.y-p.fromY)*ease}
  if(p.age>=.9){enter(p,'walk');p.cooldown=10;if(s)p.y=s.y}
 }else if(p.state==='jump'){
  if(s){const t=clamp(p.age/.8,0,1);p.x=p.fromX+((p.side==='left'?s.x-size*.3:s.x+s.width+size*.3)-p.fromX)*t;p.y=p.fromY+(s.y+size*.75-p.fromY)*t-Math.sin(t*Math.PI)*60;}
  if(p.age>=.8)enter(p,'hang');
 }else{
  const base=s?s.y:floor;p.y=move(p.y,base,dt);
  if(p.state==='walk'){
   p.x+=p.direction*32*dt;
   if(s){const lo=s.x+size*.55,hi=s.x+s.width-size*.55;if(p.x<=lo||p.x>=hi)p.direction*=-1;p.x=clamp(p.x,lo,hi)}
   if(p.age>6+p.seed){enter(p,p.seed%2?'snack':'rest')}
  }else if(p.age>3.5)enter(p,'walk');
  if(!s&&p.cooldown<=0){const candidate=target(w,p,size);if(candidate){p.surface=candidate.id;p.side=p.x<candidate.x+candidate.width/2?'left':'right';enter(p,'jump')}else p.cooldown=3}
 }
 }
 const lo=w.bounds.x+size/2,hi=w.bounds.x+w.bounds.width-size/2;
 if(p.x<=lo||p.x>=hi)p.direction=p.x<=lo?1:-1;p.x=clamp(p.x,lo,hi);p.y=clamp(p.y,w.bounds.y+size,w.bounds.y+w.bounds.height);
}
export function sprite(p:Pet):{kind:string;frame:number;flip:boolean}{
 const frame=Math.floor(p.age*9);
 switch(p.state){
 case 'walk':return {kind:'walk-cycles',frame:frame%9,flip:p.direction<0};
 case 'hang':return {kind:p.side==='left'?'hang-left':'hang-right',frame:Math.floor(p.age*3)%3,flip:false};
 case 'climb':return {kind:'climb',frame:Math.min(2,Math.floor(p.age/.3)),flip:p.side==='right'};
 case 'sleep':return {kind:'lying',frame:Math.floor(p.age*.6)%3,flip:false};
 case 'ceiling':return {kind:'hang-ceiling',frame:Math.floor(p.age*2)%3,flip:false};
 default:return {kind:'characters',frame:p.state==='snack'?4:p.state==='rest'?0:2,flip:false};
 }
}
