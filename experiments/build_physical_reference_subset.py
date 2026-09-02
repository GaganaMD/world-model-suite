"""Build five tiny symbolic embodied POSG references; no model calls."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'experiments/paper_extension_results/physical_reference'; OUT.mkdir(parents=True,exist_ok=True)
def env(name, actions, states, objective, invariant):
    for state in states:
        if not state.get('terminal'):
            state.setdefault('turn', ['robot'])
    return {'id':name,'players':[{'id':'robot'}],'initial':[{'state':'s0','p':1.0}], 'states':states,'objective':objective,'invariant':invariant,'allowed_actions':actions}
def main():
    cases=[
      env('P1_blocked_door',['move_left','move_right','open_door'],[{'id':'s0','state_features':{'door_open':False,'location':'left'},'actions':[{'by':{'robot':'open_door'},'next':[{'state':'s1','p':1}]},{'by':{'robot':'move_right'},'next':[{'state':'s0','p':1}]}]},{'id':'s1','state_features':{'door_open':True,'location':'left'},'actions':[{'by':{'robot':'move_right'},'next':[{'state':'goal','p':1}]}]},{'id':'goal','terminal':True,'state_features':{'success':True}}],'reach goal','closed door blocks traversal'),
      env('P2_fragile_delivery',['move','pick_up','drop','deliver'],[{'id':'s0','actions':[{'by':{'robot':'pick_up'},'next':[{'state':'carrying','p':1}]}]},{'id':'carrying','actions':[{'by':{'robot':'move'},'next':[{'state':'dropoff','p':1}]}]},{'id':'dropoff','actions':[{'by':{'robot':'deliver'},'next':[{'state':'goal','p':1}]},{'by':{'robot':'drop'},'next':[{'state':'broken','p':1}]}]},{'id':'broken','terminal':True,'state_features':{'broken':True}},{'id':'goal','terminal':True,'state_features':{'success':True}}],'deliver intact object','broken object cannot recover'),
      env('P3_battery_delivery',['move','charge','deliver'],[{'id':'s0','actions':[{'by':{'robot':'move'},'next':[{'state':'s1','p':1}]},{'by':{'robot':'charge'},'next':[{'state':'s0','p':1}]}]},{'id':'s1','actions':[{'by':{'robot':'deliver'},'next':[{'state':'goal','p':1}]}]},{'id':'goal','terminal':True,'state_features':{'success':True}},{'id':'dead','terminal':True,'state_features':{'failure':True}}],'deliver with battery','movement consumes battery'),
      env('P4_collision_risk',['safe_route','risky_route'],[{'id':'s0','actions':[{'by':{'robot':'safe_route'},'next':[{'state':'goal','p':1}]},{'by':{'robot':'risky_route'},'next':[{'state':'goal','p':0.8},{'state':'collision','p':0.2}]}]},{'id':'goal','terminal':True,'state_features':{'success':True}},{'id':'collision','terminal':True,'state_features':{'unsafe':True,'failure':True}}],'reach goal while avoiding collision','collision probability is 0.2'),
      env('P5_irreversible_switch',['move','press_switch'],[{'id':'s0','actions':[{'by':{'robot':'press_switch'},'next':[{'state':'s1','p':1}]}]},{'id':'s1','actions':[{'by':{'robot':'move'},'next':[{'state':'goal','p':1}]}]},{'id':'goal','terminal':True,'state_features':{'success':True}}],'reach target','switch state cannot revert')]
    rows=[]
    for c in cases:
        rows.append({'id':c['id'],'states':len(c['states']),'actions':len(c['allowed_actions']),'transition_support':sum(len(a.get('next',[])) for s in c['states'] for a in s.get('actions',[])),'objective':c['objective'],'invariant':c['invariant']})
    (OUT/'references.json').write_text(json.dumps(cases,indent=2),encoding='utf-8'); (OUT/'summary.csv').write_text('id,states,actions,transition_support,objective,invariant\n'+'\n'.join(','.join(str(x[k]) for k in rows[0]) for x in rows),encoding='utf-8')
if __name__=='__main__': main()
