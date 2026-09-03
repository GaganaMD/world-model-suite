"""Frozen final-study reference specifications recovered from the committed builder."""
import copy

def specs():
    def env(scenario, actions, states, objective, invariant, variant='v1', objective_id=None):
        for s in states:
            if not s.get('terminal'): s.setdefault('turn',['robot'])
        return {'scenario_id':scenario,'reference_variant':variant,'objective_id':objective_id or scenario.lower()+'_objective_v1','players':[{'id':'robot'}],'initial':[{'state':'s0','p':1.0}],'allowed_actions':actions,'states':states,'objective':objective,'invariant':invariant}
    return [
      env('P1_BLOCKED_DOOR',['move_left','move_right','open_door'],[
        {'id':'s0','state_features':{'location':'left','door_open':False,'goal_reached':False},'actions':[{'by':{'robot':'open_door'},'next':[{'state':'s1','p':1}]},{'by':{'robot':'move_right'},'next':[{'state':'s0','p':1}]}]},
        {'id':'s1','state_features':{'location':'left','door_open':True,'goal_reached':False},'actions':[{'by':{'robot':'move_right'},'next':[{'state':'goal','p':1}]}]},
        {'id':'goal','terminal':True,'state_features':{'location':'right','door_open':True,'goal_reached':True}}], 'reach destination; a closed door blocks traversal','door remains closed until open_door; goal is reachable after opening'),
      env('P2_FRAGILE_DELIVERY',['move','pick_up','drop','deliver'],[
        {'id':'s0','state_features':{'robot_location':'start','object_location':'start','carrying':False,'broken':False,'delivered':False},'actions':[{'by':{'robot':'pick_up'},'next':[{'state':'carrying','p':1}]}]},
        {'id':'carrying','state_features':{'robot_location':'start','object_location':'carried','carrying':True,'broken':False,'delivered':False},'actions':[{'by':{'robot':'move'},'next':[{'state':'dropoff','p':1}]}]},
        {'id':'dropoff','state_features':{'robot_location':'dropoff','object_location':'carried','carrying':True,'broken':False,'delivered':False},'actions':[{'by':{'robot':'deliver'},'next':[{'state':'goal','p':1}]},{'by':{'robot':'drop'},'next':[{'state':'broken','p':1}]}]},
        {'id':'broken','terminal':True,'state_features':{'robot_location':'dropoff','object_location':'dropoff','carrying':False,'broken':True,'delivered':False}},
        {'id':'goal','terminal':True,'state_features':{'robot_location':'dropoff','object_location':'dropoff','carrying':False,'broken':False,'delivered':True}}], 'deliver the object intact','broken object cannot recover without a repair action (none exists)'),
      env('P3_BATTERY_DELIVERY',['move','charge','deliver'],[
        {'id':'s0','state_features':{'location':'start','battery':1,'package_delivered':False,'failed':False},'actions':[{'by':{'robot':'move'},'next':[{'state':'s1','p':1}]},{'by':{'robot':'charge'},'next':[{'state':'s0','p':1}]}]},
        {'id':'s1','state_features':{'location':'destination','battery':0,'package_delivered':False,'failed':False},'actions':[{'by':{'robot':'deliver'},'next':[{'state':'goal','p':1}]}]},
        {'id':'goal','terminal':True,'state_features':{'location':'destination','battery':0,'package_delivered':True,'failed':False}},
        {'id':'dead','terminal':True,'state_features':{'location':'destination','battery':0,'package_delivered':False,'failed':True}}], 'deliver the package with finite battery','battery does not increase except through charge; movement consumes battery'),
      env('P4b_COLLISION_RISK_TRADEOFF',['safe_route','risky_route'],[
        {'id':'s0','state_features':{'location':'start','goal_reached':False,'collision':False},'actions':[{'by':{'robot':'safe_route'},'next':[{'state':'goal','p':1}]},{'by':{'robot':'risky_route'},'next':[{'state':'goal','p':.5},{'state':'collision','p':.5}]}]},
        {'id':'goal','terminal':True,'state_features':{'location':'destination','goal_reached':True,'collision':False}},
        {'id':'collision','terminal':True,'state_features':{'location':'collision_site','goal_reached':False,'collision':True}}], 'reach destination via a safe longer route or a shorter risky route; collision is possible on risky_route','collision-risk tradeoff; collision is irreversible', variant='p4b_v1', objective_id='p4b_tradeoff_v1'),
      env('P5_IRREVERSIBLE_SWITCH',['move','press_switch'],[
        {'id':'s0','state_features':{'location':'start','switch_pressed':False,'access_open':False,'goal_reached':False},'actions':[{'by':{'robot':'press_switch'},'next':[{'state':'s1','p':1}]}]},
        {'id':'s1','state_features':{'location':'corridor','switch_pressed':True,'access_open':True,'goal_reached':False},'actions':[{'by':{'robot':'move'},'next':[{'state':'goal','p':1}]}]},
        {'id':'goal','terminal':True,'state_features':{'location':'target','switch_pressed':True,'access_open':True,'goal_reached':True}}], 'press the irreversible switch and reach the target','switch state cannot revert'),
    ]

def canonical_specs(): return copy.deepcopy(specs())
