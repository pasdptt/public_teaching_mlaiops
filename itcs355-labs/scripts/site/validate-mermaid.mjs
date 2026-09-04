// Parse every ```mermaid block in the repo against mermaid's real grammar.
//
//   npm install mermaid jsdom
//   node scripts/site/validate-mermaid.mjs
//
// A diagram that fails to parse renders as raw text on the course website, which is
// worse than having no diagram. CI runs this on every push.

import { readFileSync, readdirSync, statSync } from 'fs';
import { join } from 'path';
import { JSDOM } from 'jsdom';

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', { pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
Object.defineProperty(global, "navigator", { value: dom.window.navigator, configurable: true });
global.HTMLElement = dom.window.HTMLElement;
global.SVGElement = dom.window.SVGElement;
global.Element = dom.window.Element;
global.Node = dom.window.Node;
global.DOMPurify = undefined;
global.requestAnimationFrame = (cb) => setTimeout(cb, 0);

const mermaid = (await import('mermaid')).default;
mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' });

function walk(dir, out = []) {
  for (const e of readdirSync(dir)) {
    if (e === 'node_modules' || e === '.git') continue;
    const p = join(dir, e);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (p.endsWith('.md')) out.push(p);
  }
  return out;
}

let total = 0, bad = 0;
for (const file of walk('.')) {
  const text = readFileSync(file, 'utf8');
  const blocks = [...text.matchAll(/```mermaid\n([\s\S]*?)```/g)].map(m => m[1]);
  for (const [i, b] of blocks.entries()) {
    total++;
    try {
      await mermaid.parse(b);
      console.log(`  OK   ${file} block ${i + 1}`);
    } catch (err) {
      bad++;
      console.log(`  FAIL ${file} block ${i + 1}`);
      console.log('        ' + String(err.message || err).split('\n')[0]);
    }
  }
}
console.log(`\n${total} parsed, ${bad} failed`);
process.exit(bad ? 1 : 0);
