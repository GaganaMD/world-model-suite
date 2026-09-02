"""Deterministic policy transfer via task-defined initial decision context."""
def transfer_initial_action(generated, canonical_actions=('safe_route','risky_route')):
    state=generated.initial_state()
    if generated.is_terminal(state): raise ValueError('generated initial state is terminal')
    actions=list(generated.legal_actions(state,'robot'))
    if not all(a in canonical_actions for a in actions) or not set(canonical_actions)<=set(actions):
        raise ValueError('initial state does not expose the canonical action set')
    return state, actions
