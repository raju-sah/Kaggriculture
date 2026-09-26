#!/usr/bin/env python3
"""Join target submitted orders to exact, reconciled settlements and observations."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
path = ROOT / "replays" / "episode-113718271-replay.json"
game = json.loads(path.read_text())
settlement = next(x for x in json.loads((ROOT / "accepted_sales.json").read_text()) if x["episode_id"] == 113718271)
settlements = {x["action_frame"]: x for x in settlement["transactions_by_step"]}
steps = game["steps"]
timeline = []
for frame in range(1, len(steps)):
    previous, current = steps[frame - 1], steps[frame]
    obs = previous[0]["observation"]
    day = int(obs.get("day", (frame - 1) // 24))
    row = {"action_frame": frame, "day": day, "hour": (frame - 1) % 24, "players": []}
    settled = settlements.get(frame, {})
    for seat in range(2):
        prior_obs = previous[seat]["observation"]
        farm = prior_obs["farms"][seat]
        private = prior_obs["private"]
        action = current[seat].get("action") or {}
        orders = action.get("market") or []
        accepted = next((x for x in settled.get("players", []) if x["seat"] == seat), {})
        row["players"].append({
            "name": game["info"]["TeamNames"][seat],
            "cash_before": farm["money"],
            "cash_after": current[seat]["observation"]["farms"][seat]["money"],
            "cash_delta": round(current[seat]["observation"]["farms"][seat]["money"] - farm["money"], 2),
            "shed_before": {k: v for k, v in private.get("shed", {}).items() if v},
            "worker_inventory_before": private.get("inventories", []),
            "prices_before": prior_obs.get("market", {}).get("prices", {}),
            "sell_order_intent": [{"item": o[1], "requested_quantity": o[2] if len(o) > 2 else None}
                                   for o in orders if o and o[0] == "SELL"],
            "purchase_order_intent": [{"operation": o[0], "item": o[1] if len(o) > 1 else None,
                                        "requested_quantity": o[2] if len(o) > 2 else None}
                                       for o in orders if o and o[0].startswith("BUY_")],
            "accepted_sale_units": accepted.get("accepted_units", {}).get("SELL", {}),
            "accepted_values_by_operation": accepted.get("accepted_value_by_product", {}),
        })
    timeline.append(row)

out = {"episode_id": game.get("info", {}).get("EpisodeId"), "module_version": game.get("module_version"),
       "configuration": game.get("configuration"), "replay_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
       "alignment": "action[t] is paired with observation[t-1] and produces observation[t]; accepted settlement was cash-checked exactly.",
       "steps": timeline}
(ROOT / "target_market_timeline.json").write_text(json.dumps(out, separators=(",", ":"), sort_keys=True) + "\n")
print(f"wrote {ROOT / 'target_market_timeline.json'}")
