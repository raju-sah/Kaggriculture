#!/bin/bash
# Jev live loop v3 (fastest shell): light poll -> full read -> cache -> Jev -> act+submit -> log.
set -u
RUN_DIR="$1"; MAX_TURNS="${2:-720}"
mkdir -p "$RUN_DIR"
LOG="$RUN_DIR/turns.jsonl"
S="playwright-cli -s=jev run-code"
POLL='async page => { const f = page.frames().find(x=>x.url().includes("playable")); return await f.evaluate(() => { const t=document.body.innerText; const dm=t.match(/Day\s*(\d+)\s*\/\s*(\d+)/); const tm=t.match(/Turn\s*(\d+)\s*\/\s*(\d+)/); return (dm?dm[1]:0)+"/"+(dm?dm[2]:0)+" "+(tm?tm[1]:0)+"/"+(tm?tm[2]:0)+" "+(/Your turn/.test(t)?"Y":"n"); }); }'

read_full() {
  $S "async page => { const f = page.frames().find(x=>x.url().includes('playable')); return await f.evaluate(() => { const q=(s)=>[...document.querySelectorAll(s)]; const txt=document.body.innerText; const dm=txt.match(/Day\s*(\d+)\s*\/\s*(\d+)/); const tm=txt.match(/Turn\s*(\d+)\s*\/\s*(\d+)/); const money=[...txt.matchAll(/Player\s*1[^\d]{0,20}(\d{2,6})/g)].map(x=>x[1]); const cells=q('.cell').map(c=>({r:+c.dataset.row,c:+c.dataset.col,s:+c.dataset.segment,imgs:[...c.querySelectorAll('img')].map(i=>i.alt).filter(Boolean).join('+')})); const units=q('select[id*=\"-op\"]').map(s=>({id:s.id,val:s.value})); return JSON.stringify({day:dm?+dm[1]:0,days:dm?+dm[2]:0,turn:tm?+tm[1]:0,yourTurn:/Your turn/.test(txt),money,ncells:cells.length,cells,units}); }); }" --raw | node proc.mjs "$RUN_DIR/state_last.json"
}

act_submit() { # $1 = OP
  local OP="$1"
  $S "async page => { const f = page.frames().find(x=>x.url().includes('playable')); return await f.evaluate(() => { const OP='$OP'; const setS=(s,v)=>{ const d=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(s),'value')||Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value'); d.set.call(s,v); s.dispatchEvent(new Event('change',{bubbles:true})); }; const sels=[...document.querySelectorAll('select[id*=\"-op\"]')]; sels.forEach((s,i)=>{ const v=(i===0)?OP:'PASS'; if([...s.options].some(o=>o.value===v)) setS(s,v); }); document.querySelector('button.submit-turn').click(); return JSON.stringify(sels.map(s=>s.value).join(',')); }); }" --raw
}

T=0; PREV_HASH=""; PREV_OP="PASS"; PREV_VERDICT="{}"
while [ "$T" -lt "$MAX_TURNS" ]; do
  # wait our turn with light polls
  for _ in $(seq 1 60); do
    P=$($S "$POLL" --raw 2>/dev/null | tr -d '"')
    case "$P" in *Y) break;; *) sleep 0.5;; esac
  done
  INFO=$(read_full)
  H=$(echo "$INFO" | node -e "import('fs').then(fs=>{let s='';process.stdin.on('data',d=>s+=d).on('end',()=>process.stdout.write(JSON.parse(s).hash))})")
  DT=$(echo "$INFO" | node -e "import('fs').then(fs=>{let s='';process.stdin.on('data',d=>s+=d).on('end',()=>process.stdout.write(JSON.parse(s).dt))})")
  if [ "$H" = "$PREV_HASH" ]; then
    VERDICT="$PREV_VERDICT"; OP="$PREV_OP"; CACHED="1"
  else
    VERDICT=$(node turn.mjs < "$RUN_DIR/state_last.json")
    OP=$(echo "$VERDICT" | node -e "import('fs').then(fs=>{let s='';process.stdin.on('data',d=>s+=d).on('end',()=>process.stdout.write(JSON.parse(s).action.op))})")
    CACHED="0"
  fi
  ACT="farmer:$OP"
  [ "$OP" = "MARKET" ] && { OP="PASS"; ACT="farmer:PASS(market-logged)"; }
  SET=$(act_submit "$OP" 2>/dev/null)
  # wait until turn actually advances (avoids double-submit on UI lag)
  for _ in $(seq 1 60); do
    P2=$($S "$POLL" --raw 2>/dev/null | tr -d '"')
    P2=$(echo "$P2" | awk '{split($1,a,"/"); split($2,b,"/"); print a[1]"/"b[1]}')
    [ "$P2" != "$DT" ] && break
    sleep 0.5
  done
  echo "{\"t\":\"$(date -u +%FT%TZ)\",\"day_turn\":\"$DT\",\"cached\":\"$CACHED\",\"act\":\"$ACT\",\"set\":$SET,\"jev\":$VERDICT}" >> "$LOG"
  echo "[$DT] act=$ACT cached=$CACHED"
  PREV_HASH="$H"; PREV_OP="$OP"; PREV_VERDICT="$VERDICT"
  T=$((T+1))
done
echo "LOOP_DONE turns=$T"
