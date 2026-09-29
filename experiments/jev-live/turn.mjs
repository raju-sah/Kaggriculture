// Turn glue v1: stdin = state_read.js JSON. Prints compact state + Jev verdict + action.
// Run: playwright read > state.json; node turn.mjs < state.json
// Browser actuation (React-safe) via playwright run-code snippets in ACTUATE_* below.
import { experimental_evaluate as evaluate } from 'ai';
import fs from 'fs';

const raw = JSON.parse(fs.readFileSync(0, 'utf8'));
// compact: count img kinds instead of dumping 400 cells
const kind = {};
for (const c of raw.cells || []) {
  const k = c.imgs || 'empty';
  kind[k] = (kind[k] || 0) + 1;
}
const farmerCell = (raw.cells || []).find(c => /farmer/i.test(c.imgs));
const state = [
  `Day ${raw.day}/${raw.days} Turn ${raw.turn} Money P1=${(raw.money||[])[0] ?? '?'} yourTurn=${raw.yourTurn}`,
  `Farmer@${farmerCell ? farmerCell.r + ',' + farmerCell.c : '?'}`,
  `Units=${(raw.units||[]).map(u=>u.id.split('-').pop()+':'+u.val).join(' ')}`,
  `Grid=${Object.entries(kind).slice(0,25).map(([k,v])=>k+'x'+v).join(' ')}`,
  `Prices=${JSON.stringify(raw.prices||{})}`,
].join('\n');

const result = await evaluate({
  model: 'typesafe-ai/jev',
  state,
  questions: {
    feed_urgent: { type: 'boolean', instructions: 'Any animal 1 day from escape?' },
    water_urgent: { type: 'boolean', instructions: 'Any TODAY-plant dying tonight unwatered?' },
    tactic: { type: 'choice', instructions: 'Pick tactic.',
      criteria: { feed: 'Feed animals', water: 'Water plants', harvest: 'Harvest', build: 'Build pasture/coop', place: 'Place animal', plant: 'Plant seeds', market: 'Market/hire/buy', move: 'Move', pass: 'Pass' } },
  },
});
const a = result.answers;
// Rule mapper mirrors main.py:774 _bridge_agent priority: feed > fresh-water > harvest > build/place > plant > pass.
// Jev tactic breaks ties / overrides when probability strong.
let op = 'PASS', arg = null;
const t = a.tactic?.choice;
if (a.feed_urgent?.probability > 0.6 || t === 'feed') op = 'FEED';
else if (a.water_urgent?.probability > 0.6 || t === 'water') op = 'WATER';
else if (t && ['harvest','build','place','plant','market','move'].includes(t)) op = t.toUpperCase();
console.log(JSON.stringify({ state, jev: a, action: { op, arg }, usage: result.usage }));

export const ACTUATE_SET_OP = `/* run-code in playable frame:
(sid, op) => { const s = document.querySelector('select#'+CSS.escape(sid)); if(!s) return 'no-sel';
  const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(s),'value')?.set
    || Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value')?.set;
  setter.call(s, op); s.dispatchEvent(new Event('change',{bubbles:true})); return 'set:'+s.value; } */`;
export const ACTUATE_SUBMIT = `/* click button.submit-turn in playable frame, then verify turn counter increments */`;
