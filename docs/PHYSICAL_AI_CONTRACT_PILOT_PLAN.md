# Physical-AI contract pilot plan

After the prompt/scaffold revision, run exactly three new P4 generations: one
each from `openai/gpt-5.6-sol`, `anthropic/claude-opus-5`, and
`meta-llama/llama-3.3-70b-instruct`, with the identical prompt and one sample
per model. This is an interface-compliance pilot only; no P1/P2/P3/P5 calls are
included. Success requires at least 2/3 first-pass Lane-1 passes (preferred
3/3). The six earlier outputs will not be retried or modified.
