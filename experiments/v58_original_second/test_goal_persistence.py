"""Regression for carrying a cow through the absent-sheep/goose checks."""
import importlib.util
from pathlib import Path
import unittest


CANDIDATE = Path(__file__).with_name("original_second_candidate.py")
spec = importlib.util.spec_from_file_location("original_second_candidate", CANDIDATE)
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


class GoalPersistenceTest(unittest.TestCase):
    def test_cow_target_survives_missing_other_species_and_emits_place(self):
        goals = {(2, "COW"): (5, 3), (2, "SHEEP"): (4, 3), (2, "GOOSE"): (3, 2)}
        inventory = {"COW": 1}

        held = candidate._sync_carried_animal_goals(goals, 2, inventory)

        self.assertEqual(held, ["COW"])
        self.assertEqual(goals, {(2, "COW"): (5, 3)})
        task = [0, 0, (5, 3), "place", "COW", 2]
        unit = ["hand2", (5, 3), inventory]
        self.assertEqual(candidate._emit_task(task, unit, {}), ["PLACE", "COW"])

    def test_goal_is_cleared_after_inventory_is_empty(self):
        goals = {(2, "COW"): (5, 3)}
        self.assertEqual(candidate._sync_carried_animal_goals(goals, 2, {}), [])
        self.assertEqual(goals, {})


if __name__ == "__main__":
    unittest.main()
