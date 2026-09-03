# Aborted confirmatory network run

Freeze commit: `d4b7b65`.

The frozen 30-cell matrix was traversed once: 30 transport invocations and
30 persisted failure records, each with `attempt_number = 1`. There were zero
provider responses, zero raw model-output files, and no parsing or scientific
evaluation.

Every record reports a local `ConnectionError` with Windows socket error
`WinError 10013` while establishing the HTTPS connection to OpenRouter. No
HTTP status, OpenRouter request ID, provider response, or generated text is
present. The evidence therefore places the failure at local socket connection
setup, before a provider response and before scientific observation.

This batch is labeled **ABORTED_PRE_PROVIDER_NETWORK_FAILURE**. It is
provenance only and is not a scientific dataset. No prompts, models,
references, objectives, evaluator code, or other scientific files were
changed during the attempt.
