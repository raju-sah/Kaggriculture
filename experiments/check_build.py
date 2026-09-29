import json

def load_actions(path):
    with open(path) as f:
        content = f.read()
        import re
        m = re.search(r"ACTIONS\s*=\s*(\[.*?\])\n[a-zA-Z_]", content, re.DOTALL)
        if m:
            return json.loads(m.group(1))
        # fallback
        m = re.search(r"_KAZUHIRO_ACTIONS\s*=\s*(\[.*?\])\n", content, re.DOTALL)
        if m: return json.loads(m.group(1))
        return None

# But nam_agent.py might have _ACTIONS
for name in ["nam_agent.py", "kazuhiro_agent.py", "build_v55.py", "build_v55_nam_kazuhiro.py"]:
    print(f"Checking {name}")
