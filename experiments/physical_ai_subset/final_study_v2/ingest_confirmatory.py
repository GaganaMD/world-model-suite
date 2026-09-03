"""Blinded, representation-only transport-to-evaluator ingestion.

This module deliberately knows nothing about GeneratedPOSG syntax or task
semantics.  Collection stores the provider's ``message.content`` verbatim in
``raw/<candidate_id>.txt``.  The only conversion here is reading that exact
text after checking the collector metadata and handing it to the frozen
``evaluate_python_code`` entry point.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parent
REQUIRED_MATRIX_FIELDS = {"candidate_id", "scenario", "model", "run", "prompt_hash"}


class IngestionError(RuntimeError):
    """A transport/provenance failure that must not be repaired or bypassed."""


def load_authorized_matrix(path: Path | None = None) -> list[dict[str, str]]:
    """Read the frozen collection matrix and reject malformed identifiers."""
    path = ROOT / "candidate_matrix.csv" if path is None else Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or not REQUIRED_MATRIX_FIELDS.issubset(rows[0] or {}):
        raise IngestionError("candidate matrix has an unexpected schema")
    ids = [row["candidate_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise IngestionError("candidate matrix contains duplicate candidate IDs")
    return rows


def _load_json(path: Path, description: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IngestionError(f"{description} is unreadable: {path.name}") from exc
    if not isinstance(value, dict):
        raise IngestionError(f"{description} has an unexpected envelope: {path.name}")
    return value


def _validate_completion(root: Path, expected_count: int, execution_id: str) -> None:
    completion = _load_json(root / "integrity" / "completion.json", "completion manifest")
    expected = {
        "execution_id": execution_id,
        "authorized_cells": expected_count,
        "recorded_outcomes": expected_count,
        "unique_candidate_ids": expected_count,
        "retries": 0,
        "replacements": 0,
        "fallbacks": 0,
        "collection_complete": True,
    }
    for key, value in expected.items():
        if completion.get(key) != value:
            raise IngestionError(f"completion manifest failed {key} validation")


def _metadata_for(root: Path, cell: dict[str, str], execution_id: str) -> dict:
    candidate_id = cell["candidate_id"]
    metadata = _load_json(root / "metadata" / f"{candidate_id}.json", "metadata")
    expected = {
        "candidate_id": candidate_id,
        "scenario_id": cell["scenario"],
        "model_id": cell["model"],
        "run_id": str(cell["run"]),
        "prompt_hash": cell["prompt_hash"],
        "execution_id": execution_id,
        "attempt_number": 1,
    }
    for key, value in expected.items():
        if str(metadata.get(key)) != str(value):
            raise IngestionError(f"metadata mismatch for {candidate_id}: {key}")
    return metadata


def ingest_and_evaluate(
    execution_root: Path,
    execution_id: str,
    *,
    matrix_rows: Iterable[dict[str, str]] | None = None,
    evaluator: Callable[[str, str, str, int], dict] | None = None,
) -> list[dict]:
    """Validate collector artifacts and route exact provider text once.

    ``evaluator`` defaults to the frozen generated-Python evaluator.  Tests
    inject a fake evaluator, so no real collected artifact is opened while the
    ingestion boundary is developed or tested.
    """
    execution_root = Path(execution_root)
    rows = load_authorized_matrix() if matrix_rows is None else list(matrix_rows)
    if not rows:
        raise IngestionError("no authorized cells")
    ids = [row.get("candidate_id") for row in rows]
    if any(not identifier for identifier in ids) or len(ids) != len(set(ids)):
        raise IngestionError("authorized matrix contains duplicate or missing candidate IDs")
    _validate_completion(execution_root, len(rows), execution_id)

    metadata_paths = list((execution_root / "metadata").glob("*.json"))
    if {path.stem for path in metadata_paths} != set(ids):
        raise IngestionError("metadata candidate IDs do not exactly match the authorized matrix")

    if evaluator is None:
        from experiments.physical_ai_subset.final_study.evaluate_candidate import evaluate_python_code

        evaluator = evaluate_python_code

    routed: list[dict] = []
    for cell in rows:
        candidate_id = cell["candidate_id"]
        metadata = _metadata_for(execution_root, cell, execution_id)
        if metadata.get("provider_success") is not True:
            routed.append(
                {
                    "candidate_id": candidate_id,
                    "scenario": cell["scenario"],
                    "model": cell["model"],
                    "run": int(cell["run"]),
                    "provider_success": False,
                    "evaluation_available": False,
                    "ingestion_exclusion_reason": "provider failure",
                }
            )
            continue

        raw_path = execution_root / "raw" / f"{candidate_id}.txt"
        recorded_path = metadata.get("raw_response_path")
        if not isinstance(recorded_path, str) or Path(recorded_path).resolve() != raw_path.resolve():
            raise IngestionError(f"raw response path mismatch for {candidate_id}")
        if not raw_path.is_file():
            raise IngestionError(f"raw response file missing for {candidate_id}")
        text = raw_path.read_text(encoding="utf-8")
        if hashlib.sha256(text.encode()).hexdigest() != metadata.get("raw_sha256"):
            raise IngestionError(f"raw response hash mismatch for {candidate_id}")

        # No extraction, parsing, normalization, repair, or retry occurs here.
        result = evaluator(cell["scenario"], text, cell["model"], int(cell["run"]))
        result = dict(result)
        result.update(
            candidate_id=candidate_id,
            scenario=cell["scenario"],
            model=cell["model"],
            run=int(cell["run"]),
            provider_success=True,
            evaluation_available=True,
            ingestion_exclusion_reason="NA",
        )
        routed.append(result)
    return routed
