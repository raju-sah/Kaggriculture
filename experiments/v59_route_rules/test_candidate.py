import importlib.util
import unittest
from pathlib import Path
from kaggle_environments.agent import get_last_callable

PATH=Path(__file__).with_name('candidate.py')
spec=importlib.util.spec_from_file_location('v59_candidate',PATH)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def obs0():
    board=[[None for _ in range(10)] for _ in range(10)]
    for y in range(10):
        for x in range(10):
            if x>=5 or y>=5: board[y][x]='LOCKED'
    farm={'farmer':[4,4],'hands':[[4,4],[4,4]],'money':3000,'tiles':board}
    return {'player':0,'day':0,'hour':0,'farms':[farm,dict(farm)],'private':{'inventories':[{}, {}, {}],'seeds':{'WHEAT':1,'STRAWBERRY':1},'shed':{}},'market':{'prices':{}}}

class RouteTests(unittest.TestCase):
    def test_seed_funded_tokens_are_aggregate_and_unique(self):
        o=obs0(); o['farms'][0]['farmer']=[0,0]; o['farms'][0]['hands']=[[1,0],[2,0]]; result=m.agent(o); actions=[result['farmer'],*result['hands']]
        self.assertEqual(sum(a[0]=='PLANT' for a in actions),2)
        self.assertEqual(len(actions),3)
    def test_boundary_move_is_masked(self):
        o=obs0(); o['farms'][0]['farmer']=[0,0]
        self.assertEqual(m.legal(['WEST'],o,0,0),['PASS'])
    def test_station_mapping_is_local_and_deterministic(self):
        self.assertEqual(m.station([4,4],10,1,4),(4,4))
        self.assertEqual(m.station([4,4],10,2,4),(5,4))
    def test_kaggle_exact_loader_returns_action_shape(self):
        fn=get_last_callable(PATH.read_text(),path=str(PATH))
        out=fn(obs0(),{})
        self.assertEqual(set(out),{'farmer','hands','market'})
        self.assertEqual(len(out['hands']),2)
        self.assertTrue(all(isinstance(x,list) and x for x in [out['farmer'],*out['hands'],*out['market']]))

if __name__=='__main__': unittest.main()
