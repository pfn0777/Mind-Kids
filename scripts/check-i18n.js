'use strict';
/* Validates the i18n data (I18N, LX, COLORS, SHAPE_N, def() name/desc) extracted straight
   out of mind-kids.html. Plain Node, no deps. Run: node scripts/check-i18n.js */
const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, '..', 'mind-kids.html');
const src = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');

const fails = [];
const ok = (cond, msg) => { if (!cond) fails.push(msg); };

function extractBalanced(label, startNeedle) {
  const start = src.indexOf(startNeedle);
  if (start === -1) throw new Error(`Could not find ${label} in mind-kids.html`);
  const braceStart = src.indexOf('{', start);
  let depth = 0, i = braceStart;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { i++; break; } }
  }
  return src.slice(braceStart, i);
}

// --- I18N ---
const i18nSrc = extractBalanced('I18N', 'const I18N=');
const I18N = (0, eval)('(' + i18nSrc + ')');
ok(I18N.uz && I18N.ru, 'I18N must have uz and ru tables');

const placeholders = s => (String(s).match(/\{[a-zA-Z_]+\}/g) || []).slice().sort().join(',');
for (const key of Object.keys(I18N.uz)) {
  if (!(key in I18N.ru)) { fails.push(`I18N.ru missing key: ${key}`); continue; }
  const pu = placeholders(I18N.uz[key]), pr = placeholders(I18N.ru[key]);
  if (pu !== pr) fails.push(`I18N.ru[${key}] placeholder mismatch: uz={${pu}} ru={${pr}}`);
}
for (const key of Object.keys(I18N.ru)) {
  if (!(key in I18N.uz)) fails.push(`I18N.ru has extra key not in uz: ${key}`);
}

// --- LX ---
const lxSrc = extractBalanced('LX', 'const LX=');
const LX = (0, eval)('(' + lxSrc + ')');
for (const lang of ['uz', 'ru']) {
  ok(LX[lang], `LX.${lang} missing`);
  ok(Array.isArray(LX[lang].ABC) && LX[lang].ABC.length > 0, `LX.${lang}.ABC must be non-empty`);
  ok(LX[lang].SIMILAR && Object.keys(LX[lang].SIMILAR).length > 0, `LX.${lang}.SIMILAR must be non-empty`);
  ok(Array.isArray(LX[lang].WORDS) && LX[lang].WORDS.length > 0, `LX.${lang}.WORDS must be non-empty`);
  ok(typeof LX[lang].toks === 'function', `LX.${lang}.toks must be a function`);
  // Every emoji in WORDS must be unique so a child can tell words apart by picture alone.
  const seenEmoji = new Map();
  for (const [word, emoji] of LX[lang].WORDS) {
    if (seenEmoji.has(emoji)) fails.push(`LX.${lang}.WORDS: emoji "${emoji}" reused by both "${seenEmoji.get(emoji)}" and "${word}"`);
    else seenEmoji.set(emoji, word);
  }
}
// WORDS length-group coverage: ru must have at least as many words as uz in each of the
// three filter buckets the games actually use (<=4, 5..6, >=6).
function bucket(words, toks, pred) {
  return words.filter(w => pred(toks(w[0]).length)).length;
}
const buckets = [
  ['<=4', n => n <= 4],
  ['5-6', n => n >= 5 && n <= 6],
  ['>=6', n => n >= 6]
];
for (const [label, pred] of buckets) {
  const uzN = bucket(LX.uz.WORDS, LX.uz.toks, pred);
  const ruN = bucket(LX.ru.WORDS, LX.ru.toks, pred);
  ok(ruN >= uzN, `LX.ru.WORDS bucket ${label}: ${ruN} words, need >= ${uzN} (uz has ${uzN})`);
}
// SIMILAR keys should reference letters that exist in ABC (sanity, not exhaustive coverage).
for (const lang of ['uz', 'ru']) {
  const abc = new Set(LX[lang].ABC);
  for (const k of Object.keys(LX[lang].SIMILAR)) {
    if (!abc.has(k)) fails.push(`LX.${lang}.SIMILAR key "${k}" not present in ABC`);
  }
}

