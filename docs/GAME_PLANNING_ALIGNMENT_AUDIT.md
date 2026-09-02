# G1--G9 planning-alignment audit

All nine reference schemas provide executable dynamics and explicit rewards or
terminal rewards. However, strict generated-model policy evaluation additionally
requires reproducible action and reward alignment after state renaming. The
preserved candidates frequently rename/factor actions and sometimes invent
reward conventions; no repository artifact currently verifies those mappings.

| Game | Dynamics/actions | Objective | Stochastic | Strict generated planning | Reason |
|---|---|---|---|---|---|
| G1--G9 | yes | yes in reference | G2/G3/G6 stochastic; others deterministic | 0 candidates currently eligible | generated action/reward alignment unverified |

Thus the rigorous strict subset is currently empty (`N=0`), although the
reference-only planner and alignment eligibility pipeline are ready. We do not
turn a multi-agent game into an MDP or infer rewards from state names. A future
strict study must verify exact/normalized/structural action alignment, player
perspective, terminal utility, opponent treatment, and a common horizon per
candidate before computing regret in the canonical reference world.
