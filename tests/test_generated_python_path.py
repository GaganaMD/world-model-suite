from experiments.physical_ai_subset.final_study.evaluate_candidate import evaluate_python_code

SCAFFOLD='''class GeneratedPOSG:\n    def __init__(self): self.s="s0"\n'''

def test_generated_python_path_module_exists():
    assert callable(evaluate_python_code)
