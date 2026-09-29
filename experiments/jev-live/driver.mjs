// v3 driver: hands work water/harvest, shed-driven SELL, rebuy caps, money log.
// v2 (seed 4348/headless1 eras) superseded. loop.sh deprecated.
// Run: JEV_SESSION=jevhl node driver.mjs /abs/runs/30d-v3 720
import { execFile } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import { experimental_evaluate as evaluate } from 'ai';
const sh = promisify(execFile);
const SESS = process.env.JEV_SESSION || 'jev';

const [RUN_DIR, MAX] = [process.argv[2], +(process.argv[3] || 720)];
fs.mkdirSync(RUN_DIR, { recursive: true });
const LOG = `${RUN_DIR}/turns.jsonl`;
const LEDGER_P = `${RUN_DIR}/ledger.json`;
let ledger = { WHEAT: { b: 0, u: 0 }, MELON: { b: 0, u: 0 } };
try { ledger = JSON.parse(fs.readFileSync(LEDGER_P, 'utf8')); } catch {}
const saveLedger = () => fs.writeFileSync(LEDGER_P, JSON.stringify(ledger));
const seedsEst = (c) => ledger[c].b - ledger[c].u;
let shedCache = {}; // ITEM -> count (produce only)

const SMART = (H) => `async page => { const f = page.frames().find(x=>x.url().includes('playable')); return await f.evaluate(async (LASTHASH) => {
  const sleep = ms => new Promise(r=>setTimeout(r,ms));
  const snap = () => { const t=document.body.innerText; const dm=t.match(/Day\\s*(\\d+)\\s*\\/\\s*(\\d+)/); const tm=t.match(/Turn\\s*(\\d+)\\s*\\/\\s*(\\d+)/);
    return {t, day:dm?+dm[1]:0, days:dm?+dm[2]:0, turn:tm?+tm[1]:0, your:/Your turn/.test(t)}; };
  let s=snap(), w=0;
  while(!s.your && w<90000){ await sleep(500); w+=500; s=snap(); }
  if(!s.your) return JSON.stringify({wait_timeout:true, dt:s.day+'/'+s.turn});
  const p1=document.querySelector('.farm-panel[data-player="1"]');
  const p2=document.querySelector('.farm-panel[data-player="2"]');
  const cells=[...p1.querySelectorAll('.cell')].map(c=>({r:+c.dataset.row,c:+c.dataset.col,
    imgs:[...c.querySelectorAll('img')].map(i=>i.alt).filter(Boolean).join('+'),
    t:[...c.querySelectorAll('img')].map(i=>i.title).filter(Boolean).join('|')}));
  const m1=(p1.innerText.match(/(\\d{2,7})/)||[])[1], m2=(p2.innerText.match(/(\\d{2,7})/)||[])[1];
  const units=[...document.querySelectorAll('select[id*="-op"]')].map(x=>({id:x.id,val:x.value}));
  const mktRows=document.querySelectorAll('.action-section .action-row').length;
  const k={}; cells.forEach(c=>{k[c.imgs||'e']=(k[c.imgs||'e']||0)+1});
  const hash=s.day+'|'+JSON.stringify(k)+'|'+units.map(u=>u.val).join(',')+'|'+m1;
  const dt=s.day+'/'+s.turn;
  const setS=(el,v)=>{const d=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el),'value')||Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value');d.set.call(el,v);el.dispatchEvent(new Event('change',{bubbles:true}));};
  if(hash===LASTHASH){
    [...document.querySelectorAll('select[id*="-op"]')].forEach(el=>{if([...el.options].some(o=>o.value==='PASS'))setS(el,'PASS');});
    document.querySelector('button.submit-turn').click();
    let s2=snap(), w2=0;
    while((s2.day+'/'+s2.turn)===dt && w2<30000){await sleep(500);w2+=500;s2=snap();}
    return JSON.stringify({cached:1, dt, advanced:s2.day+'/'+s2.turn});
  }
  return JSON.stringify({cached:0, dt, state:{day:s.day,days:s.days,turn:s.turn,money1:+m1||0,money2:+(m2||0),cells,units,mktRows}});
}, ${H}); }`;

