import { defineConfig } from 'vite';
export default defineConfig({base:'./',server:{host:'127.0.0.1',port:5173,strictPort:true,watch:{ignored:['**/*.tmp','**/*.temp','**/*.part','**/*.crdownload','**/*.log','**/.runtime/**','**/.npm-cache/**','**/.electron-cache/**','**/dist/**','**/dist-electron/**']}},build:{target:'es2022'}});
