"""Compact paired-match scanner: per-day public signals without replay bodies.

The tournament harness retains full replay bodies, which cost megabytes per
game. Signal-vs-outcome questions need the opposite: many seeds, tiny records.
This module runs one Kaggriculture match per isolated subprocess (never more
than four concurrent workers, matching the project's crash-containment rule)
and keeps only sampled public state:

* town shop-unlock sequence (shared, legal for both players),
* market price and inventory for tracked products at sampled days,
* each player's money, animal/structure/crop counts, hand count, land.

Everything here is observable inside an agent's own game, so a signal found by
this scanner can legally be used by a gate. `--summarize` reports how a
candidate day-gate separates paired outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from kaggle_environments import make

SAMPLE_DAYS = (0, 2, 3, 5, 6, 9, 12, 15, 20, 25, 29)
TRACK_PRODUCTS = ("MILK", "WOOL", "EGG", "WHEAT", "STRAWBERRY", "FERTILIZER")
ANIMAL_TYPES = ("COW", "SHEEP", "GOOSE")
STRUCTURE_KINDS = ("PASTURE", "COOP")

# Products each town shop drains, mirrored from the pinned engine (SHOPS).
SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _farm_summary(farm: dict[str, Any]) -> dict[str, Any]:
    animals = {kind: 0 for kind in ANIMAL_TYPES}
    structures = {kind: 0 for kind in STRUCTURE_KINDS}
    crops: dict[str, int] = {}
    weeds = empty = locked = 0
    for row in farm.get("tiles") or []:
        for tile in row:
            if tile is None:
                empty += 1
            elif isinstance(tile, str):
                locked += 1
            elif isinstance(tile, dict):
                kind = tile.get("kind")
                if kind in structures:
                    structures[kind] += 1
                    animal = tile.get("animal")
                    if animal in animals:
                        animals[animal] += 1
                elif kind == "PLANT":
                    crop = str(tile.get("crop", "?"))
                    crops[crop] = crops.get(crop, 0) + 1
                elif kind == "WEED":
                    weeds += 1
    return {
        "money": farm.get("money"),
        "animals": animals,
        "structures": structures,
        "crops": dict(sorted(crops.items())),
        "weeds": weeds,
        "empty": empty,
        "locked": locked,
        "hands": len(farm.get("hands") or []),
        "quadrants": list(farm.get("unlocked_quadrants") or []),
    }


def _snapshot(observation: dict[str, Any]) -> dict[str, Any]:
    market = observation.get("market") or {}
    prices = market.get("prices") or {}
    inventory = market.get("inventory") or {}
    return {
        "day": observation.get("day"),
        "shops": list((observation.get("town") or {}).get("unlocked_shops") or []),
        "prices": {item: prices.get(item) for item in TRACK_PRODUCTS},
        "inventory": {item: inventory.get(item) for item in TRACK_PRODUCTS},
        "farms": [_farm_summary(farm) for farm in observation.get("farms") or []],
    }

def run_match(agent_paths: list[Path], seed: int) -> dict[str, Any]:
    started = time.perf_counter()
    absolute_agents = [path.resolve() for path in agent_paths]
    base = {
        "seed": seed,
        "agents": [
            {"path": str(path), "sha256": _sha256_file(path)} for path in absolute_agents
        ],
    }
    try:
        environment = make(
            "kaggriculture",
            configuration={"episodeSteps": 720, "seed": seed},
            debug=True,
        )
        environment.run([str(path) for path in absolute_agents])
        samples = []
        seen: set[tuple[int, int]] = set()
        for turn in environment.steps:
            for seat, state in enumerate(turn):
                observation = state.observation
                day = observation.get("day")
                hour = observation.get("hour")
                if hour != 0 or day not in SAMPLE_DAYS or (day, seat) in seen:
                    continue
                seen.add((day, seat))
                samples.append({"seat": seat, **_snapshot(observation)})
        final_states = environment.steps[-1]
        rewards = [
            float(state.reward) if isinstance(state.reward, (int, float)) else None
            for state in final_states
        ]
        statuses = [str(state.status) for state in final_states]
        if rewards[0] is not None and rewards[1] is not None and rewards[0] != rewards[1]:
            winner = 0 if rewards[0] > rewards[1] else 1
        else:
            winner = None
        return {
            **base,
            "ok": all(status == "DONE" for status in statuses),
            "final_coins": rewards,
            "statuses": statuses,
            "winner_seat": winner,
            "samples": samples,
            "runtime_seconds": time.perf_counter() - started,
            "error": None,
        }
    except Exception as exc:  # A worker must preserve diagnostics for the parent.
        import traceback

        formatted = traceback.format_exc()
        return {
            **base,
            "ok": False,
            "final_coins": [None, None],
            "statuses": ["ERROR", "ERROR"],
            "winner_seat": None,
            "samples": [],
            "runtime_seconds": time.perf_counter() - started,
            "error": {"type": type(exc).__name__, "message": str(exc), "traceback": formatted},
        }


def _worker(agent_a: str, agent_b: str, seed: int, swapped: bool, result_path: Path) -> dict[str, Any]:
    paths = [Path(agent_b), Path(agent_a)] if swapped else [Path(agent_a), Path(agent_b)]
    record = run_match(paths, seed)
    record["swapped"] = swapped
    record["candidate_seat"] = 1 if swapped else 0
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    return {"seed": seed, "swapped": swapped, "ok": record["ok"]}

def _sample_for(record: dict[str, Any], seat: int, sample_day: int) -> dict[str, Any] | None:
    for sample in record["samples"]:
        if sample["seat"] == seat and sample["day"] == sample_day:
            return sample
    return None


def _signal_for(record: dict[str, Any], seat: int) -> dict[str, Any]:
    """Public signals visible to `seat` by day 6 (unlock at end of day 5)."""
    day6 = _sample_for(record, seat, 6) or _sample_for(record, seat, 5) or _sample_for(record, seat, 3)
    if day6 is None:
        return {}
    day9 = _sample_for(record, seat, 9) or day6
    own0 = _sample_for(record, seat, 0)
    shops6 = day6["shops"]
    shops9 = day9["shops"]
    milk6 = sum(1 for shop in shops6 if shop in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
    milk9 = sum(1 for shop in shops9 if shop in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
    yarn6 = sum(1 for shop in shops6 if shop == "YARN_STORE")
    yarn9 = sum(1 for shop in shops9 if shop == "YARN_STORE")
    egg6 = sum(1 for shop in shops6 if shop in ("BAKERY", "BRUNCH_SPOT"))
    egg9 = sum(1 for shop in shops9 if shop in ("BAKERY", "BRUNCH_SPOT"))
    day3 = _sample_for(record, seat, 3)
    shops3 = day3["shops"] if day3 else []
    d3 = shops3[0] if shops3 else None
    own6 = day6["farms"][seat] if seat < len(day6["farms"]) else {}
    return {
        "d3_shop": d3,
        "d3_milk": bool(d3 and "MILK" in SHOP_PRODUCTS.get(d3, ())),
        "d3_straw": bool(d3 and "STRAWBERRY" in SHOP_PRODUCTS.get(d3, ())),
        "d3_wool": bool(d3 and "WOOL" in SHOP_PRODUCTS.get(d3, ())),
        "shops6": len(shops6),
        "shops9": len(shops9),
        "milk6": milk6,
        "milk9": milk9,
        "yarn6": yarn6,
        "yarn9": yarn9,
        "egg6": egg6,
        "egg9": egg9,
        "animal6": milk6 + yarn6 + egg6,
        "animal9": milk9 + yarn9 + egg9,
        "straw_shops6": sum(1 for shop in shops6 if "STRAWBERRY" in SHOP_PRODUCTS.get(shop, ())),
        "price_milk6": day6["prices"]["MILK"],
        "price_wool6": day6["prices"]["WOOL"],
        "price_egg6": day6["prices"]["EGG"],
        "own_cash6": own6.get("money"),
        "own_animals6": sum(own6.get("animals", {}).values()) if own6 else None,
        "own_weeds0": (_sample_for(record, seat, 0) or {}).get("farms", [{}])[seat].get("weeds")
        if own0
        else None,
    }


def _seed_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_seed[record["seed"]].append(record)
    rows = []
    for seed in sorted(by_seed):
        seat_records = sorted(by_seed[seed], key=lambda record: record["candidate_seat"])
        diffs, signals_a, signals_b = [], [], []
        for record in seat_records:
            seat = record["candidate_seat"]
            candidate = record["final_coins"][seat]
            opponent = record["final_coins"][1 - seat]
            diffs.append(None if candidate is None or opponent is None else candidate - opponent)
            signals_a.append(_signal_for(record, seat))
            signals_b.append(_signal_for(record, 1 - seat))
        rows.append(
            {
                "seed": seed,
                "diff_seats": diffs,
                "diff_mean": (sum(value for value in diffs if value is not None) / len(diffs))
                if any(value is not None for value in diffs)
                else None,
                "signal_a": _merge_signals([signal for signal in signals_a if signal]),
                "signal_b": _merge_signals([signal for signal in signals_b if signal]),
            }
        )
    return rows



def _merge_signals(signals: list[dict[str, Any]]) -> dict[str, Any]:
    """Average a signal dict across the two seat assignments of one seed."""
    if not signals:
        return {}
    merged: dict[str, Any] = {}
    keys = signals[0].keys()
    for key in keys:
        values = [signal[key] for signal in signals if signal.get(key) is not None]
        if not values:
            merged[key] = None
        elif all(isinstance(value, (int, float)) for value in values):
            merged[key] = sum(values) / len(values)
        else:
            merged[key] = max(values, key=values.count)
    return merged


GATES = (
    ("animal6>=1", lambda sig: (sig.get("animal6") or 0) >= 1),
    ("animal6>=2", lambda sig: (sig.get("animal6") or 0) >= 2),
    ("animal6>=3", lambda sig: (sig.get("animal6") or 0) >= 3),
    ("milk6>=1", lambda sig: (sig.get("milk6") or 0) >= 1),
    ("milk6>=2", lambda sig: (sig.get("milk6") or 0) >= 2),
    ("yarn6>=1", lambda sig: (sig.get("yarn6") or 0) >= 1),
    ("egg6>=1", lambda sig: (sig.get("egg6") or 0) >= 1),
    ("animal9>=3", lambda sig: (sig.get("animal9") or 0) >= 3),
    ("shops6>=2", lambda sig: (sig.get("shops6") or 0) >= 2),
)


def _subgroup_stats(rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    diffs = [row["diff_mean"] for row in selected if row["diff_mean"] is not None]
    if not diffs:
        return {"seeds": 0, "mean": None, "median": None, "wins": 0, "losses": 0, "worst": None, "total": None}
    ordered = sorted(diffs)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    return {
        "seeds": len(diffs),
        "mean": sum(diffs) / len(diffs),
        "median": median,
        "wins": sum(1 for value in diffs if value > 0),
        "losses": sum(1 for value in diffs if value < 0),
        "worst": min(diffs),
        "total": sum(diffs),
    }


def summarize(records: list[dict[str, Any]], gate_view: str = "a") -> dict[str, Any]:
    rows = _seed_rows(records)
    key = f"signal_{gate_view}"
    gates = []
    for name, predicate in GATES:
        triggered = [row for row in rows if row[key] and predicate(row[key])]
        skipped = [row for row in rows if row[key] and not predicate(row[key])]
        gates.append(
            {
                "gate": name,
                "triggered": _subgroup_stats(rows, triggered),
                "skipped": _subgroup_stats(rows, skipped),
            }
        )
    return {"seeds": len(rows), "gate_view": gate_view, "rows": rows, "gates": gates}


def _worker_process(agent_a: Path, agent_b: Path, seed: int, swapped: bool, output_dir: Path) -> dict[str, Any]:
    result_path = output_dir / "games" / f"seed-{seed}-{'ba' if swapped else 'ab'}.json"
    command = [
        sys.executable,
        "-m",
        "analysis.pair_scan",
        "--worker",
        "--agent-a",
        str(agent_a),
        "--agent-b",
        str(agent_b),
        "--seed",
        str(seed),
        "--result",
        str(result_path),
    ]
    if swapped:
        command.append("--swapped")
    started = time.perf_counter()
    completed = subprocess.run(command, capture_output=True, text=True)
    return {
        "seed": seed,
        "swapped": swapped,
        "returncode": completed.returncode,
        "seconds": time.perf_counter() - started,
        "stderr": (completed.stderr or "").strip().splitlines()[-1] if completed.returncode else "",
    }


def _print_table(rows: list[dict[str, Any]], gate_view: str = "a") -> None:
    header = (
        f"{'seed':>6} | {'diff_s0':>9} {'diff_s1':>9} {'mean':>9} | "
        f"{'sh6':>3} {'an6':>3} {'mk6':>3} {'yr6':>3} {'eg6':>3} {'an9':>3} | "
        f"{'pM6':>5} {'pW6':>5}"
    )
    print(f"gate view: agent-{gate_view}")
    print(header)
    print("-" * len(header))
    for row in rows:
        signal = row[f"signal_{gate_view}"] or {}
        diffs = row["diff_seats"]
        def fmt(value: Any) -> str:
            return "   n/a" if value is None else f"{value:+.0f}".rjust(9)
        print(
            f"{row['seed']:>6} | {fmt(diffs[0])} {fmt(diffs[1] if len(diffs) > 1 else None)} "
            f"{fmt(row['diff_mean'])} | "
            f"{signal.get('shops6', '-'):>3} {signal.get('animal6', '-'):>3} "
            f"{signal.get('milk6', '-'):>3} {signal.get('yarn6', '-'):>3} "
            f"{signal.get('egg6', '-'):>3} {signal.get('animal9', '-'):>3} | "
            f"{signal.get('price_milk6', '-'):>5} {signal.get('price_wool6', '-'):>5}"
        )


def parse_seeds(value: str) -> list[int]:
    seeds: list[int] = []
    for part in value.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start, end = (int(piece) for piece in token.split("-", 1))
            seeds.extend(range(start, end + 1))
        else:
            seeds.append(int(token))
    return seeds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-a", type=Path, help="candidate agent (seat 0 unless --swapped)")
    parser.add_argument("--agent-b", type=Path, help="opponent agent")
    parser.add_argument("--seeds", help="comma-separated seeds and inclusive ranges, e.g. 4202-4241")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/runs/pair-scan"))
    parser.add_argument("--summarize", type=Path, help="summarize an existing scan directory")
    parser.add_argument("--gate-view", choices=("a", "b"), default="a",
                        help="whose day-6 view the gate signal is read from (a=candidate, b=opponent)")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--swapped", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--seed", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--result", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker:
        if not (args.agent_a and args.agent_b and args.seed is not None and args.result):
            parser.error("--worker needs --agent-a, --agent-b, --seed and --result")
        paths = [args.agent_b, args.agent_a] if args.swapped else [args.agent_a, args.agent_b]
        record = run_match(paths, args.seed)
        record["swapped"] = args.swapped
        record["candidate_seat"] = 1 if args.swapped else 0
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
        return 0

    if args.summarize:
        records = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((args.summarize / "games").glob("*.json"))
        ]
    else:
        if not (args.agent_a and args.agent_b and args.seeds):
            parser.error("provide --agent-a, --agent-b and --seeds (or use --summarize)")
        if not 1 <= args.workers <= 4:
            parser.error("--workers must be between 1 and 4")
        agent_a, agent_b = args.agent_a.resolve(), args.agent_b.resolve()
        seeds = parse_seeds(args.seeds)
        games_dir = args.output_dir / "games"
        games_dir.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        runs = []
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [
                executor.submit(_worker_process, agent_a, agent_b, seed, swapped, args.output_dir)
                for seed in seeds
                for swapped in (False, True)
            ]
            for future in as_completed(futures):
                runs.append(future.result())
        records = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(games_dir.glob("*.json"))
        ]
        failed = [run for run in runs if run["returncode"]]
        process = {
            "output_dir": str(args.output_dir.resolve()),
            "candidate": str(agent_a),
            "opponent": str(agent_b),
            "seeds": seeds,
            "workers": args.workers,
            "wall_seconds": time.perf_counter() - started,
            "worker_failures": failed,
            "games": len(records),
            "incomplete_games": [record["seed"] for record in records if not record["ok"]],
        }
        (args.output_dir / "process.json").write_text(
            json.dumps(process, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(process, indent=2, sort_keys=True))

    summary = summarize(records, args.gate_view)
    _print_table(summary["rows"], args.gate_view)
    print()
    for gate in summary["gates"]:
        print(f"{gate['gate']:>12}  triggered={gate['triggered']}  skipped={gate['skipped']}")
    if not args.summarize:
        (args.output_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

