# Threat model

The human/overseer delegates a bounded job to a controller. The controller starts a worker/agent which holds authority to invoke an external capability/provider. In a real deployment that authority could be network access, an API credential, a message-send capability, or another side-effecting permission. Here it is only a local mock provider.

The failure condition is that the controller believes execution has stopped or returned while the delegated worker can still invoke its capability. The relevant assets are the capability itself, its scope and duration, and evidence needed to account for its use. An orphaned or surviving child can create fail-open behavior. Separate worker and provider ledgers expose that a local response record is not, by itself, proof of the complete provider-side action history.

This is an operational containment problem. It does not assume intent, deception, or adversarial behavior by a model.
