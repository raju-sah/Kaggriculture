import unittest

from simulation.tournament import build_summary, parse_seeds


class TournamentSummaryTests(unittest.TestCase):
    def test_counts_seats_draws_and_determinism(self):
        records = [
            {
                "seed": 7,
                "swapped": False,
                "ok": True,
                "opponent": "baseline",
                "candidate_result": "win",
                "candidate_seat": 0,
                "opponent_seat": 1,
                "candidate_error": False,
                "opponent_error": False,
                "infrastructure_error": False,
                "timed_out": False,
                "runtime_seconds": 1.0,
                "final_coins": [20.0, 10.0],
                "statuses": ["DONE", "DONE"],
                "replay_sha256": "same-ab",
            },
            {
                "seed": 7,
                "swapped": False,
                "ok": True,
                "opponent": "baseline",
                "candidate_result": "win",
                "candidate_seat": 0,
                "opponent_seat": 1,
                "candidate_error": False,
                "opponent_error": False,
                "infrastructure_error": False,
                "timed_out": False,
                "runtime_seconds": 1.0,
                "final_coins": [20.0, 10.0],
                "statuses": ["DONE", "DONE"],
                "replay_sha256": "same-ab",
            },
            {
                "seed": 7,
                "swapped": True,
                "ok": True,
                "opponent": "baseline",
                "candidate_result": "draw",
                "candidate_seat": 1,
                "opponent_seat": 0,
                "candidate_error": False,
                "opponent_error": False,
                "infrastructure_error": False,
                "timed_out": False,
                "runtime_seconds": 1.0,
                "final_coins": [15.0, 15.0],
                "statuses": ["DONE", "DONE"],
                "replay_sha256": "same-ba",
            },
            {
                "seed": 7,
                "swapped": True,
                "ok": True,
                "opponent": "baseline",
                "candidate_result": "draw",
                "candidate_seat": 1,
                "opponent_seat": 0,
                "candidate_error": False,
                "opponent_error": False,
                "infrastructure_error": False,
                "timed_out": False,
                "runtime_seconds": 1.0,
                "final_coins": [15.0, 15.0],
                "statuses": ["DONE", "DONE"],
                "replay_sha256": "same-ba",
            },
        ]

        summary = build_summary(records)

        self.assertEqual(summary["wins"], 2)
        self.assertEqual(summary["draws"], 2)
        self.assertEqual(summary["losses"], 0)
        self.assertEqual(summary["win_rate"], 0.5)
        self.assertEqual(summary["score_rate"], 0.75)
        self.assertEqual(summary["mean_final_coins_candidate"], 17.5)
        self.assertEqual(summary["median_coin_difference_candidate"], 5.0)
        self.assertTrue(summary["deterministic"])

    def test_seed_ranges_are_inclusive_and_deduplicated(self):
        self.assertEqual(parse_seeds("1-3,3,8"), [1, 2, 3, 8])

    def test_candidate_error_is_counted_as_loss(self):
        record = {
            "opponent": "baseline",
            "seed": 1,
            "swapped": False,
            "candidate_result": "loss",
            "candidate_seat": 0,
            "opponent_seat": 1,
            "candidate_error": True,
            "opponent_error": False,
            "infrastructure_error": False,
            "timed_out": False,
            "runtime_seconds": 0.5,
            "final_coins": [None, 3000.0],
            "statuses": ["ERROR", "DONE"],
            "replay_sha256": None,
        }
        summary = build_summary([record])
        self.assertEqual(summary["losses"], 1)
        self.assertEqual(summary["candidate_errors"], 1)
        self.assertEqual(summary["win_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
