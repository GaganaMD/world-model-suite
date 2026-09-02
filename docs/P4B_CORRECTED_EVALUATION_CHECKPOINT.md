# P4b corrected evaluation checkpoint

- Preserved prompt: P4b with state features; GPT/Claude generation-valid,
  Llama mechanically invalid.
- Evaluator now uses immutable scenario/reference/objective IDs and rejects
  legacy P4 references.
- Location validation accepts arbitrary scenario-defined strings.
- P4b reference self-tests pass: exact self-match, safe_route, value 0.6,
  threshold 2/9.
- Corrected structural F1: GPT 0.2403; Claude 0.1360; Llama NA.
- No candidate has reported regret: policy transfer is not yet complete and
  Llama has empty transitions.
- No calls were made during correction. These remain pilot/debug artifacts;
  clean final study requirement remains 30 calls.
