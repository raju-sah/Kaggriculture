"""V88 provenance audit: discard unpaired findings, rebuild a valid comparison basis.

Read-only. Rebuilds agent-to-seat provenance from game records and recorded
agent SHA-256 values, never from filename prefixes.

Why this file exists
--------------------
The first V88 pass compared files named `v50-seed-XXXX-*.json` against files
named `v56-seed-XXXX-*.json` and treated them as "V50 the actor" versus "V56 the
actor". That was wrong. In this project a replay file is named after the
OPONENT in most runs: `v50-seed-92802-ab-repeat-0.json` under
`v57_broad/.../reset/replays/` is the V57-reset candidate playing against v50.
The five distinct `v50-seed-92802-ab` files found under the tree have rewards
[77947, 113785], [78631, 112218], [53067, 105795], [65182, 88632],
[51204, 133203] and carry agent lists of candidate_agent.py,
v57_reset_candidate.py, candidate.py, hybrid.py and candidate.py respectively.

Therefore every days 24-29 delta computed in the first pass is discarded. It
compared a V50 opponent seat against a V56 opponent seat on DIFFERENT games with
DIFFERENT opponents, so it could not attribute anything to either agent.

This script establishes what is actually available:
  1. the SHA-256 of every frozen agent of interest;
  2. every saved game record that places a given agent SHA at a given seat;
  3. for each (seed, opponent-agent) pair, whether the game is retained as a
     replay, and whether BOTH agents of interest appear in the same game.

Only rows where both V50 and V56 appear in the same game, or where one of them
plays a fixed identical opponent on the same seed in both seat orders, can
support an actor-level comparison. Everything else is reported as unusable for
this purpose rather than silently compared.

Output: experiments/v88_terminal_phase/provenance_audit.json
"""

import glob
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture")
OUT = ROOT / "experiments/v88_terminal_phase/provenance_audit.json"

AGENTS = {
    "v50": ROOT / "experiments/v50_agent.py",
    "v56": ROOT / "agents/v56_agent.py",
    "v48": ROOT / "experiments/v48_agent.py",
    "v51": ROOT / "experiments/v51_agent.py",
    "v52": ROOT / "experiments/v52_agent.py",
    "v53": ROOT / "agents/v53_agent.py",
    "v54": ROOT / "agents/v54_agent.py",
    "v55": ROOT / "agents/v55_agent.py",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    shas = {name: sha(p) for name, p in AGENTS.items()}
    by_sha = {v: k for k, v in shas.items()}

    direct = []            # games containing BOTH v50 and v56
    actor_games = defaultdict(list)   # agent name -> [(seed, game_id, seat, coins, replay)]
    seen = set()

    for path in glob.glob(str(ROOT / "experiments/**/games.jsonl"), recursive=True):
        for line in open(path):
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ags = rec.get("agents")
            if not isinstance(ags, list) or len(ags) != 2:
                continue
            seats = [a.get("sha256") for a in ags if isinstance(a, dict)]
            if len(seats) != 2 or any(s is None for s in seats):
                continue
            gid = rec.get("game_id")
            if gid in seen:
                continue
            seen.add(gid)
            replay = os.path.join(os.path.dirname(path), "replays", f"{gid}.json")
            has_replay = os.path.exists(replay)
            names = [by_sha.get(s) for s in seats]
            coins = rec.get("final_coins") or []
            seed = rec.get("seed")
            if "v50" in names and "v56" in names:
                direct.append(
                    {
                        "seed": seed, "game_id": gid, "seats": names,
                        "final_coins": coins, "replay": has_replay, "source": path,
                    }
                )
            for seat, name in enumerate(names):
                if name:
                    actor_games[name].append(
                        {
                            "seed": seed, "game_id": gid, "seat": seat,
                            "agent": seats[seat],
                            "opponent": names[1 - seat] or "unknown",
                            "opponent_path": (rec["agents"][1 - seat] or {}).get("path"),
                            "final_coins": coins, "replay": has_replay, "source": path,
                        }
                    )

    # Which (agent, seed, opponent) cells have a retained replay in BOTH seat orders?
    coverage = {}
    for name, games in actor_games.items():
        cell = defaultdict(dict)
        for g in games:
            key = (g["seed"], g["opponent"])
            cell[key][("ab" if g["seat"] == 0 else "ba")] = g
        coverage[name] = {
            f"{k[0]}|{k[1]}": {
                "ab_replay": ("ab" in v and v["ab"]["replay"]),
                "ba_replay": ("ba" in v and v["ba"]["replay"]),
                "ab_coins": v.get("ab", {}).get("final_coins"),
                "ba_coins": v.get("ba", {}).get("final_coins"),
                "ab_game": v.get("ab", {}).get("source"),
                "ba_game": v.get("ba", {}).get("source"),
            }
            for k, v in sorted(cell.items(), key=lambda x: (str(x[0][0]), str(x[0][1])))
        }

    report = {
        "agent_sha256": shas,
        "discarded": {
            "what": "all days 24-29 deltas in experiments/v88_terminal_phase/paired_terminal_diff.json and production_vs_liquidation.json",
            "why": "those scripts matched replay files by filename prefix. A replay is named for the opponent in this project, so the comparison paired a V50 opponent seat against a V56 opponent seat from different games with different opponents. No causal attribution is supportable from that data.",
        },
        "direct_v50_vs_v56_games": len(direct),
        "direct_v50_vs_v56_with_replay": sum(1 for d in direct if d["replay"]),
        "direct_sample": direct[:8],
        "actor_coverage": coverage,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")

    print("agent sha256:")
    for k, v in shas.items():
        print(f"  {k}: {v}")
    print(f"\ndirect V50-vs-V56 games found: {len(direct)}  (with saved replay: {report['direct_v50_vs_v56_with_replay']})")
    for d in direct[:8]:
        print(f"  seed {d['seed']} {d['game_id']:34s} seats={d['seats']} coins={d['final_coins']} replay={d['replay']}")

    print("\nper-agent coverage of (seed|opponent) cells with BOTH seat replays retained:")
    for name in ("v50", "v56"):
        both = [k for k, v in coverage.get(name, {}).items() if v["ab_replay"] and v["ba_replay"]]
        print(f"  {name}: {len(both)} cells")
        for k in both[:10]:
            print(f"      {k}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
