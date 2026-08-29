"""Standalone end-to-end smoke test for the modular evaluation pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import torch

from src.evaluation import evaluate_world_model


REPOSITORY_ROOT = Path(__file__).resolve().parent
REFERENCE_MODELS = REPOSITORY_ROOT / "json_generation" / "reference_models.json"
OUTPUT_DIR = REPOSITORY_ROOT / "evaluation_results"


def main() -> None:
    models = json.loads(REFERENCE_MODELS.read_text(encoding="utf-8"))
    sample = models["1.1"]  # Dark storage-room robot from Copy_of_Test_Cases.ipynb.
    result = evaluate_world_model(
        candidate_model_path=sample,
        ground_truth_path=sample,
        save_pth=True,
        output_dir=str(OUTPUT_DIR),
    )

    print("\nPOSG Evaluation Summary")
    print("=" * 48)
    print(f"Lane 1 mechanical : {'PASS' if result['lane1']['passed'] else 'FAIL'}")
    print(
        "Lane 2 structural : "
        f"coverage={result['lane2']['coverage']:.3f}, "
        f"precision={result['lane2']['precision']:.3f}, "
        f"combined={result['lane2']['combined_score']:.3f}"
    )
    print(f"Lane 3 qualitative: {'PASS' if result['lane3']['checklist_passed'] else 'FAIL'}")
    print(f"Overall           : {'PASS' if result['overall_passed'] else 'FAIL'}")
    print("Artifacts:")
    for artifact in result["saved_artifacts"]:
        print(f"  - {artifact}")

    assert result["lane1"]["passed"], result["lane1"]["errors"]
    assert result["lane2"]["coverage"] == 1.0
    assert result["lane2"]["precision"] == 1.0
    assert result["lane3"]["checklist_passed"]
    assert result["saved_artifacts"], "no .pth artifacts were reported"
    for artifact in result["saved_artifacts"]:
        path = Path(artifact)
        assert path.suffix == ".pth" and path.is_file(), f"missing .pth artifact: {path}"
        payload = torch.load(path, weights_only=False)
        assert all(isinstance(node, str) for node in payload["node_ids"])
        assert payload["adjacency"].shape[0] == len(payload["node_ids"])

    print("\nEnd-to-end assertions passed.")


if __name__ == "__main__":
    main()
