from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefit_demo import load_result


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/run_public_demo.py examples/sample_output.json")
        return 2

    result = load_result(sys.argv[1])
    print(f"Status: {result.status}")

    if result.status != "OK":
        print(f"Message: {result.message or 'No detail provided'}")
        return 1

    measurements = result.measurements_cm
    assert measurements is not None

    print(f"Execution target: {result.execution_target or 'Not specified'}")
    print(f"Bust / chest: {measurements.bust:.1f} cm")
    print(f"Waist: {measurements.waist:.1f} cm")
    print(f"Hip: {measurements.hip:.1f} cm")
    print(f"Body shape: {result.shape or 'Not specified'}")
    print(f"Recommended size: {result.recommended_size or 'Not specified'}")

    if result.regional_fit:
        ordered = ("chest", "waist", "hip")
        text = " | ".join(
            f"{region.title()}: {result.regional_fit[region]}"
            for region in ordered
            if region in result.regional_fit
        )
        if text:
            print(f"Regional fit: {text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
