import hashlib
import json
from pathlib import Path

import pytest

from experiments.physical_ai_subset.final_study.evaluate_candidate import evaluate_python_code
from experiments.physical_ai_subset.final_study_v2.ingest_confirmatory import IngestionError, ingest_and_evaluate
from tests.fixtures.physical_ai_generated.fixture_factory import source_for


SCENARIOS = [
    "P1_BLOCKED_DOOR",
    "P2_FRAGILE_DELIVERY",
    "P3_BATTERY_DELIVERY",
    "P4b_COLLISION_RISK_TRADEOFF",
    "P5_IRREVERSIBLE_SWITCH",
]


def cells(count=1):
    return [
        {
            "candidate_id": f"{SCENARIOS[index % len(SCENARIOS)]}_synthetic_R{index + 1}",
            "scenario": SCENARIOS[index % len(SCENARIOS)],
            "model": "synthetic/model",
            "run": str(index + 1),
            "prompt_hash": f"hash-{index}",
        }
        for index in range(count)
    ]


def make_transport(root: Path, rows, *, failure_ids=()):
    root = root / "restart_synthetic"
    raw, metadata, integrity = root / "raw", root / "metadata", root / "integrity"
    raw.mkdir(parents=True)
    metadata.mkdir()
    integrity.mkdir()
    failure_ids = set(failure_ids)
    for row in rows:
        record = {
            "candidate_id": row["candidate_id"],
            "scenario_id": row["scenario"],
            "model_id": row["model"],
            "run_id": row["run"],
            "prompt_hash": row["prompt_hash"],
            "execution_id": "synthetic",
            "attempt_number": 1,
            "provider_success": row["candidate_id"] not in failure_ids,
        }
        if record["provider_success"]:
            text = source_for(row["scenario"])
            path = raw / f"{row['candidate_id']}.txt"
            path.write_text(text, encoding="utf-8")
            record.update(raw_response_path=str(path.resolve()), raw_sha256=hashlib.sha256(text.encode()).hexdigest())
        (metadata / f"{row['candidate_id']}.json").write_text(json.dumps(record), encoding="utf-8")
    completion = {
        "execution_id": "synthetic",
        "authorized_cells": len(rows),
        "recorded_outcomes": len(rows),
        "unique_candidate_ids": len({row['candidate_id'] for row in rows}),
        "retries": 0,
        "replacements": 0,
        "fallbacks": 0,
        "collection_complete": True,
    }
    (integrity / "completion.json").write_text(json.dumps(completion), encoding="utf-8")
    return root


def test_exact_text_is_passed_once_without_extraction(tmp_path):
    rows = cells()
    root = make_transport(tmp_path, rows)
    seen = []

    def evaluator(scenario, text, model, run):
        seen.append((scenario, text, model, run))
        return {"marker": "ok"}

    result = ingest_and_evaluate(root, "synthetic", matrix_rows=rows, evaluator=evaluator)
    assert len(seen) == 1 and seen[0][1] == source_for(rows[0]["scenario"])
    assert result[0]["candidate_id"] == rows[0]["candidate_id"]
    assert result[0]["marker"] == "ok"


def test_provider_failure_is_unavailable_and_never_evaluated(tmp_path):
    rows = cells()
    root = make_transport(tmp_path, rows, failure_ids={rows[0]["candidate_id"]})
    result = ingest_and_evaluate(root, "synthetic", matrix_rows=rows, evaluator=lambda *_: pytest.fail("must not evaluate"))
    assert result[0]["evaluation_available"] is False
    assert result[0]["ingestion_exclusion_reason"] == "provider failure"


@pytest.mark.parametrize("mutation", ["missing_raw", "hash", "path", "malformed"])
def test_transport_integrity_failures_are_fail_closed(tmp_path, mutation):
    rows = cells()
    root = make_transport(tmp_path, rows)
    candidate = rows[0]["candidate_id"]
    metadata_path = root / "metadata" / f"{candidate}.json"
    if mutation == "missing_raw":
        (root / "raw" / f"{candidate}.txt").unlink()
    else:
        metadata = json.loads(metadata_path.read_text())
        if mutation == "hash":
            metadata["raw_sha256"] = "incorrect"
        elif mutation == "path":
            metadata["raw_response_path"] = str(root / "raw" / "other.txt")
        else:
            metadata = [metadata]
        metadata_path.write_text(json.dumps(metadata))
    with pytest.raises(IngestionError):
        ingest_and_evaluate(root, "synthetic", matrix_rows=rows, evaluator=lambda *_: {})


def test_candidate_id_mismatch_fails_closed(tmp_path):
    rows = cells()
    root = make_transport(tmp_path, rows)
    (root / "metadata" / f"{rows[0]['candidate_id']}.json").rename(root / "metadata" / "wrong.json")
    with pytest.raises(IngestionError):
        ingest_and_evaluate(root, "synthetic", matrix_rows=rows, evaluator=lambda *_: {})


def test_duplicate_matrix_candidate_fails_closed(tmp_path):
    rows = cells()
    root = make_transport(tmp_path, rows)
    with pytest.raises(IngestionError):
        ingest_and_evaluate(root, "synthetic", matrix_rows=[rows[0], dict(rows[0])], evaluator=lambda *_: {})


def test_all_thirty_synthetic_cells_route_once_without_repair_or_fallback(tmp_path):
    rows = cells(30)
    root = make_transport(tmp_path, rows)
    calls = []

    def evaluator(*args):
        calls.append(args)
        return {}

    result = ingest_and_evaluate(root, "synthetic", matrix_rows=rows, evaluator=evaluator)
    assert len(result) == 30
    assert len(calls) == 30
    assert len({row["candidate_id"] for row in result}) == 30


def test_evaluator_failure_is_not_retried_or_repaired(tmp_path):
    rows = cells()
    root = make_transport(tmp_path, rows)
    calls = []

    def failing_evaluator(*args):
        calls.append(args)
        raise RuntimeError("synthetic evaluator failure")

    with pytest.raises(RuntimeError, match="synthetic evaluator failure"):
        ingest_and_evaluate(root, "synthetic", matrix_rows=rows, evaluator=failing_evaluator)
    assert len(calls) == 1


def test_adapter_is_equivalent_to_direct_frozen_evaluator(tmp_path):
    rows = cells(5)
    root = make_transport(tmp_path, rows)
    routed = ingest_and_evaluate(root, "synthetic", matrix_rows=rows, evaluator=evaluate_python_code)
    for row, observed in zip(rows, routed):
        direct = evaluate_python_code(row["scenario"], source_for(row["scenario"]), row["model"], int(row["run"]))
        for key in (
            "contract_valid", "feature_contract_valid", "lane1_valid", "structural_evaluable",
            "structural_f1", "exact_structural_match", "planning_eligible", "generated_optimal_action",
            "reference_optimal_action", "policy_agreement", "planning_regret",
        ):
            assert observed[key] == direct[key]
