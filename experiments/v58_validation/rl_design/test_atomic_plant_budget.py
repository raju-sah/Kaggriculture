"""Regression test for Kaggriculture's whole-action simultaneous PLANT rule."""
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name('candidate.py')
spec=importlib.util.spec_from_file_location('rl_candidate',SOURCE)
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)

class PlantSeedBudgetTests(unittest.TestCase):
    def test_over_budget_crop_requests_are_masked_as_a_batch(self):
        actions=[['PLANT','WHEAT'],['WATER'],['PLANT','WHEAT'],['PLANT','CARROT'],['PLANT','WHEAT']]
        result=policy._reserve_plant_seeds(actions,{'WHEAT':2,'CARROT':0})
        self.assertEqual(result,[['PLANT','WHEAT'],['WATER'],['PLANT','WHEAT'],['PASS'],['PASS']])
        self.assertEqual(sum(a[0]=='PLANT' and a[1]=='WHEAT' for a in result),2)
        self.assertEqual(sum(a[0]=='PLANT' and a[1]=='CARROT' for a in result),0)

    def test_nonplant_actions_and_independent_crop_budgets_are_preserved(self):
        actions=[['PLANT','WHEAT'],['PLANT','CARROT'],['WATER'],['PLANT','CARROT']]
        self.assertEqual(policy._reserve_plant_seeds(actions,{'WHEAT':1,'CARROT':2}),actions)

    def test_task_tokens_are_seed_funded_and_horizon_bounded(self):
        board=[[None for _ in range(10)] for _ in range(10)]
        params={**policy.PARAMS,'crop_target':8,'herd_target':0}
        farm={"tiles":board}
        actors=[[4,4]]
        private={"shed":{},"seeds":{"WHEAT":0},"inventories":[{}]}
        obs={"day":10}
        self.assertFalse(any(t[1]=='PLANT' for t in policy._tasks(obs,farm,private,actors,board,params)))
        private["seeds"]["WHEAT"]=2
        plants=[t for t in policy._tasks(obs,farm,private,actors,board,params) if t[1]=='PLANT']
        self.assertEqual(len(plants),2)
        self.assertFalse(any(t[1]=='PLANT' for t in policy._tasks({"day":26},farm,private,actors,board,params)))

    def test_no_seed_purchase_after_last_profitable_sowing_day(self):
        params={**policy.PARAMS,'crop_target':8,'herd_target':0,'staff_target':0}
        board=[[None for _ in range(10)] for _ in range(10)]
        farm={"tiles":board,"money":10000}
        private={"shed":{},"seeds":{"WHEAT":0},"inventories":[{}]}
        obs={"day":26,"hour":0,"market":{"prices":{}}}
        orders=policy._manager_market(obs,farm,private,board,[[4,4]],params,())
        self.assertFalse(any(o[:2]==['BUY_SEED','WHEAT'] for o in orders))

if __name__=='__main__':unittest.main()
