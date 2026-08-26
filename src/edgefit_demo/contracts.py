from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Measurements:
    bust: float
    waist: float
    hip: float

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "Measurements":
        required = ("bust", "waist", "hip")
        missing = [key for key in required if key not in value]
        if missing:
            raise ValueError(f"Missing measurement fields: {', '.join(missing)}")
        return cls(*(float(value[key]) for key in required))


@dataclass(frozen=True)
class EdgeFitResult:
    status: str
    measurements_cm: Measurements | None
    shape: str | None
    recommended_size: str | None
    regional_fit: dict[str, str] | None
    execution_target: str | None
    message: str | None = None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "EdgeFitResult":
        status = str(payload.get("status", "")).strip()
        if not status:
            raise ValueError("Result status is required")

        measurements_value = payload.get("measurements_cm")
        measurements = None
        if measurements_value is not None:
            if not isinstance(measurements_value, dict):
                raise ValueError("measurements_cm must be an object or null")
            measurements = Measurements.from_mapping(measurements_value)

        regional_value = payload.get("regional_fit")
        regional_fit = None
        if regional_value is not None:
            if not isinstance(regional_value, dict):
                raise ValueError("regional_fit must be an object or null")
            regional_fit = {str(k): str(v) for k, v in regional_value.items()}

        if status == "OK" and measurements is None:
            raise ValueError("Successful results require measurements_cm")

        if status != "OK" and measurements is not None:
            raise ValueError("Failure results must not contain body measurements")

        return cls(
            status=status,
            measurements_cm=measurements,
            shape=_optional_string(payload.get("shape")),
            recommended_size=_optional_string(payload.get("recommended_size")),
            regional_fit=regional_fit,
            execution_target=_optional_string(payload.get("execution_target")),
            message=_optional_string(payload.get("message")),
        )

    def to_mapping(self) -> dict[str, Any]:
        measurements = None
        if self.measurements_cm is not None:
            measurements = {
                "bust": self.measurements_cm.bust,
                "waist": self.measurements_cm.waist,
                "hip": self.measurements_cm.hip,
            }
        return {
            "status": self.status,
            "measurements_cm": measurements,
            "shape": self.shape,
            "recommended_size": self.recommended_size,
            "regional_fit": self.regional_fit,
            "execution_target": self.execution_target,
            "message": self.message,
        }


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def load_result(path: str | Path) -> EdgeFitResult:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("EdgeFit result must be a JSON object")
    return EdgeFitResult.from_mapping(payload)
