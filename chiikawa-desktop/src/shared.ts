export const modes=['free','pointer','ceiling','nap'] as const;
export type Mode=typeof modes[number];
export const labels:Record<Mode,string>={free:'자유 산책',pointer:'따라오기',ceiling:'천장 산책',nap:'낮잠 시간'};
export interface Settings {mode:Mode;fps:30|60;size:number;hidden:boolean}
export const defaults:Settings={mode:'free',fps:60,size:96,hidden:false};
export function sanitize(input:unknown):Settings {
 const v=(input && typeof input==='object'?input:{}) as Partial<Settings>;
 return {mode:modes.includes(v.mode as Mode)?v.mode!:defaults.mode,fps:v.fps===30?30:60,size:typeof v.size==='number'&&Number.isFinite(v.size)?Math.min(160,Math.max(64,v.size)):96,hidden:v.hidden===true};
}
export interface Rect{x:number;y:number;width:number;height:number}
export interface Surface extends Rect{id:string}
export interface World{bounds:Rect;work:Rect;pointer:{x:number;y:number};windows:Surface[];fullscreen:boolean;tracker:string}
export interface DesktopAPI{initial:()=>Promise<{settings:Settings;world:World}>;set:(settings:Partial<Settings>)=>void;action:(action:'gather'|'resume'|'pause'|'quit'|'settings')=>void;hit:(hit:boolean)=>void;onSettings:(fn:(s:Settings)=>void)=>()=>void;onWorld:(fn:(w:World)=>void)=>()=>void;onAction:(fn:(action:string)=>void)=>()=>void;}
declare global{interface Window{desktop?:DesktopAPI}}
