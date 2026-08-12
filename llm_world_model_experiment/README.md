# LLM World Model Experiment

This prototype studies whether Codex, acting as the LLM under study, can turn natural-language grid-world scenarios into executable Python world models.

Executable world models are useful because their behavior can be probed. The evaluation compares behavior, not source-code similarity.

Faithfulness means the generated environment matches the intended reference world on movement, obstacle blocking, transitions, reachability, shortest paths, and final answers.

## Components

- A. Ground truth: `reference/`
- B. LLM-generated worlds: `generated_worlds/`
- C. Behavioral evaluation harness: `run_experiment.py` plus `results/`

## Results

- Execution success rate: 1.000
- Behavioral test pass rate: 1.000
- Task-answer accuracy: 1.000
- World-model fidelity: 1.000

## Limitations

Small deterministic grids, one-shot generated code from a shared prototype script, limited sandboxing, and a compact behavioral probe suite.

## Next Experiment

Use a fixed prompt template, generate multiple independent model attempts per scenario, add hidden tests, and test refinements where the LLM must repair a generated world after seeing behavioral failures.