// SHED(): open shed dialog, read slots, close. Returns {ITEM:count} produce+seeds by title.
const SHED = `async page => { const f = page.frames().find(x=>x.url().includes('playable')); return await f.evaluate(async () => {
  const sleep = ms => new Promise(r=>setTimeout(r,ms));
  [...document.querySelectorAll('button')].filter(b=>b.textContent.trim()==='Shed')[0]?.click();
  await sleep(600);
  const out={};
  [...document.querySelectorAll('.inventory-slot')].forEach(sl=>{
    const img=sl.querySelector('.item-icon img'); if(!img) return;
    const n=parseInt((sl.querySelector('.item-count')?.innerText||'0').trim())||0;
    if(n>0) out[img.title||img.alt]=n;
  });
  [...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='×')?.click();
  await sleep(300);
  return JSON.stringify(out);
}); }`;

// ACT(units, orders): units=[{op,arg}] aligned to selects; hands PASS default.
const ACT = (UNITS, ORDERS) => `async page => { const f = page.frames().find(x=>x.url().includes('playable')); return await f.evaluate(async (P) => {
  const sleep = ms => new Promise(r=>setTimeout(r,ms));
  const setS=(el,v)=>{const d=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el),'value')||Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value');d.set.call(el,v);el.dispatchEvent(new Event('change',{bubbles:true}));};
  const dt0=(()=>{const t=document.body.innerText;const dm=t.match(/Day\\s*(\\d+)/);const tm=t.match(/Turn\\s*(\\d+)/);return (dm?dm[1]:0)+'/'+(tm?tm[1]:0);})();
  [...document.querySelectorAll('.action-section .action-row button')].filter(b=>b.textContent.trim()==='×').forEach(b=>b.click());
  await sleep(400);
  for(const o of P.orders){
    const add=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='+ Add');
    if(!add) break; add.click(); await sleep(300);
    const rows=[...document.querySelectorAll('.action-section .action-row')];
    if(!rows.length) break;
    const r=rows[rows.length-1]; const sels=[...r.querySelectorAll('select')];
    if([...sels[0].options].some(x=>x.value===o.op)) setS(sels[0],o.op);
    if(sels[1]&&o.item&&[...sels[1].options].some(x=>x.value===o.item)) setS(sels[1],o.item);
    const q=r.querySelector('input[type=number]'); if(q&&o.qty){q.focus();q.value=o.qty;q.dispatchEvent(new Event('input',{bubbles:true}));q.dispatchEvent(new Event('change',{bubbles:true}));}
  }
  const sels=[...document.querySelectorAll('select[id*="-op"]')];
  const got=[];
  sels.forEach((el,i)=>{ const u=P.units[i]||{op:'PASS'}; const v=[...el.options].some(o=>o.value===u.op)?u.op:'PASS'; setS(el,v); got.push(v);
    if(['PLANT','PICKUP','PLACE'].includes(v)&&u.arg){ const a=el.parentElement.querySelectorAll('select')[1];
      if(a&&[...a.options].some(o=>o.value===u.arg)) setS(a,u.arg); } });
  document.querySelector('button.submit-turn').click();
  const setStr=got.join(',');
  let w=0,cur=dt0;
  const snap=()=>{const t=document.body.innerText;const dm=t.match(/Day\\s*(\\d+)/);const tm=t.match(/Turn\\s*(\\d+)/);return (dm?dm[1]:0)+'/'+(tm?tm[1]:0);};
  while(cur===dt0&&w<30000){await sleep(500);w+=500;cur=snap();}
  return JSON.stringify({set:setStr, advanced:cur});
}, ${JSON.stringify({ units: UNITS, orders: ORDERS })}); }`;

