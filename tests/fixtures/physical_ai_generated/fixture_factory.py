"""Synthetic generated-Python candidates; never used for model data."""
import pprint
from experiments.physical_ai_subset.final_study.reference_spec import canonical_specs

def source_for(scenario_id, wrong=False):
    spec=next(s for s in canonical_specs() if s['scenario_id']==scenario_id)
    if wrong:
        # Valid dynamics with a deliberately suboptimal initial decision.
        s0=next(s for s in spec['states'] if s['id']=='s0')
        optimal=s0.get('actions',[{}])[0].get('by',{}).get('robot')
        alt=next((a for a in spec['allowed_actions'] if a!=optimal), optimal)
        for a in s0.get('actions',[]):
            if a.get('by',{}).get('robot')==optimal: a['next']=[{'state':'s0','p':1.0}]
        if not any(a.get('by',{}).get('robot')==alt for a in s0.get('actions',[])):
            s0.setdefault('actions',[]).append({'by':{'robot':alt},'next':[{'state':'goal','p':1.0}]})
        else:
            for a in s0['actions']:
                if a.get('by',{}).get('robot')==alt: a['next']=[{'state':'goal','p':1.0}]
    payload=pprint.pformat(spec,width=120)
    return f'''class GeneratedPOSG(AbstractPOSG):
    def __init__(self): self._m={payload}
    @property
    def players(self): return ["robot"]
    def initial_state(self): return self._m["initial"][0]["state"]
    def legal_actions(self,state,player):
        if player != "robot" or self.is_terminal(state): return []
        return [a["by"]["robot"] for a in next(s for s in self._m["states"] if s["id"]==state).get("actions",[])]
    def transition(self,state,joint_action):
        if self.is_terminal(state): return {{state:1.0}}
        a=joint_action.get("robot")
        p=next(a0 for a0 in next(s for s in self._m["states"] if s["id"]==state).get("actions",[]) if a0["by"]["robot"]==a)
        return {{n["state"]:float(n.get("p",1.0)) for n in p["next"]}}
    def observation(self,state,joint_action,next_state,player): return str(next_state)
    def reward(self,state,joint_action,next_state,player): return 0.0
    def is_terminal(self,state): return bool(next(s for s in self._m["states"] if s["id"]==state).get("terminal",False))
    def state_features(self,state): return next(s for s in self._m["states"] if s["id"]==state).get("state_features",{{}})
'''
