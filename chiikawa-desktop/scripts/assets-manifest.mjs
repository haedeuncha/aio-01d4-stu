import {readdirSync,readFileSync,writeFileSync} from 'node:fs';
const layouts={'characters':[4,2],'walk-cycles':[3,3],'hang-left':[3,1],'hang-right':[3,1],'hang-ceiling':[3,1],lying:[3,1],climb:[3,1]};
const manifest=[];
for(const [kind,[columns,rows]] of Object.entries(layouts))for(const name of readdirSync(`public/assets/v2/${kind}`)){
 const data=readFileSync(`public/assets/v2/${kind}/${name}`);const width=data.readUInt32BE(16),height=data.readUInt32BE(20);
 manifest.push({file:`assets/v2/${kind}/${name}`,width,height,columns,rows,frames:columns*rows,cellWidth:width/columns,cellHeight:height/rows,pixelBoundaries:'round(index * dimension / count)',alphaThreshold:32,maxDecodedFrameDimension:192});
}
writeFileSync('public/assets/sprite-manifest.json',JSON.stringify(manifest,null,2));
