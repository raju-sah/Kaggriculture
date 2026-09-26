#!/usr/bin/env python3
"""Build an accepted-transaction control panel from saved frozen-v57 reset games only."""
from __future__ import annotations
import csv, glob, hashlib, json, os
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RESET_SHA = "4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e"
sys.path.insert(0, str(ROOT / "experiments/v62_elite_games"))
from accepted_sales import settle


def opponent_name(g, candidate_seat):
    name = g.get("opponent")
    if name:
        return str(name)
    agents = g.get("agents", [])
    other = agents[1 - candidate_seat].get("path", "unknown") if len(agents) == 2 else "unknown"
    base = Path(other).stem
    return base.replace("_agent", "").replace("_candidate", "")


def list_records():
    files = sorted(set(glob.glob(str(ROOT / "experiments/**/games/*.json"), recursive=True)
                       + glob.glob(str(ROOT / "experiments/**/games/**/*.json"), recursive=True)))
    by_seed_opp = defaultdict(lambda: defaultdict(dict))
    for fp in files:
        try:
            g = json.loads(Path(fp).read_text())
        except (OSError, json.JSONDecodeError):
            continue
        agents = g.get("agents", [])
        reset_seats = [i for i, a in enumerate(agents) if a.get("sha256") == RESET_SHA]
        rp = g.get("replay_path")
        if len(reset_seats) != 1 or not rp or not Path(rp).is_file():
            continue
        seat = reset_seats[0]
        seed = g.get("resolved_seed", g.get("seed"))
        opp = opponent_name(g, seat)
        # A seat/orientation is represented once; sorted traversal picks the first
        # saved artifact if a completed replay was copied into several run folders.
        by_seed_opp[seed][opp].setdefault(seat, {
            "game_record": str(Path(fp).relative_to(ROOT)),
            "replay_path": str(Path(rp).resolve()),
            "seed": seed,
            "opponent": opp,
            "reset_seat": seat,
            "game_id": g.get("game_id", Path(fp).stem),
            "candidate_result": g.get("candidate_result"),
            "final_coins": g.get("final_coins"),
            "agents": agents,
        })
    # Choose exactly one matchup per distinct seed, balancing opponent lineages
    # and preferring seat-swapped saved pairs. This avoids repeated seeds
    # dominating distributions while retaining two seats where available.
    selected = []
    opp_load = Counter()
    for seed in sorted(by_seed_opp, key=lambda x: (isinstance(x, str), x)):
        choices = []
        for opp, seats in by_seed_opp[seed].items():
            choices.append((opp_load[opp], -len(seats), opp, seats))
        _, _, opp, seats = min(choices, key=lambda x: (x[0], x[1], x[2]))
        opp_load[opp] += 1
        selected.extend(seats[s] for s in sorted(seats))
    return selected, by_seed_opp


def snapshot(replay, seat, day):
    frame = min(day * 24 if day == 0 else day * 24 + 1, len(replay["steps"]) - 1)
    obs = replay["steps"][frame][seat]["observation"]
    farm = obs["farms"][seat]
    plants = Counter()
    animals = Counter()
    animal_tiles = 0
    for row in farm.get("tiles", []):
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "PLANT":
                plants[tile.get("crop", "?")] += 1
            if tile.get("animal"):
                animals[tile["animal"]] += 1
                animal_tiles += 1
    town = obs.get("town", {})
    shops = sorted(town.get("unlocked_shops", []))
    shed = {k: int(v) for k, v in obs.get("private", {}).get("shed", {}).items() if int(v)}
    result = {
        "day": day, "observation_step": frame, "cash": float(farm.get("money", 0)),
        "hands": len(farm.get("hands", [])),
        "quadrants": len(farm.get("unlocked_quadrants", [])),
        "crop_tiles": sum(plants.values()), "plants_by_crop": dict(plants),
        "animal_tiles": animal_tiles, "animals_by_species": dict(animals),
        "shed_items": sum(shed.values()), "shed_by_item": shed,
        "shops": shops, "shop_regime": "|".join(shops) if shops else "none",
        "market_prices": obs.get("market", {}).get("prices", {}),
    }
    return result


