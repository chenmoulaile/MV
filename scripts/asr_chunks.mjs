import fs from 'fs';
import { execSync } from 'child_process';
const dir = '/home/z/my-project/workspace/asr_chunks';
const chunks = fs.readdirSync(dir).filter(f => f.startsWith('chunk_') && f.endsWith('.wav')).sort();
for (const c of chunks) {
  try {
    const out = execSync(`z-ai asr -f ${dir}/${c}`, { encoding: 'utf8', timeout: 120000, maxBuffer: 10*1024*1024 });
    const j = JSON.parse(out);
    console.log(c, '=>', (j.text || JSON.stringify(j)).slice(0, 200));
  } catch (e) {
    console.log(c, 'ERR', String(e.stdout || e.message).slice(0, 150));
  }
}
