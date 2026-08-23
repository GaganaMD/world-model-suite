# World Model EDA

`WorldModelEDA` provides exploratory, graph-focused analysis for finite generated POSGs.
It accepts the JSON-style schema used by the game test cases or an implementation of the
notebook's `AbstractPOSG` interface. For `AbstractPOSG`, it enumerates the reachable state
space from the initial state, including all legal joint actions and stochastic outcomes.

```python
from world_model_eda import WorldModelEDA

analysis = WorldModelEDA.from_dict(generated_model)
report = analysis.summary()
analysis.plot_state_graph()
```

The report includes state, action, transition, terminal-distance, and graph statistics.
`build_state_graph()`, `build_state_action_graph()`, and
`build_player_action_state_graph()` return NetworkX directed graphs. Plotting methods use
Matplotlib. Install the visualization dependencies with:

```shell
python -m pip install networkx matplotlib
```

Run the G1 sanity-check example with `python examples\game_eda.py`, and the focused tests
with `python -m unittest tests.test_world_model_eda`.
