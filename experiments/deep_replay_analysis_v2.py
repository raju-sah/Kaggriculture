"""Deep Replay Analysis v2: Correctly identify our player seat and extract patterns."""

import json
import os
import sys

REPLAY_DIR = "/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture/experiments/elite_replays"

def load_replay(episode_id):
    path = os.path.join(REPLAY_DIR, f"episode-{episode_id}-replay.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def analyze_replay_v2(replay, label, our_agent_name):
    """Deep analysis with correct player identification."""
    steps = replay.get("steps", [])
    info = replay.get("info", {})
    
    # Get player names/IDs from replay info
    agents_info = info.get("TeamNames", [])
    print(f"\n{'='*80}")
    print(f"REPLAY: {label}")
    print(f"{'='*80}")
    print(f"Team Names: {agents_info}")
    
    # Check configuration for team info
    config = replay.get("configuration", {})
    print(f"Configuration keys: {list(config.keys()) if isinstance(config, dict) else 'N/A'}")
    
    # Look at the replay structure
    print(f"Top-level keys: {list(replay.keys())}")
    print(f"Info keys: {list(info.keys()) if isinstance(info, dict) else 'N/A'}")
    
    # Check rewards
    if steps and len(steps) > 0:
        first_step = steps[0]
        last_step = steps[-1]
        print(f"\nFirst step structure: {type(first_step)}")
        if isinstance(first_step, list) and len(first_step) >= 2:
            for i in range(min(2, len(first_step))):
                p = first_step[i]
                if isinstance(p, dict):
                    print(f"  Player {i} first step keys: {list(p.keys())}")
                    print(f"  Player {i} first reward: {p.get('reward')}")
                    print(f"  Player {i} first status: {p.get('status')}")
                    obs = p.get('observation', {})
                    if isinstance(obs, dict):
                        print(f"  Player {i} obs.player: {obs.get('player')}")
                        print(f"  Player {i} obs.step: {obs.get('step')}")
        
        if isinstance(last_step, list) and len(last_step) >= 2:
            print(f"\nFinal scores:")
            for i in range(min(2, len(last_step))):
                p = last_step[i]
                if isinstance(p, dict):
                    print(f"  Player {i} final reward: {p.get('reward')}")
                    obs = p.get('observation', {})
                    if isinstance(obs, dict):
                        private = obs.get('private', {})
                        if isinstance(private, dict):
                            print(f"  Player {i} final money: {private.get('money')}")
                            print(f"  Player {i} shed: {private.get('shed')}")

    # Detailed turn-by-turn analysis of key moments
    print(f"\n--- KEY MOMENTS ---")
    for step_idx in [0, 24, 48, 72, 96, 144, 168, 192, 216, 360, 504, 624, 696, 718, 719]:
        if step_idx >= len(steps):
            continue
        step_data = steps[step_idx]
        if not isinstance(step_data, list) or len(step_data) < 2:
            continue
        for pi in range(2):
            p = step_data[pi]
            if not isinstance(p, dict):
                continue
            obs = p.get("observation", {})
            action = p.get("action", {})
            private = obs.get("private", {}) if isinstance(obs, dict) else {}
            shed = private.get("shed", {}) if isinstance(private, dict) else {}
            money = private.get("money", 0) if isinstance(private, dict) else 0
            day = obs.get("day", 0) if isinstance(obs, dict) else 0
            hour = obs.get("hour", 0) if isinstance(obs, dict) else 0
            
            # Count shed animals
            animals = {k: int(v) for k, v in shed.items() if k in ("COW", "SHEEP", "GOOSE") and int(v or 0) > 0}
            # Count shed products
            products = {k: int(v) for k, v in shed.items() if k not in ("COW", "SHEEP", "GOOSE") and int(v or 0) > 0}
            
            if pi == 0 and (step_idx == 0 or step_idx % 72 == 0 or step_idx >= 696):
                market = action.get("market", []) if isinstance(action, dict) else []
                print(f"  Step {step_idx} (D{day}H{hour}) P{pi}: money={money:,} animals={animals} products={products}")
                if market and step_idx >= 696:
                    print(f"    Market actions: {market[:5]}")

    # Analyze opponent patterns (P1 typically)
    print(f"\n--- OPPONENT ANALYSIS (common patterns) ---")
    opp_animal_buys = {}
    opp_product_buys = {}
    for step_data in steps:
        if not isinstance(step_data, list) or len(step_data) < 2:
            continue
        # Player 1 (typically the opponent)
        p1 = step_data[1] if len(step_data) > 1 else {}
        if not isinstance(p1, dict):
            continue
        action = p1.get("action", {})
        if not isinstance(action, dict):
            continue
        market = action.get("market", [])
        if isinstance(market, list):
            for order in market:
                if isinstance(order, list) and len(order) >= 3:
                    if order[0] == "BUY_ANIMAL":
                        animal = order[1]
                        qty = int(order[2])
                        opp_animal_buys[animal] = opp_animal_buys.get(animal, 0) + qty
                    elif order[0] == "BUY_PRODUCT":
                        product = order[1]
                        qty = int(order[2])
                        opp_product_buys[product] = opp_product_buys.get(product, 0) + qty
    
    print(f"  Opponent animal buys: {opp_animal_buys}")
    print(f"  Opponent product buys: {opp_product_buys}")
    
    # Analyze animal counts at key points 
    print(f"\n--- OPPONENT ANIMAL TIMELINE ---")
    prev_animals = {}
    for step_idx, step_data in enumerate(steps):
        if not isinstance(step_data, list) or len(step_data) < 2:
            continue
        p1 = step_data[1] if len(step_data) > 1 else {}
        if not isinstance(p1, dict):
            continue
        obs = p1.get("observation", {})
        if not isinstance(obs, dict):
            continue
        private = obs.get("private", {})
        if not isinstance(private, dict):
            continue
        shed = private.get("shed", {})
        animals = {k: int(v) for k, v in shed.items() if k in ("COW", "SHEEP", "GOOSE") and int(v or 0) > 0}
        if animals != prev_animals:
            prev_animals = animals.copy()
            print(f"  Step {step_idx} (D{obs.get('day',0)}H{obs.get('hour',0)}): {animals}")

# Main
episodes = [
    ("113339120", "V56 vs Tergel Munkhbat (#123, Elo 2557.6)", "V56"),
    ("112804984", "V52 vs Azathoth (#137, Elo 2537.9)", "V52"),
    ("113217120", "V56 vs Oleg Smirnov (#375, Elo 2329.3)", "V56"),
    ("114787845", "V110 vs Tashfik Salehin (#1568, Elo 1847.6)", "V110"),
]

# Also analyze V115 recent matches
v115_episodes = [
    ("114818287", "V115 Recent Match 1", "V115"),
    ("114816859", "V115 Recent Match 2", "V115"),
    ("114815361", "V115 Recent Match 3", "V115"),
    ("114813867", "V115 Recent Match 4", "V115"),
]

print("=" * 80)
print("DEEP REPLAY ANALYSIS v2: Player Identification + Pattern Extraction")
print("=" * 80)

# Analyze elite wins first
for ep_id, label, agent_name in episodes:
    replay = load_replay(ep_id)
    if replay is None:
        print(f"  [SKIP] {ep_id} not found")
        continue
    analyze_replay_v2(replay, label, agent_name)

# Then analyze V115 recent matches
print("\n\n" + "=" * 80)
print("V115 RECENT MATCH ANALYSIS")
print("=" * 80)
for ep_id, label, agent_name in v115_episodes:
    replay = load_replay(ep_id)
    if replay is None:
        print(f"  [SKIP] {ep_id} not found")
        continue
    analyze_replay_v2(replay, label, agent_name)
