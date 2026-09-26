"""Build a compact, derived V66 Kaggle episode summary from gitignored replays."""
import collections, glob, hashlib, importlib.util, json, os

REPLAY_DIR = "experiments/kaggle/v66_postmortem"
OUT = "experiments/v66_postmortem/episode_summary.json"
SOURCE = "experiments/submission_candidate_20260926/original_planner.py"

_spec = importlib.util.spec_from_file_location("v66_submitted_source", SOURCE)
_agent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_agent)


def farm_metrics(farm):
    tiles = collections.Counter()
    animals = collections.Counter()
    plants = collections.Counter()
    for row in farm.get("tiles", []):
        for tile in row:
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind", "UNKNOWN")
            tiles[kind] += 1
            if tile.get("animal"):
                animals[tile["animal"]] += 1
            if kind == "PLANT":
                plants[tile.get("crop", "UNKNOWN")] += 1
    return {"tile_kinds": dict(tiles), "animals": dict(animals), "plants": dict(plants),
            "hands": len(farm.get("hands", [])), "unlocked": farm.get("unlocked_quadrants", [])}


def main():
    matches = []
    for path in sorted(glob.glob(os.path.join(REPLAY_DIR, "episode-*-replay.json"))):
        data = json.load(open(path))
        agents = data["info"]["Agents"]
        cand = next((i for i, a in enumerate(agents) if a.get("Name") == "Rajusah"), 0)
        opp = 1 - cand
        _agent._UNIT_GOALS = {}
        source_matches = 0
        for t in range(len(data["steps"]) - 1):
            predicted = _agent.agent(data["steps"][t][cand]["observation"])
            if predicted == data["steps"][t + 1][cand]["action"]:
                source_matches += 1
        final_obs = data["steps"][-1][cand]["observation"]
        action_counts = []
        market_quantities = []
        first_land = []
        max_hands = [0, 0]
        for p in (cand, opp):
            counts = collections.Counter()
            quantities = collections.defaultdict(lambda: {"orders": 0, "units": 0})
            for t, step in enumerate(data["steps"]):
                act = step[p].get("action", {})
                counts["farmer:" + str((act.get("farmer") or ["?"])[0])] += 1
                counts.update("worker:" + str((x or ["?"])[0]) for x in act.get("hands", []))
                for order in act.get("market", []):
                    op = order[0]
                    counts["market:" + op] += 1
                    if op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL") and len(order) > 2 and isinstance(order[-1], int):
                        item = order[1] if op != "HIRE" else ""
                        quantities[op + ":" + item]["orders"] += 1
                        quantities[op + ":" + item]["units"] += order[-1]
                    if op == "BUY_LAND" and p == opp:
                        first_land.append({"step": t, "day": step[p]["observation"].get("day"), "order": order})
                farm = step[p]["observation"]["farms"][p]
                max_hands[p == opp] = max(max_hands[p == opp], len(farm.get("hands", [])))
            action_counts.append(dict(sorted(counts.items())))
            market_quantities.append(dict(sorted(quantities.items())))
        players = []
        for p in (cand, opp):
            farm = final_obs["farms"][p]
            players.append({"name": agents[p].get("Name"), "seat": p,
                            "reward": data.get("rewards", [None, None])[p],
                            "money": farm.get("money"), **farm_metrics(farm),
                            "max_hands_seen": max_hands[p == opp],
                            "action_counts": action_counts[0 if p == cand else 1],
                            "market_quantities": market_quantities[0 if p == cand else 1]})
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        matches.append({"episode_id": data["info"].get("EpisodeId"), "seed": data["info"].get("seed"),
                        "state": data.get("statuses", [None])[-1] if data.get("statuses") else None,
                        "module_version": data.get("module_version"), "steps": len(data.get("steps", [])),
                        "source_action_replay": {"matched": source_matches, "checked": len(data.get("steps", [])) - 1},
                        "replay_file": os.path.basename(path), "replay_sha256": h,
                        "candidate_seat": cand, "players": players,
                        "opponent_land_buys": first_land})
    out = {"submission_id": 56583862,
           "submission_public_score_latest": 492.1,
           "submission_public_score_initial_observation": 506.5,
           "source_sha256": "d82c430c9562b6b213b92899d4df59aa9b9b58bcc8bdf3522b9e819da03e083d",
           "module_versions": sorted({m["module_version"] for m in matches}),
           "completed_matches_returned_by_kaggle": len(matches),
           "public_matches": sum(m["episode_id"] != 113765357 for m in matches),
           "matches": matches}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(OUT)
    for m in matches:
        c, o = m["players"]
        print(m["episode_id"], m["seed"], m["candidate_seat"], c["reward"], o["reward"],
              c["unlocked"], o["unlocked"], c["animals"], o["animals"],
              "crops", c["action_counts"].get("farmer:PLANT", 0) + sum(v for k,v in c["action_counts"].items() if k == "worker:PLANT"),
              o["action_counts"].get("farmer:PLANT", 0) + sum(v for k,v in o["action_counts"].items() if k == "worker:PLANT"),
              "landbuys", len(m["opponent_land_buys"]))
        print(" hashes", m["replay_sha256"])

if __name__ == "__main__":
    main()
