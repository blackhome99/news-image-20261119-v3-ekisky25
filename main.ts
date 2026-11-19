// "The World in One Day" — Thursday 19 November 2026 (news-image-01).
//
// The front page is rendered by build_news.py into entry.png beside this
// file (33 verified stories of 19 Nov 2026: 3 leads, 10 small cards,
// 20 numbered briefs, a numbered world map, a DATE CHECK strip).
// This entrypoint copies that exact image to the output directory,
// deterministically: same input bytes, same output bytes, no network,
// no timestamps, no randomness.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { closeSync, copyFileSync, mkdirSync, openSync, readSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, 'entry.png');
copyFileSync(new URL('./entry.png', import.meta.url), dest);
// Fail loudly instead of shipping a truncated copy: the gate rejects
// anything that is not a whole image, so verify size and PNG signature.
const copied = statSync(dest);
if (copied.size === 0 || copied.size > 1048576) {
  throw new Error(`entry.png copy has unexpected size ${copied.size}`);
}
const fd = openSync(dest, 'r');
const head = Buffer.alloc(8);
readSync(fd, head, 0, 8, 0);
closeSync(fd);
const pngSig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!head.equals(pngSig)) {
  throw new Error('entry.png copy is not a PNG file');
}
console.log(`copied entry.png -> ${dest} (${copied.size} bytes)`);
