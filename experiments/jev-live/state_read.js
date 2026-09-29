// Read DOM-visible game state from the playable iframe.
// Run inside frame context via playwright `run-code`. Returns compact JSON.
// ponytail: DOM-only v1, engine-private fields (seeds/shed counts) when UI exposes them.
export const READ_FN = `() => {
  const q = (s) => [...document.querySelectorAll(s)];
  const txt = document.body.innerText;
  const m = (re) => (txt.match(re) || [])[1];
  // header
  const day = parseInt((txt.match(/Day\\s*(\\d+)\\s*\\/\\s*(\\d+)/) || [])[1] || '1');
  const days = parseInt((txt.match(/Day\\s*(\\d+)\\s*\\/\\s*(\\d+)/) || [])[2] || '1');
  const turn = parseInt((txt.match(/Turn\\s*(\\d+)\\s*\\/\\s*(\\d+)/) || [])[1] || '1');
  // money: "Player 1 (You) Shed 3000"
  const money = [...txt.matchAll(/Player\\s*1[^\\d]{0,20}(\\d{2,6})/g)].map(x=>x[1]);
  // grid cells
  const cells = q('.cell').map(c => ({
    r: +c.dataset.row, c: +c.dataset.col, s: +c.dataset.segment,
    imgs: [...c.querySelectorAll('img')].map(i=>i.alt).filter(Boolean).join('+')
  }));
  // unit action selects
  const units = q('select[id*="-op"], select[id*="-Hand"]').map(s => ({
    id: s.id, val: s.value,
    opts: [...s.options].map(o=>o.value)
  }));
  // prices (market dialog may be closed; read if present)
  const prices = {};
  q('.market-item[data-item]').forEach(el => {
    prices[el.dataset.item] = el.querySelector('.market-price')?.innerText?.trim();
  });
  // shed slots
  const shed = q('.inventory-slot').map(sl => (sl.innerText||'').trim()).filter(Boolean);
  // turn header
  const yourTurn = /Your turn/.test(txt);
  return JSON.stringify({ day, days, turn, money, yourTurn, ncells: cells.length,
    cells: cells.slice(0, 400), units, prices, shed });
}`;
