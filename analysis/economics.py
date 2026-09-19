"""Extract a conservative static economic baseline from the official engine."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from kaggle_environments.envs.kaggriculture import kaggriculture as engine


SEASON_DAYS = 30


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_economic_snapshot() -> dict[str, Any]:
    engine_path = Path(engine.__file__).resolve()
    crop_rows = []
    for name, crop in engine.CROPS.items():
        base_price = engine.MARKET_PARAMS[name]["base"]
        gross = crop["max_yield"] * base_price
        profit = gross - crop["seed"]
        crop_rows.append(
            {
                "crop": name,
                **crop,
                "base_price": base_price,
                "gross_at_documented_max_yield": gross,
                "profit_before_labor_and_fertilizer": profit,
                "return_on_seed_capital": profit / crop["seed"],
                "profit_per_day_to_max_yield": profit / crop["max_yield_day"],
            }
        )

    animal_rows = []
    wheat_base_price = engine.MARKET_PARAMS["WHEAT"]["base"]
    for name, animal in engine.ANIMALS.items():
        production_days = list(
            range(animal["first_yield_day"], SEASON_DAYS, animal["interval"])
        )
        product = animal["product"]
        product_base_price = engine.MARKET_PARAMS[product]["base"]
        base_units = len(production_days)
        gross = base_units * product_base_price
        daily_feed_cost = (SEASON_DAYS - 1) * wheat_base_price
        animal_rows.append(
            {
                "animal": name,
                **animal,
                "structure_build_coin_cost": 0,
                "product_base_price": product_base_price,
                "base_production_days_if_placed_day_0": production_days,
                "base_units_before_care_bonus": base_units,
                "gross_base_product_revenue": gross,
                "daily_feed_cost_at_base_wheat_price": daily_feed_cost,
                "profit_before_labor_care_and_fertilizer": (
                    gross - animal["cost"] - daily_feed_cost
                ),
                "collectable_fertilizer_units_upper_bound": SEASON_DAYS - 1,
            }
        )

    market_rows = []
    for product, params in engine.MARKET_PARAMS.items():
        anchor = params["I0"]
        throughput = params["T"]
        market_rows.append(
            {
                "product": product,
                **params,
                "price_at_i0_minus_t": engine.market_price(product, anchor - throughput),
                "price_at_i0": engine.market_price(product, anchor),
                "price_at_i0_plus_t": engine.market_price(product, anchor + throughput),
                "price_at_i0_plus_2t": engine.market_price(product, anchor + 2 * throughput),
            }
        )

    return {
        "schema_version": 1,
        "engine": {
            "path": str(engine_path),
            "sha256": _sha256(engine_path),
        },
        "assumptions": [
            "Prices use the engine's static base/anchor curve and ignore opponent and town flow.",
            "Crop gross value uses documented max_yield and excludes movement, watering, fertilizer, decay, and reinvestment timing.",
            "Animal base production assumes placement on day 0, no care bonus, and daily feed valued at base wheat price.",
            "Animal fertilizer is reported as an upper bound and excluded from profit because collection and selling consume actions.",
            "These figures rank hypotheses only; simulations decide strategy quality.",
        ],
        "land_prices": list(engine.LAND_PRICES),
        "crops": crop_rows,
        "animals": animal_rows,
        "market": market_rows,
        "town_shops": engine.SHOPS,
    }


def _markdown(snapshot: dict[str, Any]) -> str:
    lines = [
        "# Kaggriculture static economic snapshot",
        "",
        f"Engine SHA-256: `{snapshot['engine']['sha256']}`",
        "",
        "These figures are hypothesis inputs. They exclude important labor, routing, timing, market, and opponent effects; simulations remain authoritative.",
        "",
        "## Crops at base price",
        "",
        "| Crop | Seed | Max units | Base price | Static profit | ROI | Profit/day to max |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in snapshot["crops"]:
        lines.append(
            f"| {row['crop']} | {row['seed']} | {row['max_yield']} | {row['base_price']} "
            f"| {row['profit_before_labor_and_fertilizer']} | {row['return_on_seed_capital']:.2f} "
            f"| {row['profit_per_day_to_max_yield']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Animals at base price",
            "",
            "| Animal | Capital | Product | Base units | Gross | Base feed cost | Profit before labor |",
            "|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    for row in snapshot["animals"]:
        lines.append(
            f"| {row['animal']} | {row['cost']} | {row['product']} "
            f"| {row['base_units_before_care_bonus']} | {row['gross_base_product_revenue']} "
            f"| {row['daily_feed_cost_at_base_wheat_price']} "
            f"| {row['profit_before_labor_care_and_fertilizer']} |"
        )
    lines.extend(["", "## Assumptions", ""])
    lines.extend(f"- {assumption}" for assumption in snapshot["assumptions"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/runs/economics"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_economic_snapshot()
    json_path = args.output_dir / "economics.json"
    markdown_path = args.output_dir / "economics.md"
    json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(snapshot), encoding="utf-8")
    print(json.dumps({"json": str(json_path.resolve()), "markdown": str(markdown_path.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
