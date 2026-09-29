// Local Jev relay: browser loop POSTs state, gets back {op}. Key stays server-side.
// POST /vote {state} -> Jev evaluate -> {op, verdict}
// POST /log {line} -> append turns.jsonl (reduces lost data on crash)
import http from 'http';
import fs from 'fs';
import { experimental_evaluate as evaluate } from 'ai';

const RUN_DIR = process.argv[2] || 'runs/relay';
fs.mkdirSync(RUN_DIR, { recursive: true });
const LOG = `${RUN_DIR}/turns.jsonl`;

async function vote(state) {
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
  let op = 'PASS';
  if (a.feed_urgent?.probability > 0.6 || a.tactic?.choice === 'feed') op = 'FEED';
  else if (a.water_urgent?.probability > 0.6 || a.tactic?.choice === 'water') op = 'WATER';
  else if (a.tactic?.choice && a.tactic.choice !== 'pass') op = a.tactic.choice.toUpperCase();
  return { op, verdict: a, usage: result.usage };
}

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  let body = '';
  req.on('data', d => body += d);
  req.on('end', async () => {
    try {
      const j = JSON.parse(body || '{}');
      if (req.url === '/vote') {
        const { op, verdict, usage } = await vote(j.state);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ op, verdict, usage }));
      } else if (req.url === '/log') {
        fs.appendFileSync(LOG, j.line + '\n');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end('{"ok":true}');
      } else { res.writeHead(404); res.end(); }
    } catch (e) { res.writeHead(500); res.end(JSON.stringify({ error: String(e).slice(0, 300) })); }
  });
});
server.listen(8765, '127.0.0.1', () => console.log('relay :8765 dir=' + RUN_DIR));