async function cli(code) {
  const { stdout } = await sh('playwright-cli', [`-s=${SESS}`, 'run-code', code, '--raw'], { timeout: 150000 });
  const s = stdout.trim();
  const once = JSON.parse(s);
  return typeof once === 'string' ? JSON.parse(once) : once;
}

async function vote(text) {
  const result = await evaluate({
    model: 'typesafe-ai/jev', state: text,
    questions: {
      harvest_due: { type: 'boolean', instructions: 'Any mature crop/animal product that decays if skipped?' },
      water_urgent: { type: 'boolean', instructions: 'Any dry crop at death/decay risk tonight?' },
      tactic: { type: 'choice', instructions: 'Pick tactic.',
        criteria: { harvest: 'Harvest mature first', water: 'Water dry crops', plant: 'Plant empty soil', dig: 'Clear weeds', build: 'Build structures', market: 'Market/hire/buy', move: 'Move to target', pass: 'Pass' } },
    },
  });
  return result.answers;
}

const dist = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
const step = (f, t) => f[0] < t[0] ? 'SOUTH' : f[0] > t[0] ? 'NORTH' : f[1] < t[1] ? 'EAST' : f[1] > t[1] ? 'WEST' : null;
const ITEM_OF = (alt, title) => {
  const s = ((title || '') + ' ' + (alt || '')).toUpperCase();
  for (const k of ['WHEAT', 'MELON', 'CARROT', 'TOMATO', 'STRAWBERRY', 'EGG', 'MILK', 'WOOL']) if (s.includes(k)) return k;
  return null;
};

