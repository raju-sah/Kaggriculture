"""Behavior checks for v57's observation-driven controls."""
import copy
import importlib.util
from pathlib import Path
import unittest

SPEC=importlib.util.spec_from_file_location('v57_under_test',Path(__file__).with_name('lizs_herd.py'))
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)


def state(step=100, position=(4,4), inventory=None):
    farm={'farmer':list(position),'hands':[],'tiles':[[None for _ in range(10)] for _ in range(10)],'money':3000}
    return {'player':0,'step':step,'day':step//24,'hour':step%24,'farms':[farm,copy.deepcopy(farm)],
            'private':{'shed':{'WHEAT':5},'seeds':{},'inventories':[inventory or {}]},
            'town':{'unlocked_shops':[]},'market':{'prices':{'MILK':160,'WOOL':200,'WHEAT':25,'FERTILIZER':100}}}


def action(op):
    return {'farmer':[op],'hands':[],'market':[]}


class Controls(unittest.TestCase):
    def test_does_not_replace_valid_feed(self):
        obs=state(inventory={'WHEAT':1});obs['farms'][0]['tiles'][4][4]={'animal':'COW','fed_today':False,'yield_units':6}
        self.assertEqual(M._repair_noops(obs,action('FEED'))['farmer'],['FEED'])

    def test_repairs_empty_harvest_to_feed(self):
        obs=state(inventory={'WHEAT':1});obs['farms'][0]['tiles'][4][4]={'animal':'COW','fed_today':False,'yield_units':0}
        self.assertEqual(M._repair_noops(obs,action('HARVEST'))['farmer'],['FEED'])

    def test_terminal_returns_valuable_load_before_deadline(self):
        obs=state(717,position=(3,4),inventory={'MILK':6})
        self.assertEqual(M._recover_terminal(obs,action('CARE'))['farmer'],['EAST'])
        obs=state(718,inventory={'MILK':6})
        self.assertEqual(M._recover_terminal(obs,action('CARE'))['farmer'],['DROP'])

    def test_terminal_does_not_redirect_early_route(self):
        obs=state(500,position=(0,0),inventory={'MILK':6})
        self.assertEqual(M._recover_terminal(obs,action('SOUTH'))['farmer'],['SOUTH'])

    def test_actual_replacement_animal_is_placed(self):
        old=M._before_herd
        try:
            M._before_herd=lambda o,c:{'farmer':['PLACE','SHEEP',1],'hands':[],'market':[]}
            obs=state(inventory={'COW':1})
            self.assertEqual(M.agent(obs)['farmer'],['PLACE','COW',1])
        finally:M._before_herd=old

    def test_unfavorable_town_preserves_sheep_purchase(self):
        old=M._before_herd
        try:
            M._before_herd=lambda o,c:{'farmer':['PASS'],'hands':[],'market':[['BUY_ANIMAL','SHEEP',1]]}
            obs=state();obs['town']['unlocked_shops']=['YARN_STORE','PIZZA_SHOP']
            self.assertEqual(M.agent(obs)['market'],[['BUY_ANIMAL','SHEEP',1]])
        finally:M._before_herd=old

if __name__=='__main__':unittest.main()
