from pathlib import Path

import pytest

from edgefit_demo.contracts import EdgeFitResult, load_result


ROOT = Path(__file__).resolve().parents[1]


def test_sample_output_is_valid():
    result = load_result(ROOT / "examples" / "sample_output.json")
    assert result.status == "OK"
    assert result.measurements_cm is not None
    assert result.execution_target == "Arduino UNO Q"


def test_success_requires_measurements():
    with pytest.raises(ValueError):
        EdgeFitResult.from_mapping({"status": "OK", "measurements_cm": None})


def test_failure_cannot_fabricate_measurements():
    with pytest.raises(ValueError):
        EdgeFitResult.from_mapping(
            {
                "status": "MODEL_ERROR",
                "measurements_cm": {"bust": 90, "waist": 70, "hip": 95},
            }
        )


def test_failure_without_measurements_is_valid():
    result = EdgeFitResult.from_mapping(
        {
            "status": "RETAKE_SIDE",
            "measurements_cm": None,
            "message": "Side view is required.",
        }
    )
    assert result.status == "RETAKE_SIDE"
    assert result.measurements_cm is None


def test_blank_status_is_rejected():
    with pytest.raises(ValueError):
        EdgeFitResult.from_mapping({"status": "  "})


def test_missing_measurement_field_is_rejected():
    with pytest.raises(ValueError):
        EdgeFitResult.from_mapping(
            {"status": "OK", "measurements_cm": {"bust": 90, "waist": 70}}
        )


def test_regional_fit_must_be_object_or_null():
    with pytest.raises(ValueError):
        EdgeFitResult.from_mapping(
            {
                "status": "OK",
                "measurements_cm": {"bust": 90, "waist": 70, "hip": 95},
                "regional_fit": "Balanced",
            }
        )


def test_result_round_trip_preserves_public_fields():
    original = load_result(ROOT / "examples" / "sample_output.json")
    restored = EdgeFitResult.from_mapping(original.to_mapping())
    assert restored == original