let prevHash = '';
for (let i = 0; i < MAX; i++) {
 try {
  const r = await cli(SMART(JSON.stringify(prevHash)));
  if (r.wait_timeout) { console.log('wait-timeout ' + r.dt); continue; }
  if (r.cached) {
    fs.appendFileSync(LOG, JSON.stringify({ t: new Date().toISOString(), day_turn: r.dt, cached: 1, act: 'repeat-PASS', advanced: r.advanced }) + '\n');
    console.log(`[${r.dt}] repeat-PASS -> ${r.advanced}`);
    continue;
  }
  const st = r.state;
  const cats = { mature: [], dry: [], weed: [], bare: [] };
  const pos = [[4, 4]]; // idx0 farmer; hands appended by farmhand_N token
  let melon = 0, wheat = 0;
  const unknown = new Set();
  for (const c of st.cells) {
    const im = c.imgs, tt = c.t || '';
    if (/locked_cell/.test(im)) continue;
    const fh = im.match(/farmhand_(\d+)/);
    if (/farmer_p1/.test(im)) pos[0] = [c.r, c.c];
    if (fh) pos[+fh[1]] = [c.r, c.c];
    const ct = (tt.match(/(WHEAT|MELON|CARROT|TOMATO|STRAWBERRY)\s*\(([^)]+)\)/i) || []);
    if (ct[1]) {
      const cu = ct[1].toUpperCase(), stage = (ct[2] || '').toLowerCase();
      if (cu === 'MELON') melon++; if (cu === 'WHEAT') wheat++;
      if (/ready|mature|harvest/.test(stage)) cats.mature.push([c.r, c.c]);
      else if (/^soil_dry/i.test(im)) cats.dry.push([c.r, c.c]);
      continue;
    }
    const t = im.replace(/farmhand_\d+|farmer_p1|farmer p1|shed|coins/g, '').replace(/\++/g, '+').replace(/^\+|\+$/g, '');
    if (/weed/.test(t)) { cats.weed.push([c.r, c.c]); continue; }
    if (/shed/i.test(im)) continue;
    const crop = (t.match(/(WHEAT|MELON|CARROT|TOMATO|STRAWBERRY)/i) || [])[1];
    if (crop) {
      const cu = crop.toUpperCase();
      if (cu === 'MELON') melon++; if (cu === 'WHEAT') wheat++;
      if (/ready|mature|harvest/i.test(t)) cats.mature.push([c.r, c.c]);
      else if (/^soil_dry/i.test(t)) cats.dry.push([c.r, c.c]);
      else if (!/watered|growth|sprout|seed/i.test(t)) unknown.add(t);
      continue;
    }
    if (/^soil_(dry|watered)$/.test(t) || t === '') cats.bare.push([c.r, c.c]);
    else if (t && !/farmer|shed|coins/.test(t)) unknown.add(t);
  }
  const nU = st.units.length;
  while (pos.length < nU) pos.push(pos[0].slice());
  const near = (p, L) => L.slice().sort((a, b) => dist(p, a) - dist(p, b))[0];
  const go = (p, t, op, arg) => { const mv = step(p, t); return mv ? { op: mv, arg: null } : { op, arg }; };
  // task pools (claimed across units)
  const pool = {
    harvest: cats.mature.slice(),
    water: cats.dry.slice(),
    weed: cats.weed.slice(),
    bare: cats.bare.slice(),
  };
  const take = (p, L) => { if (!L.length) return null; let bi = 0, bd = 1e9; L.forEach((t, i) => { const d = dist(p, t); if (d < bd) { bd = d; bi = i; } }); return L.splice(bi, 1)[0]; };
  // market ladder + refills + SELL from shed cache
  const orders = [];
  const hands = nU - 1;
  if (st.day === 1 && hands < 2 && st.money1 > 100) orders.push({ op: 'HIRE', qty: 2 - hands });
  const wantW = st.day <= 21 && wheat < 10 ? 10 - wheat - seedsEst('WHEAT') : 0;
  const wantM = st.day <= 13 && melon < 6 ? 6 - melon - seedsEst('MELON') : 0;
  if (wantW >= 5 && st.money1 > 300) orders.push({ op: 'BUY_SEED', item: 'WHEAT', qty: Math.min(10, wantW) });
  else if (st.day === 1 && wantW > 0 && st.money1 > 300) orders.push({ op: 'BUY_SEED', item: 'WHEAT', qty: wantW });
  if (wantM >= 2 && st.money1 > 500) orders.push({ op: 'BUY_SEED', item: 'MELON', qty: Math.min(6, wantM) });
  else if (st.day === 1 && wantM > 0 && st.money1 > 500) orders.push({ op: 'BUY_SEED', item: 'MELON', qty: wantM });
  if (st.turn === 1) { // refresh shed cache daily, sell produce
    try {
      const inv = await cli(SHED);
      shedCache = {};
      for (const [k2, n] of Object.entries(inv)) {
        if (/seed/i.test(k2)) continue;
        const item = ITEM_OF('', k2);
        if (item && n > 0) { shedCache[item] = n; orders.push({ op: 'SELL', item, qty: n }); }
      }
    } catch {}
  } else {
    for (const [item, n] of Object.entries(shedCache)) if (n > 0) orders.push({ op: 'SELL', item, qty: n });
  }
  // per-unit assignment: farmer full range, hands harvest/water only
  const units = [];
  for (let u = 0; u < nU; u++) {
    const p = pos[u] || pos[0];
    let a = { op: 'PASS', arg: null }, why = 'idle';
    const ht = take(p, pool.harvest); if (ht) { a = go(p, ht, 'HARVEST', null); why = 'harvest'; }
    else { const wt = take(p, pool.water); if (wt) { a = go(p, wt, 'WATER', null); why = 'water'; }
      else if (u === 0) {
        if (pool.bare.length && st.day <= 25) {
          const crop = (melon < 6 && st.day <= 13 && seedsEst('MELON') > 0) ? 'MELON'
            : (seedsEst('WHEAT') > 0 && wheat < 10 ? 'WHEAT' : (seedsEst('MELON') > 0 ? 'MELON' : null));
          if (crop) { const t2 = take(p, pool.bare); if (t2) { a = go(p, t2, 'PLANT', crop); why = 'plant-' + crop; } }
        }
        if (a.op === 'PASS') { const dt2 = take(p, pool.weed); if (dt2) { a = go(p, dt2, 'DIG', null); why = 'weed'; } }
      } }
    units.push({ ...a, why });
  }
  const text = [`Day ${st.day}/${st.days} Turn ${st.turn} Money ${st.money1} (starter ${st.money2})`,
    `units=${nU} mktRows=${st.mktRows} shed=${JSON.stringify(shedCache)}`,
    `mature=${pool.harvest.length} dry=${pool.water.length} bare=${pool.bare.length} weed=${pool.weed.length} melon=${melon} wheat=${wheat} seeds W/M=${seedsEst('WHEAT')}/${seedsEst('MELON')}`,
    `Farmer plan: ${units[0].op}${units[0].arg ? ' ' + units[0].arg : ''} (${units[0].why}) Orders: ${orders.map(o => o.op + (o.item ? ' ' + o.item : '') + 'x' + (o.qty || 1)).join(',') || 'none'}`].join('\n');
  let v = null;
  for (let a2 = 0; a2 < 2; a2++) { try { v = await vote(text); break; } catch { await new Promise(rr => setTimeout(rr, 1500)); } }
  if (v) {
    const jt = v.tactic?.choice;
    const cat = units[0].op === 'HARVEST' ? 'harvest' : units[0].op === 'WATER' ? 'water' : units[0].op === 'PLANT' ? 'plant' : units[0].op === 'DIG' ? 'dig' : null;
    if (jt && jt !== 'pass' && jt !== 'move' && jt !== 'market' && cat !== jt && (v.tactic.probabilities?.[jt] || 0) > 0.6) {
      const L = jt === 'harvest' ? cats.mature : jt === 'water' ? cats.dry : jt === 'plant' ? cats.bare : cats.weed;
      if (L.length) { const t2 = near(pos[0], L); const op2 = jt.toUpperCase();
        const arg2 = op2 === 'PLANT' ? (seedsEst('MELON') > 0 && melon < 6 ? 'MELON' : 'WHEAT') : null;
        if (op2 !== 'PLANT' || arg2) { const g = go(pos[0], t2, op2, arg2); units[0] = { ...g, why: 'jev-' + jt }; } }
    }
  }
  if (units[0].op === 'PLANT' && units[0].arg) { ledger[units[0].arg].u++; saveLedger(); }
  for (const o of orders) if (o.op === 'BUY_SEED') { ledger[o.item].b += o.qty; saveLedger(); }
  const a = await cli(ACT(units.map(u => ({ op: u.op, arg: u.arg })), orders));
  const k = {};
  prevHash = ''; // active play: fresh read every turn
  if (unknown.size) console.log(`[${r.dt}] unknown: ${[...unknown].join(' ~ ').slice(0, 160)}`);
  fs.appendFileSync(LOG, JSON.stringify({ t: new Date().toISOString(), day_turn: r.dt, cached: 0, money1: st.money1, money2: st.money2, acts: units.map(u => u.op + (u.arg ? '+' + u.arg : '')), why: units.map(u => u.why), orders, set: a.set, advanced: a.advanced, jev: v }) + '\n');
  console.log(`[${r.dt}] $${st.money1} ${units.map(u => u.op + (u.arg ? '+' + u.arg : '')).join('/')} orders=${orders.length} -> ${a.advanced}`);
 } catch (e) {
  fs.appendFileSync(LOG, JSON.stringify({ t: new Date().toISOString(), error: String(e?.message || e).slice(0, 200) }) + '\n');
  console.log('turn-error (retrying): ' + String(e?.message || e).slice(0, 120));
  await new Promise(rr => setTimeout(rr, 5000));
 }
}
console.log('DRIVER_DONE');
