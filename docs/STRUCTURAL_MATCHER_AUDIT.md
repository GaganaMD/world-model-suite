# Structural matcher audit

The production Lane-2 path is `json_generation/lane2.py`, which converts both
v2 models to the pinned `game_matching` representation and calls its intrinsic
state/action-structure matcher. The matcher searches a state alignment and a
player permutation; state and player identifiers therefore do not need to be
identical. Action profiles are compared through their aligned structural
roles, not by list position. Terminality, successor topology, and transition
probabilities in the finite-horizon conversion contribute to the score.

Coverage is the matched score divided by the reference self-match score;
precision divides by the candidate self-match score; F1 is their harmonic mean.
An exact match means normalized coverage, precision, and F1 are all 1.0. The
conversion unrolls cyclic models to horizon 3 (the same horizon for both sides),
adds a synthetic initial root where needed, and defaults missing terminal
payoffs to zero. Observations and rewards are not used as semantic evidence by
the structural score. State splitting/merging and alternative granularities
are not guaranteed to be equivalent and may be penalized.

The old fallback compared a coarse multiset of counts (state/action/edge
arities, terminal counts, and turn arities). It ignored which action led to
which successor. Consequently a candidate with the right global histogram but
wrong dynamics could score highly. The stricter matcher is expected to lower
such scores; this is a diagnostic difference, not proof that every decrease is
a semantic error.

Sanity tests cover identity, state ordering/renaming, player/action renaming,
missing and extra transitions/actions, terminality, probabilities, and
spurious reverse edges. The targeted matcher tests cover these cases. State splitting and
merging are explicitly treated as representation-sensitive cases rather than
silently declared equivalent.
