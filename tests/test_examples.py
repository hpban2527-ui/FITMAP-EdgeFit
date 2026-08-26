import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_sample_input_has_two_views_and_body_metadata():
    payload = json.loads((ROOT / "examples" / "sample_input.json").read_text(encoding="utf-8"))
    assert set(payload) == {"front_view", "side_view", "height_cm", "weight_kg"}
    assert payload["height_cm"] > 0
    assert payload["weight_kg"] > 0


def test_result_schema_is_valid_json_and_declares_required_contract():
    schema = json.loads(
        (ROOT / "specs" / "edgefit_result.schema.json").read_text(encoding="utf-8")
    )
    assert schema["type"] == "object"
    assert "status" in schema["required"]
    assert "measurements_cm" in schema["properties"]
    assert "regional_fit" in schema["properties"]
