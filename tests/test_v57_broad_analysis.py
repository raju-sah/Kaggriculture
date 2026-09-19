import unittest

from experiments.v57_broad.analyze import compare, pair_index, seed_bootstrap


def game(seed, seat, won, opponent='control'):
    scores = [20, 10] if (won == (seat == 0)) else [10, 20]
    return {'seed': seed, 'candidate_seat': seat, 'opponent': opponent,
            'candidate_result': 'win' if won else 'loss', 'final_coins': scores}


class PairedAnalysisTests(unittest.TestCase):
    def test_matches_by_seed_and_seat_not_completion_order(self):
        candidate = [game(1, 0, True), game(1, 1, True), game(2, 0, False), game(2, 1, False)]
        baseline = [game(2, 1, False), game(1, 0, False), game(2, 0, False), game(1, 1, True)]
        result = compare(candidate, baseline, [1, 2])
        self.assertEqual(result['win_rate_gain_pp'], 25)
        self.assertEqual(result['mean_margin_gain'], 5)
        self.assertEqual(result['positive_win_flips'], 1)
        self.assertEqual(result['negative_win_flips'], 0)
        self.assertEqual(result['seed_win_rate_deltas'], {1: .5, 2: 0})

    def test_rejects_missing_pairs_and_duplicate_records(self):
        with self.assertRaises(ValueError):
            compare([game(1, 0, True)], [game(1, 1, True)], [1])
        with self.assertRaises(ValueError):
            pair_index([game(1, 0, True), game(1, 0, True)])

    def test_bootstrap_retains_uncertainty_between_seed_blocks(self):
        self.assertEqual(seed_bootstrap([-1, 1], samples=10000), [-1, 1])
        self.assertEqual(seed_bootstrap([.25] * 30, samples=100), [.25, .25])


if __name__ == '__main__':
    unittest.main()
