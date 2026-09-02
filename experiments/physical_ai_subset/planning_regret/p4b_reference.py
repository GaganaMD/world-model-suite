"""Frozen P4b reference model and identity."""
import hashlib, json
def reference():
 return {'scenario_id':'P4b_COLLISION_RISK_TRADEOFF','reference_variant':'p4b_v1','objective_id':'p4b_tradeoff_v1','players':[{'id':'robot'}],'initial':[{'state':'s0','p':1.0}],'states':[
 {'id':'s0','turn':['robot'],'state_features':{'location':'start','goal_reached':False,'collision':False},'actions':[{'by':{'robot':'safe_route'},'next':[{'state':'goal','p':1.0}]},{'by':{'robot':'risky_route'},'next':[{'state':'goal','p':.5},{'state':'collision','p':.5}]}]},
 {'id':'goal','terminal':True,'state_features':{'location':'destination','goal_reached':True,'collision':False}},
 {'id':'collision','terminal':True,'state_features':{'location':'collision_site','goal_reached':False,'collision':True}}]}
def identity(m=None):
 m=m or reference(); return {'scenario_id':m['scenario_id'],'reference_variant':m['reference_variant'],'objective_id':m['objective_id'],'reference_hash':hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()}
