import importlib.util
import json
import unittest
from pathlib import Path
from kaggle_environments.agent import get_last_callable

HERE=Path(__file__).resolve().parent
p=HERE/'candidate.py'
spec=importlib.util.spec_from_file_location('mix_gate_candidate',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def obs(gate=True):
    board=[[None for _ in range(10)] for _ in range(10)]
    for y in range(10):
        for x in range(10):
            if x>=5 or y>=5: board[y][x]='LOCKED'
    board[1][1]={'kind':'PASTURE'}
    farm={'farmer':[4,4],'hands':[],'money':3000,'tiles':board}
    return {'player':0,'day':6 if gate else 24,'hour':7,'farms':[farm,dict(farm)],
            'private':{'inventories':[{}],'seeds':{},'shed':{'SHEEP':0,'GOOSE':0}},
            'market':{'prices':{'WOOL':190}},
            'town':{'unlocked_shops':['YARN_STORE'] if gate else []}}

class MixGateTests(unittest.TestCase):
    def test_gate_is_early_yarn_and_high_wool_only(self):
        self.assertTrue(m._v59_yarn_gate(obs(True)))
        self.assertFalse(m._v59_yarn_gate(obs(False)))
        bad=obs(True);bad['market']['prices']['WOOL']=179
        self.assertFalse(m._v59_yarn_gate(bad))
    def test_one_goose_unit_becomes_sheep_when_gate_open(self):
        o=obs(True);a={'farmer':['PASS'],'hands':[],'market':[['BUY_ANIMAL','GOOSE',2]]}
        got=m._v59_mix_gate(o,a)
        self.assertEqual(got['market'],[['BUY_ANIMAL','GOOSE',1],['BUY_ANIMAL','SHEEP',1]])
    def test_closed_gate_preserves_goose_order(self):
        o=obs(False);a={'farmer':['PASS'],'hands':[],'market':[['BUY_ANIMAL','GOOSE',2]]}
        self.assertEqual(m._v59_mix_gate(o,a)['market'],[['BUY_ANIMAL','GOOSE',2]])
    def test_no_capacity_and_no_land_skips_market_conversion(self):
        o=obs(True);o['farms'][0]['tiles'][1][1]=None
        a={'farmer':['PASS'],'hands':[],'market':[['BUY_ANIMAL','GOOSE',1]]}
        self.assertEqual(m._v59_mix_gate(o,a)['market'],[['BUY_ANIMAL','GOOSE',1]])
    def test_land_order_allows_one_future_capacity_slot(self):
        o=obs(True);o['farms'][0]['tiles'][1][1]=None
        a={'farmer':['PASS'],'hands':[],'market':[['BUY_LAND'],['BUY_ANIMAL','GOOSE',2]]}
        self.assertEqual(m._v59_mix_gate(o,a)['market'],[['BUY_LAND'],['BUY_ANIMAL','GOOSE',1],['BUY_ANIMAL','SHEEP',1]])
    def test_gated_goose_pickup_uses_sheep_stock(self):
        o=obs(True);o['private']['shed']['SHEEP']=1
        a={'farmer':['PICKUP','GOOSE',1],'hands':[],'market':[]}
        self.assertEqual(m._v59_mix_gate(o,a)['farmer'],['PICKUP','SHEEP',1])
    def test_sheep_carrier_routes_to_available_pasture(self):
        o=obs(False);o['private']['inventories']=[{'SHEEP':1}]
        a={'farmer':['PASS'],'hands':[],'market':[]}
        out=m._v59_mix_gate(o,a)
        self.assertEqual(out['farmer'],['WEST'])
    def test_exact_kaggle_loader(self):
        o=obs(True);fn=get_last_callable(p.read_text(),path=str(p));out=fn(o,{})
        self.assertEqual(set(out),{'farmer','hands','market'})
        self.assertIsInstance(out['farmer'],list)
        self.assertIsInstance(out['market'],list)

if __name__=='__main__':unittest.main()
