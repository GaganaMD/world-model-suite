"""Bounded action-trace comparison for small declarative POSGs.

This deliberately keeps action identifiers exact: it is a conservative
complement to permutation-aware structural matching, not a semantic oracle.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import product

def traces(model, horizon=3):
    states={s['id']:s for s in model.get('states',[])}; init=model.get('initial',[{}])[0].get('state')
    out={}
    def walk(s, seq, prob, depth):
        st=states.get(s,{})
        if depth>=horizon or st.get('terminal') or not st.get('actions'):
            out[tuple(seq)]=(bool(st.get('terminal')), prob); return
        for a in st.get('actions',[]):
            key='|'.join(f'{k}={v}' for k,v in sorted(a.get('by',{}).items()))
            for n in a.get('next',[]): walk(n['state'],seq+[key],prob*float(n.get('p',1.0)),depth+1)
    if init in states: walk(init,[],1.0,0)
    grouped=defaultdict(float)
    for seq,(terminal,p) in out.items(): grouped[(seq,terminal)]+=p
    return grouped

def compare_traces(reference,candidate,horizon=3):
    a,b=traces(reference,horizon),traces(candidate,horizon)
    common=set(k[0] for k in a)&set(k[0] for k in b)
    tv=0.0; terminal=0; probs=0; compared=0
    for seq in common:
        for t in (False,True):
            pa=a.get((seq,t),0.0); pb=b.get((seq,t),0.0); tv+=abs(pa-pb)/2
        terminal += int(any(k[0]==seq and k[1] for k in a)==any(k[0]==seq and k[1] for k in b))
        probs += int(all(abs(a.get((seq,t),0)-b.get((seq,t),0))<1e-9 for t in (False,True)))
        compared+=1
    return {'reference_traces':len(a),'candidate_traces':len(b),'common_sequences':len(common),
            'trace_sequence_coverage':len(common)/len(a) if a else 0.0,
            'trace_terminal_agreement':terminal/compared if compared else None,
            'trace_probability_exact':probs/compared if compared else None,
            'trace_probability_tv':tv/compared if compared else None,
            'behaviorally_equivalent': bool(common and len(common)==len(a)==len(b) and tv<1e-9)}
