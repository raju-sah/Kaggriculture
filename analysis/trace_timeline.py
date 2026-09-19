import json
import sys
from collections import Counter

def trace_timeline(filepath):
    with open(filepath) as f:
        data = json.load(f)
    info = data.get('info', {})
    teams = info.get('TeamNames', ['P0', 'P1'])
    rewards = data.get('rewards', [0, 0])
    steps = data['steps']
    print(f"=== Timeline for {teams[0]} vs {teams[1]} (Rewards: {rewards}) ===")
    
    for day in range(30):
        step_idx = day * 24
        if step_idx >= len(steps): break
        obs = steps[step_idx][0]['observation']
        farms = obs.get('farms', [])
        
        mkt_actions = [Counter(), Counter()]
        builds = [Counter(), Counter()]
        
        for h in range(24):
            idx = day * 24 + h
            if idx >= len(steps): break
            for seat in [0, 1]:
                act = steps[idx][seat].get('action', {}) or {}
                for role, order in [('farmer', act.get('farmer'))] + [('hand', o) for o in act.get('hands', [])]:
                    if not order: continue
                    cmd = order[0]
                    if cmd in ('BUILD_COOP', 'BUILD_PASTURE', 'HIRE_HAND', 'BUY_LAND'):
                        builds[seat][cmd] += 1
                for m in act.get('market', []):
                    if not m: continue
                    cmd = m[0]
                    item = m[1] if len(m) > 1 else ''
                    qty = m[2] if len(m) > 2 and isinstance(m[2], (int, float)) else 1
                    mkt_actions[seat][f"{cmd}_{item}"] += qty
        
        f0, f1 = farms[0], farms[1]
        if day in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 18, 19, 23, 24, 28, 29):
            print(f"Day {day:2d}:")
            print(f"  {teams[0]}: ${f0.get('money', 0):,.0f} | Hands: {len(f0.get('hands', []))} | Quads: {len(f0.get('unlocked_quadrants', []))} | Builds: {dict(builds[0])} | Mkt: {dict(mkt_actions[0])}")
            print(f"  {teams[1]}: ${f1.get('money', 0):,.0f} | Hands: {len(f1.get('hands', []))} | Quads: {len(f1.get('unlocked_quadrants', []))} | Builds: {dict(builds[1])} | Mkt: {dict(mkt_actions[1])}")

if __name__ == "__main__":
    trace_timeline(sys.argv[1])