def flatten_player(game_meta, replay, settled, seat):
    p = settled["players"][seat]
    phases = ("opening_0_5", "day6_11", "day12_23", "late_24_29")
    by_phase = p.get("accepted_value_by_phase", {})
    sell_by_phase = {ph: int(by_phase.get(ph, {}).get("SELL", 0)) for ph in phases}
    buyprod_by_phase = {ph: int(by_phase.get(ph, {}).get("BUY_PRODUCT", 0)) for ph in phases}
    netprod_by_phase = {ph: sell_by_phase[ph] - buyprod_by_phase[ph] for ph in phases}
    sells = p.get("accepted_value_by_product", {}).get("SELL", {})
    buys = p.get("accepted_value_by_product", {}).get("BUY_PRODUCT", {})
    buys_seed = p.get("accepted_value_by_product", {}).get("BUY_SEED", {})
    buys_animal = p.get("accepted_value_by_product", {}).get("BUY_ANIMAL", {})
    final_cash = [float(replay["steps"][-1][s]["observation"]["farms"][s]["money"]) for s in (0, 1)]
    phases_cash = {"opening_0_5": (0, 6*24), "day6_11": (6*24, 12*24),
                   "day12_23": (12*24, 24*24), "late_24_29": (24*24, len(replay["steps"])-1)}
    row = {
        "game_id": game_meta["game_id"], "seed": game_meta["seed"],
        "opponent": game_meta["opponent"], "seat": seat,
        "is_reset_v57": seat == game_meta["reset_seat"],
        "replay_sha256": settled["replay_sha256"],
        "final_cash": float(replay["steps"][-1][seat]["observation"]["farms"][seat]["money"]),
        "accepted_sell_value": int(sum(sells.values())),
        "accepted_product_buy_value": int(sum(buys.values())),
        "accepted_product_net": int(sum(sells.values()) - sum(buys.values())),
        "accepted_seed_buy_value": int(sum(buys_seed.values())),
        "accepted_animal_buy_value": int(sum(buys_animal.values())),
        "land_hire_net_cost": float(sum(p.get("land_and_hire_net_cost_by_phase", {}).values())),
        "wheat_fert_sale_value": int(sells.get("WHEAT", 0) + sells.get("FERTILIZER", 0)),
        "wheat_fert_product_buy_value": int(buys.get("WHEAT", 0) + buys.get("FERTILIZER", 0)),
        "wheat_fert_net": int(sells.get("WHEAT", 0) + sells.get("FERTILIZER", 0)
                               - buys.get("WHEAT", 0) - buys.get("FERTILIZER", 0)),
        "winner": final_cash[seat] > final_cash[1-seat],
        "opponent_reward": final_cash[1-seat],
        "game_gap_coins": abs(final_cash[seat] - final_cash[1-seat]),
        "accepted_units": p.get("accepted_units", {}),
        "sell_value_by_product": sells, "product_buy_value_by_product": buys,
        "seed_buy_value_by_product": buys_seed, "animal_buy_value_by_product": buys_animal,
        "net_product_cash_by_phase": netprod_by_phase,
        "sell_value_by_phase": sell_by_phase,
        "product_buy_value_by_phase": buyprod_by_phase,
        "state_day0": snapshot(replay, seat, 0),
        "state_day6": snapshot(replay, seat, 6),
        "state_day12": snapshot(replay, seat, 12),
        "state_day20": snapshot(replay, seat, 20),
        "state_day29": snapshot(replay, seat, 29),
        "total_sales": int(sum(sells.values())),
        "total_product_purchases": int(sum(buys.values())),
        "net_product_market": int(sum(sells.values()) - sum(buys.values())),
        "net_product_by_kind": {"SELL": sells, "BUY_PRODUCT": buys},
        "audit_max_cash_error": float(settled["audit"]["max_cash_error"]),
    }
    for day in (0, 6, 12, 20, 29):
        snap = row[f"state_day{day}"]
        prefix = f"day{day}_"
        row[prefix+"cash"] = snap["cash"]
        row[prefix+"hands"] = len(replay["steps"][snap["observation_step"]][seat]["observation"]["farms"][seat].get("hands", []))
        row[prefix+"quadrants"] = snap["quadrants"]
        row[prefix+"crop_tiles"] = snap["crop_tiles"]
        row[prefix+"animals"] = snap["animal_tiles"]
        row[prefix+"crop_mix"] = json.dumps(snap["plants_by_crop"], sort_keys=True, separators=(",", ":"))
        row[prefix+"animal_mix"] = json.dumps(snap["animals_by_species"], sort_keys=True, separators=(",", ":"))
        row[prefix+"shed"] = json.dumps(snap["shed_by_item"], sort_keys=True, separators=(",", ":"))
        row[prefix+"shed_value_current_price"] = sum(int(q)*float(snap["market_prices"].get(k, 0)) for k, q in snap["shed_by_item"].items())
        row[prefix+"shops"] = json.dumps(snap["shops"], separators=(",", ":"))
        row[prefix+"market_prices"] = json.dumps(snap["market_prices"], sort_keys=True, separators=(",", ":"))
    for phase, (i0, i1) in phases_cash.items():
        o0 = replay["steps"][i0][seat]["observation"]
        o1 = replay["steps"][i1][seat]["observation"]
        row[phase+"_cash_delta"] = round(float(o1["farms"][seat]["money"]) - float(o0["farms"][seat]["money"]), 2)
        row[phase+"_sales"] = sell_by_phase[phase]
        row[phase+"_product_purchases"] = buyprod_by_phase[phase]
        row[phase+"_seed_purchases"] = int(by_phase.get(phase, {}).get("BUY_SEED", 0))
        row[phase+"_animal_purchases"] = int(by_phase.get(phase, {}).get("BUY_ANIMAL", 0))
        row[phase+"_land_hire_cost"] = float(p.get("land_and_hire_net_cost_by_phase", {}).get(phase, 0))
        row[phase+"_market_net_product"] = netprod_by_phase[phase]
        row[phase+"_accepted_product_by_kind"] = json.dumps({op: p.get("accepted_value_by_product", {}).get(op, {}) for op in ("SELL", "BUY_PRODUCT")}, sort_keys=True, separators=(",", ":"))
    return row


