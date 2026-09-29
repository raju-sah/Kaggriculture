"""Deep Replay Analysis: Extract winning patterns from elite victories.
Analyzes game state, animal compositions, market timing, and action sequences
from our top victories against elite opponents (2000+ score)."""

import json
import os
import sys

REPLAY_DIR = "/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture/experiments/elite_replays"

def load_replay(episode_id):
    path = os.path.join(REPLAY_DIR, f"episode-{episode_id}-replay.json")
    if not os.path.exists(path):
        print(f"  [SKIP] {path} not found")
        return None
    with open(path) as f:
        return json.load(f)

def analyze_replay(replay, label, our_agent_name):
    """Deep analysis of a single replay."""
    steps = replay.get("steps", [])
    if not steps:
        print(f"  [SKIP] No steps in {label}")
        return None
    
    # Determine which player we are (agent 0 or 1)
    info = replay.get("info", {})
    
    # Check final scores
    final_step = steps[-1] if steps else None
    
    results = {
        "label": label,
        "agent": our_agent_name,
        "total_steps": len(steps),
    }
    
    # Track key metrics through the game
    p0_scores = []
    p1_scores = []
    p0_animals = []
    p1_animals = []
    p0_actions_summary = {"BUY_ANIMAL": {}, "SELL_PRODUCT": 0, "BUY_PRODUCT": {}}
    p1_actions_summary = {"BUY_ANIMAL": {}, "SELL_PRODUCT": 0, "BUY_PRODUCT": {}}
    p0_shop_unlocks = []
    p1_shop_unlocks = []
    town_shops_timeline = []
    
    for i, step_data in enumerate(steps):
        obs_list = step_data  # Each step is a list of observations
        if not isinstance(obs_list, list) or len(obs_list) < 2:
            continue
        
        for player_idx in range(min(2, len(obs_list))):
            player_data = obs_list[player_idx]
            if not isinstance(player_data, dict):
                continue
            
            obs = player_data.get("observation", {})
            if not isinstance(obs, dict):
                continue
            
            # Get score/money
            reward = player_data.get("reward", 0)
            status = player_data.get("status", "")
            
            # Get action taken
            action = player_data.get("action", {})
            if isinstance(action, dict):
                market = action.get("market", [])
                if isinstance(market, list):
                    for order in market:
                        if isinstance(order, list) and len(order) >= 2:
                            summary = p0_actions_summary if player_idx == 0 else p1_actions_summary
                            if order[0] == "BUY_ANIMAL" and len(order) >= 3:
                                animal = order[1]
                                qty = int(order[2]) if len(order) > 2 else 1
                                summary["BUY_ANIMAL"][animal] = summary["BUY_ANIMAL"].get(animal, 0) + qty
                            elif order[0] == "SELL_PRODUCT":
                                summary["SELL_PRODUCT"] += 1
                            elif order[0] == "BUY_PRODUCT" and len(order) >= 3:
                                product = order[1]
                                qty = int(order[2]) if len(order) > 2 else 1
                                summary["BUY_PRODUCT"][product] = summary["BUY_PRODUCT"].get(product, 0) + qty
            
            # Track town shops
            town = obs.get("town", {})
            if isinstance(town, dict) and player_idx == 0:
                shops = town.get("unlocked_shops", [])
                day = obs.get("day", 0)
                hour = obs.get("hour", 0)
                if shops and (not town_shops_timeline or shops != town_shops_timeline[-1][1]):
                    town_shops_timeline.append((f"D{day}H{hour}", list(shops)))
            
            # Track shed animals
            private = obs.get("private", {})
            if isinstance(private, dict):
                shed = private.get("shed", {})
                if isinstance(shed, dict):
                    animals = {k: int(v) for k, v in shed.items() if k in ("COW", "SHEEP", "GOOSE") and int(v or 0) > 0}
                    if player_idx == 0:
                        if animals and (not p0_animals or animals != p0_animals[-1][1]):
                            p0_animals.append((i, animals))
                    else:
                        if animals and (not p1_animals or animals != p1_animals[-1][1]):
                            p1_animals.append((i, animals))
            
            # Track score at key intervals
            if isinstance(reward, (int, float)):
                if player_idx == 0:
                    p0_scores.append((i, reward))
                else:
                    p1_scores.append((i, reward))
    
    results["p0_final_score"] = p0_scores[-1][1] if p0_scores else 0
    results["p1_final_score"] = p1_scores[-1][1] if p1_scores else 0
    results["p0_animals_bought"] = p0_actions_summary["BUY_ANIMAL"]
    results["p1_animals_bought"] = p1_actions_summary["BUY_ANIMAL"]
    results["p0_products_bought"] = p0_actions_summary["BUY_PRODUCT"]
    results["p1_products_bought"] = p1_actions_summary["BUY_PRODUCT"]
    results["p0_sell_count"] = p0_actions_summary["SELL_PRODUCT"]
    results["p1_sell_count"] = p1_actions_summary["SELL_PRODUCT"]
    results["p0_animal_timeline"] = p0_animals[:8]  # First 8 animal changes
    results["p1_animal_timeline"] = p1_animals[:8]
    results["town_shops"] = town_shops_timeline
    
    return results

