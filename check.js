// usage: node check.js index.html
// Runs the page's own solver on every puzzle and compares with the stored par.
const fs = require('fs');
const html = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
const size = +html.match(/const SIZE = (\d+);/)[1];
const solver = html.split('// SOLVER-START')[1].split('// SOLVER-END')[0];
const puzzles = JSON.parse(html.match(/const PUZZLES = (\[.*?\]);\n/s)[1]);
const solvePuzzle = new Function(solver + '; return solvePuzzle;')();
let bad = 0, slowest = 0;
puzzles.forEach((p, n) => {
  const cells = {};
  for (let i = 0; i < size * size; i++) if (p.grid[i] !== '.') (cells[p.grid[i]] = cells[p.grid[i]] || []).push(i);
  const ids = Object.keys(cells).sort((a, b) => (a === 'X' ? -1 : b === 'X' ? 1 : a < b ? -1 : 1));
  const meta = [], pos = [];
  ids.forEach(id => {
    const c = cells[id], h = c[1] - c[0] === 1;
    meta.push({ h, len: c.length, fixed: h ? (c[0] / size) | 0 : c[0] % size });
    pos.push(h ? c[0] % size : (c[0] / size) | 0);
  });
  const t = Date.now();
  const sol = solvePuzzle(meta, pos, size);
  const ms = Date.now() - t;
  slowest = Math.max(slowest, ms);
  if (!sol || sol.length !== p.par) { bad++; console.log('MISMATCH', n + 1, p.tier, p.par, sol && sol.length); }
});
console.log(puzzles.length, 'puzzles on a', size + 'x' + size, 'board,', bad, 'mismatches, slowest solve', slowest, 'ms');
[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach(m => new Function(m[1]));
console.log('page script parses');
