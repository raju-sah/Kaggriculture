import copy
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('candidate',Path(__file__).resolve().parents[1]/'agents/v57_agent.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


def observation(step=100):
    farm={'farmer':[4,4],'hands':[],'tiles':[[None]*10 for _ in range(10)],'money':3000}
    return {'player':0,'step':step,'day':step//24,'hour':step%24,'farms':[farm,copy.deepcopy(farm)],
            'private':{'shed':{'WHEAT':5,'MILK':5},'seeds':{},'inventories':[{}]},
            'town':{'unlocked_shops':[]},'market':{'prices':{'MILK':160,'WOOL':200,'WHEAT':25,'FERTILIZER':100}}}

class MarketControls(unittest.TestCase):
    def setUp(self):
        self.old=M._base_agent;M._v57_price_state.clear()
        self.action={'farmer':['PASS'],'hands':[],'market':[]}
        M._base_agent=lambda obs,c:copy.deepcopy(self.action)
    def tearDown(self):M._base_agent=self.old
    def test_empty_sells_removed_and_buy_barriers_preserved(self):
        self.action['market']=[['SELL','WOOL',10],['SELL','MILK',2],['SELL','MILK',3],['BUY_PRODUCT','WHEAT',1],['SELL','WHEAT',6]]
        obs=observation();before=copy.deepcopy(obs)
        self.assertEqual(M.agent(obs)['market'],[['SELL','MILK',5],['BUY_PRODUCT','WHEAT',1],['SELL','WHEAT',6]])
        self.assertEqual(obs,before)
    def test_online_decline_triggers_surplus_sale_and_reset_clears_memory(self):
        obs=observation();M.agent(obs)
        obs=observation(101);obs['market']['prices']['MILK']=150
        self.assertIn(['SELL','MILK',5],M.agent(obs)['market'])
        obs=observation(0);obs['market']['prices']['MILK']=100
        self.assertEqual(M.agent(obs)['market'],[])
        self.assertEqual(M._v57_price_state[0]['drift']['MILK'],0)
    def test_feed_and_fertilizer_not_sold_by_price_learning(self):
        obs=observation();obs['private']['shed']={'WHEAT':60,'FERTILIZER':30}
        self.assertEqual(M.agent(obs)['market'],[])
    def test_terminal_moves_then_sells_same_turn_drop(self):
        obs=observation(717);obs['farms'][0]['farmer']=[3,4];obs['private']['inventories']=[{'MILK':6}]
        self.assertEqual(M.agent(obs)['farmer'],['EAST'])
        obs=observation(718);obs['private']['inventories']=[{'MILK':6}]
        result=M.agent(obs)
        self.assertEqual(result['farmer'],['DROP'])
        self.assertIn(['SELL','MILK',11],result['market'])
    def test_purchase_sale_sequence_kept(self):
        self.action['market']=[['SELL','MILK',3],['BUY_PRODUCT','WHEAT',2],['SELL','MILK',2]]
        self.assertEqual(M.agent(observation())['market'],self.action['market'])

    def test_milk_demand_changes_later_sheep_purchase(self):
        self.action['market']=[['BUY_ANIMAL','SHEEP',1]]
        obs=observation(240)
        obs['town']['unlocked_shops']=['PIZZA_SHOP']
        obs['market']['prices']['MILK']=200
        self.assertEqual(M.agent(obs)['market'],[['BUY_ANIMAL','COW',1]])
        obs=observation(240)
        obs['town']['unlocked_shops']=['PIZZA_SHOP','YARN_STORE']
        self.assertEqual(M.agent(obs)['market'],[['BUY_ANIMAL','SHEEP',1]])
    def test_replacement_animal_delivered_to_pasture(self):
        self.action['farmer']=['PLACE','SHEEP',1]
        obs=observation(240)
        obs['private']['inventories']=[{'COW':1}]
        self.assertEqual(M.agent(obs)['farmer'],['PLACE','COW',1])

if __name__=='__main__':unittest.main()
