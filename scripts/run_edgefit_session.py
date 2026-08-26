from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefit_demo import UnoQTransport, run_edgefit_session


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the public EdgeFit host-to-UNO-Q orchestration boundary."
    )
    parser.add_argument("--front", required=True, type=Path)
    parser.add_argument("--side", required=True, type=Path)
    parser.add_argument("--height-cm", required=True, type=float)
    parser.add_argument("--weight-kg", required=True, type=float)
    parser.add_argument("--adb", default=None)
    parser.add_argument("--remote-root", default=None)
    parser.add_argument(
        "--keep-local-captures",
        action="store_true",
        help="Keep local session captures after the run. Remote captures are still removed.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    transport = UnoQTransport(adb=args.adb, remote_root=args.remote_root)

    try:
        transport.check_device()
        result = run_edgefit_session(
            args.front,
            args.side,
            args.height_cm,
            args.weight_kg,
            transport,
            cleanup_local=not args.keep_local_captures,
        )
    except Exception as exc:
        print(f"EDGEFIT_SESSION_ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Status: {result.status}")
    if result.status != "OK":
        print(f"Message: {result.message or 'No detail provided'}")
        return 2

    measurements = result.measurements_cm
    assert measurements is not None
    print(f"Execution target: {result.execution_target or 'Arduino UNO Q'}")
    print(f"Bust / chest: {measurements.bust:.1f} cm")
    print(f"Waist: {measurements.waist:.1f} cm")
    print(f"Hip: {measurements.hip:.1f} cm")
    print(f"Body shape: {result.shape or 'Not specified'}")
    print(f"Recommended size: {result.recommended_size or 'Not specified'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
