"""Single-variable ablation: discard weed transactions after overnight reset."""
import ast, base64, json, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
source=(ROOT/'agents/v57_agent.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_LIZS_MODULES' for t in n.targets))
modules=eval(compile(ast.Expression(node.value),'<bundle>','eval'),dict(json=json,zlib=zlib,base64=base64))
keys=[k for k,v in modules.items() if 'def wrap_weed_repair(' in v]
assert len(keys)==1
key=keys[0]
old='        game["last_step"] = step\n'
new='        if step // 24 != game["last_step"] // 24:\n            game["active"].clear()\n'+old
assert modules[key].count(old)==1
modules[key]=modules[key].replace(old,new)
blob=base64.b85encode(zlib.compress(json.dumps(modules).encode(),9)).decode()
lines=source.splitlines(keepends=True)
lines[node.lineno-1:node.end_lineno]=[f'_LIZS_MODULES = json.loads(zlib.decompress(base64.b85decode({blob!r})))\n']
(ROOT/'experiments/v57_broad/v57_reset_candidate.py').write_text(''.join(lines))
print('Created experimental variant; frozen release untouched')
