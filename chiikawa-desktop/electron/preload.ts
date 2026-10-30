import {contextBridge,ipcRenderer} from 'electron';
import type {DesktopAPI} from '../src/shared';
const subscribe=(channel:string,fn:(value:any)=>void)=>{const listener=(_:unknown,value:unknown)=>fn(value);ipcRenderer.on(channel,listener);return()=>ipcRenderer.removeListener(channel,listener)};
const api:DesktopAPI={initial:()=>ipcRenderer.invoke('initial'),set:s=>ipcRenderer.send('settings',s),action:a=>ipcRenderer.send('action',a),hit:h=>ipcRenderer.send('hit',h),onSettings:f=>subscribe('settings',f),onWorld:f=>subscribe('world',f),onAction:f=>subscribe('action',f)};
contextBridge.exposeInMainWorld('desktop',api);
