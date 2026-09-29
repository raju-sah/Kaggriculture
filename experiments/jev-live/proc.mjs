// One-shot stdin processor: CLI-wrapped JSON -> {raw, hash, day_turn, yourTurn}, writes state file.
import fs from 'fs';
const out = process.argv[2];
let s = fs.readFileSync(0, 'utf8').trim();
const once = JSON.parse(s);
const j = typeof once === 'string' ? JSON.parse(once) : once;
if (out) fs.writeFileSync(out, JSON.stringify(j));
const k = {};
for (const c of j.cells || []) k[c.imgs || 'e'] = (k[c.imgs || 'e'] || 0) + 1;
const hash = j.day + '|' + JSON.stringify(k) + '|' + (j.units || []).map(u => u.val).join(',') + '|' + (j.money || []).join(',');
process.stdout.write(JSON.stringify({ hash, dt: j.day + '/' + j.turn, yt: !!j.yourTurn }));
