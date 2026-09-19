"""Fast invariant checks for the exp-0044 state-derived opener.

Covers the constants that encode the public replay geometry and the agent
entry point's behavior on a synthetic day-0 observation. Full-pattern smoke
traces (day-0/day-1 invariant assertions against the live engine) live in the
experiment records; see experiments/runs/exp-0044-dev-gate-001.
"""
import unittest

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("candidate_main", Path(__file__).resolve().parents[1] / "main.py")
main = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(main)


class OpenerGeometryTest(unittest.TestCase):
    def test_all_opener_tiles_in_nw_quadrant(self):
        """NW quadrant is x,y in 0..4 on the 10x10 board; y=5 is LOCKED SW."""
        tile_sets = (
            main.OPENER_WHEAT_TILES,
            main.OPENER_MELON_TILES,
            main.OPENER_MELON_DAY1_TILES,
            main.OPENER_COW_SPOTS,
            main.OPENER_SHEEP_SPOTS,
            main.OPENER_PASTURES,
        )
        for tiles in tile_sets:
            for x, y in tiles:
                self.assertTrue(0 <= x <= 4 and 0 <= y <= 4, f"tile ({x},{y}) outside NW")

    def test_geometry_matches_public_replay(self):
        """Exact end-of-day-0 map from the five public top-vs-top replays."""
        self.assertEqual(
            main.OPENER_WHEAT_TILES,
            ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (2, 2), (0, 3), (0, 4)),
        )
        self.assertEqual(
            main.OPENER_MELON_TILES,
            ((3, 1), (4, 1), (1, 2), (3, 2), (1, 3), (1, 4)),
        )
        self.assertEqual(main.OPENER_MELON_DAY1_TILES, ((3, 0), (4, 0), (2, 3), (3, 3)))
        self.assertEqual(main.OPENER_COW_SPOTS, ((4, 4), (4, 2)))
        self.assertEqual(main.OPENER_SHEEP_SPOTS, ((4, 3), (3, 4), (2, 4)))

    def test_no_tile_overlap_between_footprints(self):
        self.assertEqual(set(main.OPENER_WHEAT_TILES) & set(main.OPENER_MELON_TILES), set())
        self.assertEqual(set(main.OPENER_MELON_TILES) & set(main.OPENER_MELON_DAY1_TILES), set())

    def test_constants_single_source_of_truth(self):
        """The deleted duplicate block must not resurrect (MELON_SEED_COST=80,
        one OPENER_PASTURES definition feeding both planner and market)."""
        self.assertEqual(main.MELON_SEED_COST, 80)
        self.assertEqual(main.OPENER_HANDS_TARGET, 4)
        self.assertEqual(len(main.OPENER_PASTURES), 5)


class AgentEntryTest(unittest.TestCase):
    @staticmethod
    def _day0_obs(hour, money=3000.0):
        tiles = [[None] * 10 for _ in range(10)]
        for y in range(10):
            for x in range(5, 10):
                tiles[y][x] = "LOCKED"
        return {
            "player": 0,
            "day": 0,
            "hour": hour,
            "farms": [{
                "money": money,
                "farmer": [4, 4],
                "hands": [],
                "hires_today": 0,
                "unlocked_quadrants": ["NW"],
                "tiles": tiles,
            }],
            "private": {
                "shed": {k: 0 for k in ("WHEAT", "FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "COW", "SHEEP", "GOOSE")},
                "seeds": {k: 0 for k in ("WHEAT", "MELON", "STRAWBERRY", "CARROT", "TOMATO")},
                "inventories": [{}],
            },
            "market": {"prices": {"WHEAT": 25, "FERTILIZER": 100}},
            "town": {"unlocked_shops": []},
        }

    def test_day0_ladder_fires(self):
        action = main.agent(self._day0_obs(1))
        self.assertIn(["BUY_ANIMAL", "COW", 2], action["market"])
        self.assertIn(["BUY_ANIMAL", "SHEEP", 3], action["market"])
        self.assertEqual(action["market"].count(["HIRE"]), 4)
        self.assertEqual(action["farmer"][0], "BUILD_PASTURE")

    def test_actions_are_schema_valid(self):
        for hour in range(24):
            action = main.agent(self._day0_obs(hour))
            self.assertIsInstance(action, dict)
            self.assertIsInstance(action["farmer"], list)
            self.assertIsInstance(action["hands"], list)
            self.assertIsInstance(action["market"], list)
            for unit in [action["farmer"], *action["hands"]]:
                self.assertTrue(isinstance(unit, list) and unit, unit)
            for order in action["market"]:
                self.assertTrue(isinstance(order, list) and order and isinstance(order[0], str), order)

    def test_ladder_guards_against_low_money(self):
        obs = self._day0_obs(1, money=50.0)
        action = main.agent(obs)
        for order in action["market"]:
            if order[0] == "BUY_SEED" and order[1] == "WHEAT":
                self.assertLessEqual(order[2] * 10, 50.0, "wheat seed buy unaffordable")
            elif order[0] == "BUY_ANIMAL":
                self.fail("animal buy unaffordable at $50")
            elif order[0] == "BUY_SEED" and order[1] == "MELON":
                self.fail("melon seed buy unaffordable at $50")


if __name__ == "__main__":
    unittest.main()
