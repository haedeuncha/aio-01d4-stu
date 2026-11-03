import {app,BrowserWindow,Tray,Menu,ipcMain,globalShortcut,screen,nativeImage} from 'electron';
import {readFileSync,writeFileSync,renameSync,mkdirSync,appendFileSync} from 'node:fs';
import path from 'node:path';
import {spawn,type ChildProcess} from 'node:child_process';
import {createInterface} from 'node:readline';
import {defaults,sanitize,modes,labels,type Settings,type World,type Surface} from '../src/shared';
const root=path.join(__dirname,'..');
// A portable profile keeps settings beside this source project.
const profile=path.join(root,'.runtime');mkdirSync(profile,{recursive:true});app.setPath('userData',profile);
let settings:Settings={...defaults},tray:Tray, panel:BrowserWindow|undefined,worker:ChildProcess|undefined;
let windows:(Surface&{foreground:boolean})[]=[],tracker='시작 중';
const overlays=new Map<number,BrowserWindow>();
let timer:ReturnType<typeof setInterval>;
const config=()=>path.join(app.getPath('userData'),'settings.json');
function log(message:string){appendFileSync(path.join(app.getPath('userData'),'desktop.log'),`${new Date().toISOString()} ${message}\n`)}
function broadcast(channel:string,value:unknown){for(const w of BrowserWindow.getAllWindows())if(!w.isDestroyed())w.webContents.send(channel,value)}
function update(patch:Partial<Settings>){settings=sanitize({...settings,...patch});const tmp=config()+'.tmp';writeFileSync(tmp,JSON.stringify(settings));renameSync(tmp,config());for(const w of overlays.values())settings.hidden?w.hide():w.showInactive();broadcast('settings',settings);menu()}
function worldFor(w:BrowserWindow):World {
 const d=screen.getDisplayMatching(w.getBounds());const b=d.bounds;
 const visible=windows.filter(r=>r.x+r.width>b.x&&r.x<b.x+b.width&&r.y+r.height>b.y&&r.y<b.y+b.height);
 return {bounds:b,work:d.workArea,pointer:screen.getCursorScreenPoint(),windows:visible,fullscreen:visible.some(r=>r.foreground&&r.x<=b.x+2&&r.y<=b.y+2&&r.width>=b.width-4&&r.height>=b.height-4),tracker};
}
function load(w:BrowserWindow,view:string){w.webContents.setWindowOpenHandler(()=>({action:'deny'}));w.webContents.on('will-navigate',e=>e.preventDefault());w.webContents.on('render-process-gone',(_,d)=>log('renderer gone '+d.reason));w.webContents.on('did-fail-load',(_,code,desc)=>log(`load failed ${code} ${desc}`));const dev=process.env.VITE_DEV_SERVER_URL;if(dev)void w.loadURL(`${dev}/?view=${view}`);else void w.loadFile(path.join(root,'dist/index.html'),{query:{view}});}
const prefs=()=>({preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true});
function displays(){for(const w of overlays.values())w.destroy();overlays.clear();for(const d of screen.getAllDisplays()){
 const w=new BrowserWindow({...d.bounds,transparent:true,frame:false,alwaysOnTop:true,skipTaskbar:true,focusable:false,resizable:false,hasShadow:false,show:false,webPreferences:prefs()});
 overlays.set(d.id,w);w.setIgnoreMouseEvents(true,{forward:true});w.setAlwaysOnTop(true,'screen-saver');load(w,'overlay');w.once('ready-to-show',()=>{if(!settings.hidden)w.showInactive();log('overlay ready '+d.id)});
}}
function settingsWindow(){if(panel&&!panel.isDestroyed()){panel.show();panel.focus();return}panel=new BrowserWindow({width:570,height:650,title:'치이카와 · 설정',backgroundColor:'#fffaf4',autoHideMenuBar:true,show:true,webPreferences:prefs()});const current=panel;current.webContents.once('did-finish-load',()=>{current.show();current.focus();log('settings loaded')});load(current,'settings');current.on('closed',()=>{panel=undefined})}
function action(a:string){if(a==='quit')app.quit();else if(a==='settings')settingsWindow();else if(a==='gather'||a==='resume'||a==='pause')broadcast('action',a)}
function menu(){if(!tray)return;tray.setContextMenu(Menu.buildFromTemplate([...modes.map(mode=>({label:labels[mode],type:'radio' as const,checked:settings.mode===mode,click:()=>update({mode})})),{type:'separator'},{label:'다시 따라오기',click:()=>{update({mode:'pointer'});action('resume')}},{label:'캐릭터 모으기',click:()=>action('gather')},{label:settings.hidden?'표시':'숨기기',click:()=>update({hidden:!settings.hidden})},{label:'설정',click:settingsWindow},{type:'separator'},{label:'종료',click:()=>app.quit()}]))}
if(!app.requestSingleInstanceLock())app.quit();else {
app.on('second-instance',settingsWindow);
app.whenReady().then(()=>{
 mkdirSync(app.getPath('userData'),{recursive:true});try{settings=sanitize(JSON.parse(readFileSync(config(),'utf8')))}catch{};
 const trusted=(sender:Electron.WebContents)=>BrowserWindow.getAllWindows().some(w=>w.webContents===sender);
 ipcMain.handle('initial',e=>{const w=BrowserWindow.fromWebContents(e.sender);if(!w)throw Error('Unknown sender');return {settings,world:worldFor(w)}});
 ipcMain.on('settings',(e,v)=>{if(trusted(e.sender)&&v&&typeof v==='object')update(v)});
 ipcMain.on('action',(e,a)=>{if(trusted(e.sender)&&typeof a==='string')action(a)});
 ipcMain.on('hit',(e,v)=>{const w=BrowserWindow.fromWebContents(e.sender);if(w&&[...overlays.values()].includes(w)&&typeof v==='boolean')w.setIgnoreMouseEvents(!v,{forward:true})});
 displays();tray=new Tray(nativeImage.createFromPath(path.join(root,'public/assets/brand/app-icon.png')).resize({width:24,height:24}));tray.setToolTip('치이카와 · 작은 친구들');tray.on('double-click',settingsWindow);menu();
 for(const [key,fn] of Object.entries({'M':()=>update({mode:modes[(modes.indexOf(settings.mode)+1)%4]}),'G':()=>action('gather'),'H':()=>update({hidden:!settings.hidden}),'Q':()=>app.quit()}))if(!globalShortcut.register('Control+Alt+'+key,fn))log('Shortcut unavailable '+key);
 if(process.platform==='win32'){
 worker=spawn('powershell.exe',['-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',path.join(root,'scripts/windows.ps1'),String(process.pid)],{windowsHide:true,stdio:['ignore','pipe','pipe']});
 createInterface({input:worker.stdout!}).on('line',line=>{try{const rows=JSON.parse(line);windows=rows.map((r:Surface&{foreground:boolean})=>({...r,...screen.screenToDipRect(null,r)}));tracker='Windows 창 추적 활성'}catch{}});
 worker.stderr?.on('data',d=>{tracker='창 추적 오류 — 바닥 산책 사용';log(String(d))});worker.on('error',e=>{tracker='창 추적 실패';log(e.message)});worker.on('exit',()=>{windows=[];tracker='창 추적 중지'});
 }else tracker='Windows 전용 기능 비활성';
 let ticks=0;
 timer=setInterval(()=>{if(!settings.hidden)for(const w of overlays.values())if(!w.webContents.isLoading())w.webContents.send('world',worldFor(w));if(++ticks%30===0&&panel&&!panel.isDestroyed()&&!panel.webContents.isLoading())panel.webContents.send('world',worldFor(panel))},33);
 screen.on('display-added',displays);screen.on('display-removed',displays);screen.on('display-metrics-changed',displays);
 if(process.argv.includes('--settings')||process.env.CHIIKAWA_SETTINGS==='1')settingsWindow();
 setTimeout(()=>log(JSON.stringify({tracker,trackedWindows:windows.length,windows:BrowserWindow.getAllWindows().map(w=>({title:w.getTitle(),visible:w.isVisible(),loading:w.webContents.isLoading(),url:w.webContents.getURL()}))})),5000);
 log('app ready');
});
app.on('window-all-closed',()=>{});
app.on('will-quit',()=>{clearInterval(timer);globalShortcut.unregisterAll();worker?.kill();tray?.destroy()});
}