def main():
    selected, options = list_records()
    seeds = sorted({x["seed"] for x in selected}, key=lambda x: (isinstance(x, str), x))
    if len(seeds) < 20:
        raise SystemExit(f"need >=20 unique spent seeds; found {len(seeds)}")
    players = []
    games = []
    manifest_rows = []
    for n, meta in enumerate(selected, 1):
        path = Path(meta["replay_path"])
        replay = json.loads(path.read_text())
        result = settle(path)
        if result["audit"]["cash_mismatches"] != 0:
            raise SystemExit(f"cash reconciliation failed for {path}: {result['audit']}")
        reset_seat = meta["reset_seat"]
        final = [float(replay["steps"][-1][s]["observation"]["farms"][s]["money"]) for s in (0, 1)]
        game = {
            "game_id": meta["game_id"], "seed": meta["seed"], "opponent": meta["opponent"],
            "reset_seat": reset_seat,
            "reset_result": "win" if final[reset_seat] > final[1-reset_seat] else "loss" if final[reset_seat] < final[1-reset_seat] else "draw",
            "original_candidate_result": meta.get("candidate_result"),
            "final_coins": final, "reset_reward": final[reset_seat],
            "opponent_reward": final[1-reset_seat], "replay_path": str(path.relative_to(ROOT)),
            "game_record": meta["game_record"], "replay_sha256": result["replay_sha256"],
            "settlement_audit": result["audit"],
        }
        games.append(game)
        for seat in (0, 1):
            players.append(flatten_player(meta, replay, result, seat))
        manifest_rows.append({k: meta[k] for k in ("game_id", "seed", "opponent", "reset_seat", "game_record")}
                             | {"replay_path": str(path.relative_to(ROOT)), "replay_sha256": result["replay_sha256"],
                                "agent_hashes": [a.get("sha256") for a in meta["agents"]]})
        if n % 5 == 0:
            print(f"settled {n}/{len(selected)} games; {len(seeds)} unique seeds", flush=True)
    (OUT / "games.json").write_text(json.dumps(games, separators=(",", ":"), sort_keys=True) + "\n")
    (OUT / "players.json").write_text(json.dumps(players, separators=(",", ":"), sort_keys=True) + "\n")
    (OUT / "manifest.json").write_text(json.dumps({
        "candidate_sha256": RESET_SHA, "settlement": "one-frame aligned accepted_sales.settle; engine cash reconciliation required zero mismatches",
        "selected_games": manifest_rows, "unique_seed_count": len(seeds),
        "selected_opponent_lineages": sorted({g["opponent"] for g in games}),
        "distinct_replay_count": len({g["replay_sha256"] for g in games}),
    }, indent=2, sort_keys=True) + "\n")
    for name, rows in (("games.csv", games), ("players.csv", players)):
        with (OUT / name).open("w", newline="") as f:
            cols = [k for k, v in rows[0].items() if not isinstance(v, (dict, list))]
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows({k: row.get(k) for k in cols} for row in rows)
    print(f"wrote {len(games)} games / {len(players)} player rows across {len(seeds)} seeds")

if __name__ == "__main__":
    main()
