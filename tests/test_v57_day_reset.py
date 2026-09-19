"""Observed late-night weed repair must not displace the next day's route."""
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class DayResetRegression(unittest.TestCase):
    def test_real_collision_resumes_morning_route(self):
        spec=importlib.util.spec_from_file_location('reset_candidate',ROOT/'experiments/v57_broad/v57_reset_candidate.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        observations=json.loads((ROOT/'experiments/v57_broad/diagnostics/day_reset_fixture.json').read_text())
        actions=[module.agent(obs)['farmer'] for obs in observations]
        self.assertEqual(actions,[['DIG'],['PLANT','WHEAT'],['WEST']])

if __name__=='__main__':unittest.main()
