// 素材包构建：node tools/pack/build-pack.mjs "<项目名>" [输出目录]
// 临时在 8099 起静态服务，用软件渲染的无头 Chrome 跑 export.html（GPU 路径偶发丢上下文，读回全透明 / 贴图变黑），约 1–2 分钟。
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const PROJECT = process.argv[2] || '示例项目';
const OUT = path.resolve(process.argv[3] || path.join(ROOT, 'exports', `${PROJECT}_素材包`));
const STATES_DIR = path.join(ROOT, 'exports', `${PROJECT}_状态版`);
const PORT = 8099;
const srv = spawn('python3', ['serve.py', String(PORT)], { cwd: ROOT, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 1200));
let browser;
try {
  browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await (await browser.newContext({ viewport: { width: 1200, height: 1200 } })).newPage();
  page.on('pageerror', e => console.log('pageerror', e.message));
  page.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
  await page.goto(`http://127.0.0.1:${PORT}/tools/pack/export.html`);
  const res = await page.evaluate(() => window.__pack);
  fs.rmSync(OUT, { recursive: true, force: true }); fs.rmSync(STATES_DIR, { recursive: true, force: true });
  for (const [f, b64] of Object.entries(res.files)) {
    const p = f.startsWith('__states/') ? path.join(STATES_DIR, f.slice(9)) : path.join(OUT, f);
    fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, Buffer.from(b64, 'base64'));
  }
  fs.writeFileSync(path.join(OUT, 'layout.json'), JSON.stringify(res.layout, null, 2));
  fs.writeFileSync(path.join(OUT, 'tags.json'), JSON.stringify(res.tags, null, 2));
  const q = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
  fs.writeFileSync(path.join(OUT, 'tags.csv'), '﻿id,name,unit,type\n' + res.tags.map(t => [t.id, t.name, t.unit, t.type].map(q).join(',')).join('\n') + '\n');
  const readme = path.join(ROOT, 'tools/pack/README.md');
  if (fs.existsSync(readme)) fs.writeFileSync(path.join(OUT, 'README.md'), fs.readFileSync(readme, 'utf8').replaceAll('{{PROJECT}}', PROJECT));
  console.log('written', Object.keys(res.files).length, 'files →', OUT);
} finally { await browser?.close(); srv.kill(); }
