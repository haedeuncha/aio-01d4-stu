import {test} from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import manifest from '../public/assets/sprite-manifest.json';
test('all 28 v2 sheets exist with declared dimensions and complete frame coverage',()=>{
 assert.equal(manifest.length,28);
 for(const sheet of manifest){const data=readFileSync('public/'+sheet.file);assert.equal(data.subarray(1,4).toString(),'PNG');assert.equal(data.readUInt32BE(16),sheet.width);assert.equal(data.readUInt32BE(20),sheet.height);assert.equal(sheet.frames,sheet.columns*sheet.rows);assert.equal(Math.round(sheet.columns*sheet.cellWidth),sheet.width)}
});