// --- COLORS ---
const colorsSrc = extractBalanced('COLORS', 'const COLORS={');
const COLORS = (0, eval)('(' + colorsSrc + ')');
for (const [k, v] of Object.entries(COLORS)) {
  ok(v.hex && /^#[0-9a-f]{6}$/i.test(v.hex), `COLORS.${k}.hex missing/invalid`);
  ok(v.uz, `COLORS.${k}.uz missing`);
  ok(v.ru && v.ru.m && v.ru.f && v.ru.n, `COLORS.${k}.ru must have m/f/n`);
  ok(v.en, `COLORS.${k}.en missing`);
}

// --- SHAPE_N ---
const shapeSrc = extractBalanced('SHAPE_N', 'const SHAPE_N={');
const SHAPE_N = (0, eval)('(' + shapeSrc + ')');
for (const [k, v] of Object.entries(SHAPE_N)) {
  ok(v.uz, `SHAPE_N.${k}.uz missing`);
  ok(v.ru && v.ru.w && v.ru.g, `SHAPE_N.${k}.ru must have w (word) and g (gender)`);
  ok(['m', 'f', 'n'].includes(v.ru.g), `SHAPE_N.${k}.ru.g must be m/f/n, got "${v.ru && v.ru.g}"`);
}

// --- def({name:{uz,ru},desc:{uz,ru},...}) for all 37 games ---
const defRe = /def\(\{name:\{uz:'(?:[^'\\]|\\.)*',ru:'(?:[^'\\]|\\.)*'\},[\s\S]*?desc:\{uz:'(?:[^'\\]|\\.)*',ru:'(?:[^'\\]|\\.)*'\}/g;
const defMatches = src.match(/def\(\{name:\{/g) || [];
ok(defMatches.length === 37, `expected 37 def({name:{...}}) games, found ${defMatches.length}`);
const defFull = src.match(/def\(\{name:\{uz:/g) || [];
ok(defFull.length === 37, `expected 37 def({name:{uz:...}}) games, found ${defFull.length}`);
// every def(...) block's name/desc objects must contain both uz: and ru:
function extractObjAt(braceStart) {
  let depth = 0, i = braceStart;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { i++; break; } }
  }
  return src.slice(braceStart, i);
}
let idx = 0, gameNum = 0;
while (true) {
  idx = src.indexOf('def({name:{', idx);
  if (idx === -1) break;
  gameNum++;
  const nameBrace = idx + 'def({name:'.length;
  const nameObj = extractObjAt(nameBrace);
  ok(/uz:/.test(nameObj) && /ru:/.test(nameObj), `game #${gameNum}: name must have uz and ru`);
  const descAt = src.indexOf('desc:{', idx);
  const nextDefAt = src.indexOf('def({name:{', idx + 10);
  if (descAt !== -1 && (nextDefAt === -1 || descAt < nextDefAt)) {
    const descObj = extractObjAt(descAt + 'desc:'.length);
    ok(/uz:/.test(descObj) && /ru:/.test(descObj), `game #${gameNum}: desc must have uz and ru`);
  } else {
    fails.push(`game #${gameNum}: desc:{...} not found before next game`);
  }
  idx += 10;
}

if (fails.length) {
  console.error(`check-i18n: ${fails.length} failure(s)`);
  fails.forEach(f => console.error(' - ' + f));
  process.exit(1);
} else {
  console.log(`check-i18n: OK — I18N (${Object.keys(I18N.uz).length} keys), LX.uz/ru, COLORS (${Object.keys(COLORS).length}), SHAPE_N (${Object.keys(SHAPE_N).length}), ${defFull.length} games all have ru content.`);
}
