import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';
const dir = '/home/z/my-project/workspace/asr_chunks';
const chunks = fs.readdirSync(dir).filter(f => f.startsWith('chunk_') && f.endsWith('.wav')).sort();
const zai = await ZAI.create();
for (const c of chunks) {
  try {
    const b64 = fs.readFileSync(`${dir}/${c}`).toString('base64');
    const r = await zai.audio.asr.create({ file_base64: b64 });
    console.log(c, '=>', String(r.text || JSON.stringify(r)).slice(0, 180));
  } catch (e) { console.log(c, 'ERR', String(e.message).slice(0, 100)); }
}
