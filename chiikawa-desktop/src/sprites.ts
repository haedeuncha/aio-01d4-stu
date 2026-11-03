import {ids} from './engine';
export interface Frame{canvas:HTMLCanvasElement;alpha:Uint8ClampedArray;width:number;height:number}
export const layouts:Record<string,[number,number]>={'characters':[4,2],'walk-cycles':[3,3],'hang-left':[3,1],'hang-right':[3,1],'hang-ceiling':[3,1],'lying':[3,1],'climb':[3,1]};
export const cache=new Map<string,Frame[]>();
export async function loadSprites(progress:(message:string)=>void){
 for(const id of ids)for(const [kind,[cols,rows]] of Object.entries(layouts)){
  progress(`${id} · ${kind}`);const img=new Image();img.src=`./assets/v2/${kind}/${id}.png`;await img.decode();
  const frames:Frame[]=[];
  for(let i=0;i<cols*rows;i++){
   const sx=Math.round(i%cols*img.width/cols),sy=Math.round(Math.floor(i/cols)*img.height/rows);
   const cw=Math.round((i%cols+1)*img.width/cols)-sx,ch=Math.round((Math.floor(i/cols)+1)*img.height/rows)-sy;
   const work=document.createElement('canvas');work.width=cw;work.height=ch;const c=work.getContext('2d',{willReadFrequently:true})!;c.drawImage(img,sx,sy,cw,ch,0,0,cw,ch);
   const data=c.getImageData(0,0,cw,ch).data;let left=cw,top=ch,right=0,bottom=0;
   for(let y=0;y<ch;y++)for(let x=0;x<cw;x++)if(data[(y*cw+x)*4+3]>32){left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y)}
   if(left>right)throw Error(`빈 프레임: ${id}/${kind}/${i}`);
   const width=right-left+1,height=bottom-top+1,out=document.createElement('canvas');
   const scale=Math.min(1,192/Math.max(width,height));out.width=Math.max(1,Math.round(width*scale));out.height=Math.max(1,Math.round(height*scale));
   const ctx=out.getContext('2d',{willReadFrequently:true})!;ctx.drawImage(work,left,top,width,height,0,0,out.width,out.height);
   frames.push({canvas:out,alpha:ctx.getImageData(0,0,out.width,out.height).data,width:out.width,height:out.height});work.width=0;
  }
  cache.set(`${id}/${kind}`,frames);img.src='';
 }
}
