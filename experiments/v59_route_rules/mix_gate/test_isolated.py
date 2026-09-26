import importlib.util
import unittest
from pathlib import Path
from kaggle_environments.agent import get_last_callable

P=Path(__file__).with_name('candidate_isolated.py')
spec=importlib.util.spec_from_file_location('v59_isolated_test',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def make_obs(step=200, sheep=2, sheep_shed=0, goose_shed=0):
    board=[[None for _ in range(10)] for _ in range(10)]
    for y in range(10):
        for x in range(10):
            if x>=5 or y>=5: board[y][x]='LOCKED'
    pts=[(0,0),(1,0),(2,0),(3,0)]
    for x,y in pts[:sheep]: board[y][x]={'kind':'PASTURE','animal':'SHEEP'}
    board[1][1]={'kind':'PASTURE'}
    f={'farmer':[4,4],'hands':[],'money':3000,'tiles':board}
    return {'player':0,'day':step//24,'hour':step%24,'step':step,'farms':[f,dict(f)],
      'private':{'inventories':[{}],'seeds':{},'shed':{'SHEEP':sheep_shed,'GOOSE':goose_shed}},
      'market':{'prices':{'WOOL':190}},'town':{'unlocked_shops':['YARN_STORE']}}

class IsolatedMixTests(unittest.TestCase):
    def test_baseline_two_sheep_never_substitutes(self):
        o=make_obs(step=151,sheep=2)
        a={'farmer':['PASS'],'hands':[],'market':[['BUY_ANIMAL','GOOSE',2]]}
        self.assertEqual(m._v59_iso_apply(o,a),a)
    def test_extra_purchase_only_after_four_sheep(self):
        o=make_obs(step=217,sheep=4)
        a={'farmer':['PASS'],'hands':[],'market':[['BUY_ANIMAL','GOOSE',2]]}
        out=m._v59_iso_apply(o,a)
        self.assertEqual(out['market'],[['BUY_ANIMAL','GOOSE',1],['BUY_ANIMAL','SHEEP',1]])
    def test_only_converted_sheep_pickup_and_route_are_overridden(self):
        o=make_obs(step=217,sheep=4)
        a={'farmer':['PASS'],'hands':[],'market':[['BUY_ANIMAL','GOOSE',1]]}
        m._v59_iso_apply(o,a)
        o2=make_obs(step=218,sheep=4,sheep_shed=1)
        out2=m._v59_iso_apply(o2,{'farmer':['PICKUP','GOOSE',1],'hands':[],'market':[]})
        self.assertEqual(out2['farmer'],['PICKUP','SHEEP',1])
        o3=make_obs(step=289,sheep=4)
        o3['private']['inventories']=[{'SHEEP':1}]
        moved=m._v59_iso_apply(o3,{'farmer':['PASS'],'hands':[],'market':[]})
        self.assertEqual(moved['farmer'],['WEST'])
    def test_baseline_sheep_carrier_keeps_frozen_action(self):
        o=make_obs(step=289,sheep=3)
        o['private']['inventories']=[{'SHEEP':1}]
        action={'farmer':['EAST'],'hands':[],'market':[]}
        self.assertEqual(m._v59_iso_apply(o,action),action)
    def test_kaggle_loader_returns_action(self):
        fn=get_last_callable(P.read_text(),path=str(P));out=fn(make_obs(step=0,sheep=0),{})
        self.assertEqual(set(out),{'farmer','hands','market'})
        self.assertIsInstance(out['farmer'],list)
        self.assertIsInstance(out['hands'],list)
        self.assertIsInstance(out['market'],list)

if __name__=='__main__':unittest.main()
