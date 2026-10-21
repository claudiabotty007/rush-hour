const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const solver = html.split('// SOLVER-START')[1].split('// SOLVER-END')[0];
const puzzles = JSON.parse(html.match(/const PUZZLES = (\[.*?\]);\n/s)[1]);
const solvePuzzle = new Function(solver + '; return solvePuzzle;')();
let bad = 0;
puzzles.forEach((p, n) => {
  const cells = {};
  for (let i = 0; i < 36; i++) if (p.grid[i] !== '.') (cells[p.grid[i]] = cells[p.grid[i]] || []).push(i);
  const ids = Object.keys(cells).sort((a, b) => (a === 'X' ? -1 : b === 'X' ? 1 : a < b ? -1 : 1));
  const meta = [], pos = [];
  ids.forEach(id => {
    const c = cells[id], h = c[1] - c[0] === 1;
    meta.push({ h, len: c.length, fixed: h ? (c[0] / 6) | 0 : c[0] % 6 });
    pos.push(h ? c[0] % 6 : (c[0] / 6) | 0);
  });
  const sol = solvePuzzle(meta, pos);
  if (!sol || sol.length !== p.par) { bad++; console.log('MISMATCH', n + 1, p.tier, p.par, sol && sol.length); }
});
console.log(puzzles.length, 'puzzles checked,', bad, 'mismatches');
// syntax check of the whole page script
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
scripts.forEach(s => new Function(s));
console.log('page script parses');
