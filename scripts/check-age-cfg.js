'use strict';
/* Validates AGE_CFG (difficulty table for games 31-37) extracted straight out of
   mind-kids.html. Plain Node, no deps. Run: node scripts/check-age-cfg.js */
const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, '..', 'mind-kids.html');
const src = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');

function extract(label, re) {
  const m = src.match(re);
  if (!m) throw new Error(`Could not find ${label} in mind-kids.html`);
  return m[1];
}

const lerpSrc = extract('lerp', /const lerp=(\([^\n]*?\)=>[^\n]*?);\n/);
const cfgStart = src.indexOf('const AGE_CFG={');
if (cfgStart === -1) throw new Error('Could not find AGE_CFG in mind-kids.html');
const cfgEnd = src.indexOf('\n};', cfgStart);
if (cfgEnd === -1) throw new Error('Could not find end of AGE_CFG literal');
const cfgSrc = src.slice(cfgStart + 'const AGE_CFG='.length, cfgEnd + 2);

const lerp = (0, eval)(lerpSrc);
const AGE_CFG = (0, eval)('(' + cfgSrc + ')');

const AGES = ['4-6', '7-9', '10-12'];
const LEVELS = [1,2,3,4,5,6,7,8,9,10];
const fails = [];
const ok = (cond, msg) => { if (!cond) fails.push(msg); };
const isGrid = n => Number.isInteger(n) && n >= 3 && n <= 6;

for (const age of AGES) {
  // 31 Schulte jadvali — grid grows from n1 to n2 at level `split`.
  {
    const c = AGE_CFG.schulte[age];
    ok(isGrid(c.n1) && isGrid(c.n2), `schulte/${age}: grid size out of 3..6 range`);
    ok(c.time > 0, `schulte/${age}: time must be > 0`);
    for (const L of LEVELS) {
      const n = L < c.split ? c.n1 : c.n2;
      ok(isGrid(n), `schulte/${age}/L${L}: grid ${n} not in 3..6`);
    }
  }
  // 32 Rang chalg'itadi — number of color choices (bounded by available palette).
  {
    const c = AGE_CFG.colors[age];
    ok(c.time > 0, `colors/${age}: time must be > 0`);
    for (const L of LEVELS) {
      const n = Math.min(lerp(c.n1, c.n2, L), 7);
      ok(n >= 2 && n <= 7, `colors/${age}/L${L}: option count ${n} out of range`);
    }
  }
  // 33 Yodda qo'sh — sequence of numbers to sum.
  {
    const c = AGE_CFG.mathmem[age];
    ok(c.min >= 1 && c.min <= c.max, `mathmem/${age}: min/max invalid`);
    ok(c.dur > 0, `mathmem/${age}: dur must be > 0`);
    ok(c.gap > 0, `mathmem/${age}: gap must be > 0`);
    ok(c.ans > 0, `mathmem/${age}: ans time must be > 0`);
    ok(c.opts === 3 || c.opts === 4, `mathmem/${age}: opts must be 3 or 4`);
    for (const L of LEVELS) {
      const cnt = lerp(c.c1, c.c2, L);
      ok(cnt >= 1, `mathmem/${age}/L${L}: count ${cnt} must be >= 1`);
    }
  }
  // 34 Sonlar joyi — N numbers placed on an n×n grid, count must fit the grid.
  {
    const c = AGE_CFG.numpos[age];
    ok(isGrid(c.n), `numpos/${age}: grid size out of 3..6 range`);
    ok(c.show > 0, `numpos/${age}: show time must be > 0`);
    for (const L of LEVELS) {
      const cnt = Math.min(lerp(c.c1, c.c2, L), c.n * c.n);
      ok(cnt >= 1 && cnt <= c.n * c.n, `numpos/${age}/L${L}: count ${cnt} exceeds ${c.n * c.n} cells`);
    }
  }
  // 35 Qora kataklar — black cells on an n×n grid, count must fit the grid.
  {
    const c = AGE_CFG.pattern[age];
    ok(isGrid(c.n), `pattern/${age}: grid size out of 3..6 range`);
    ok(c.show > 0, `pattern/${age}: show time must be > 0`);
    for (const L of LEVELS) {
      const cnt = Math.min(lerp(c.c1, c.c2, L), c.n * c.n);
      ok(cnt >= 1 && cnt <= c.n * c.n, `pattern/${age}/L${L}: count ${cnt} exceeds ${c.n * c.n} cells`);
    }
  }
  // 36 Chivin yo'li — n×n grid, arrow-step count and per-step speed.
  {
    const c = AGE_CFG.fly[age];
    ok(isGrid(c.n), `fly/${age}: grid size out of 3..6 range`);
    ok(c.speed > 0, `fly/${age}: speed must be > 0`);
    ok(c.ans > 0, `fly/${age}: answer time must be > 0`);
    ok(typeof c.diag === 'boolean', `fly/${age}: diag must be a boolean`);
    ok(c.diag === (age !== '4-6'), `fly/${age}: diag should be false only for 4-6 (diagonals too hard at that age)`);
    for (const L of LEVELS) {
      const cnt = lerp(c.c1, c.c2, L);
      ok(cnt >= 1, `fly/${age}/L${L}: step count ${cnt} must be >= 1`);
    }
  }
  // 37 Og'zaki hisob — arithmetic operand ranges per operation.
  {
    const c = AGE_CFG.mental[age];
    ok(c.time > 0, `mental/${age}: time must be > 0`);
    for (const op of ['add', 'sub', 'mul', 'div']) {
      if (!c[op]) continue;
      ok(c[op].min >= 1 && c[op].min <= c[op].max, `mental/${age}/${op}: min/max invalid`);
    }
    // 4-6 and 7-9 cap the addition RESULT at add.max (x=ri(min,max-min), y=ri(min,max-x)),
    // which only produces a valid ri() range when max-min >= min.
    if (age !== '10-12') {
      ok(c.add.max - c.add.min >= c.add.min, `mental/${age}/add: max-min must be >= min for the capped-sum formula`);
    }
  }
}

if (fails.length) {
  console.error(`check-age-cfg: ${fails.length} failure(s)`);
  fails.forEach(f => console.error(' - ' + f));
  process.exit(1);
} else {
  const games = Object.keys(AGE_CFG).length;
  console.log(`check-age-cfg: OK — ${games} games x ${AGES.length} ages x ${LEVELS.length} levels all within bounds.`);
}