def format_results(results):
    """Pretty print analysis results."""
    print(f"\n{'='*80}")
    print(f"REPLAY: {results['label']}")
    print(f"{'='*80}")
    print(f"Our Agent: {results['agent']}")
    print(f"Total Steps: {results['total_steps']}")
    print(f"\nFinal Scores: P0={results['p0_final_score']:,.0f} | P1={results['p1_final_score']:,.0f}")
    margin = results['p0_final_score'] - results['p1_final_score']
    print(f"Margin: {'+' if margin > 0 else ''}{margin:,.0f}")
    
    print(f"\n--- ANIMAL PURCHASES ---")
    print(f"  P0 animals: {results['p0_animals_bought']}")
    print(f"  P1 animals: {results['p1_animals_bought']}")
    
    print(f"\n--- PRODUCT PURCHASES ---")
    print(f"  P0 products: {results['p0_products_bought']}")
    print(f"  P1 products: {results['p1_products_bought']}")
    
    print(f"\n--- SELL ACTIONS ---")
    print(f"  P0 sells: {results['p0_sell_count']}")
    print(f"  P1 sells: {results['p1_sell_count']}")
    
    print(f"\n--- ANIMAL TIMELINE (first 8 changes) ---")
    for step, animals in results['p0_animal_timeline'][:5]:
        print(f"  P0 Step {step}: {animals}")
    for step, animals in results['p1_animal_timeline'][:5]:
        print(f"  P1 Step {step}: {animals}")
    
    print(f"\n--- TOWN SHOPS UNLOCKED ---")
    for time, shops in results['town_shops']:
        print(f"  {time}: {shops}")


# Main analysis
episodes = [
    ("113339120", "V56 vs Tergel Munkhbat (#123, Elo 2557.6)", "V56"),
    ("112804984", "V52 vs Azathoth (#137, Elo 2537.9)", "V52"),
    ("113217120", "V56 vs Oleg Smirnov (#375, Elo 2329.3)", "V56"),
    ("112967158", "V54 vs flaty (#517, Elo 2254.4)", "V54"),
    ("114787845", "V110 vs Tashfik Salehin (#1568, Elo 1847.6)", "V110"),
]

print("=" * 80)
print("DEEP REPLAY ANALYSIS: Elite Victory Pattern Extraction")
print("=" * 80)

all_results = []
for ep_id, label, agent_name in episodes:
    print(f"\nLoading {label}...")
    replay = load_replay(ep_id)
    if replay is None:
        continue
    results = analyze_replay(replay, label, agent_name)
    if results:
        all_results.append(results)
        format_results(results)

# Cross-analysis: Find common patterns in our victories
print("\n" + "=" * 80)
print("CROSS-ANALYSIS: Common Winning Patterns")
print("=" * 80)

if all_results:
    # Animal composition patterns
    print("\n--- Our Animal Purchases Across Wins ---")
    for r in all_results:
        print(f"  {r['label'][:50]}: {r['p0_animals_bought']}")
    
    # Opponent animal patterns 
    print("\n--- Opponent Animal Purchases Across Our Wins ---")
    for r in all_results:
        print(f"  {r['label'][:50]}: {r['p1_animals_bought']}")
    
    # Product purchase patterns
    print("\n--- Our Product Purchases ---")
    for r in all_results:
        print(f"  {r['label'][:50]}: {r['p0_products_bought']}")
    
    # Sell frequency
    print("\n--- Sell Action Frequency ---")
    for r in all_results:
        avg_sells_per_step = r['p0_sell_count'] / max(1, r['total_steps'])
        print(f"  {r['label'][:50]}: P0={r['p0_sell_count']} P1={r['p1_sell_count']} (ratio: {avg_sells_per_step:.3f}/step)")
    
    # Margin analysis
    print("\n--- Victory Margins ---")
    for r in all_results:
        margin = r['p0_final_score'] - r['p1_final_score']
        print(f"  {r['label'][:50]}: {'+' if margin > 0 else ''}{margin:,.0f}")
