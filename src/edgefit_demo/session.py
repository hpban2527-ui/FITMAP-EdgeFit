from __future__ import annotations

from pathlib import Path

from .contracts import EdgeFitResult
from .session_cleanup import cleanup_local_captures
from .unoq_transport import UnoQTransport


def run_edgefit_session(
    front: str | Path,
    side: str | Path,
    height_cm: float,
    weight_kg: float,
    transport: UnoQTransport,
    *,
    cleanup_local: bool = True,
) -> EdgeFitResult:
    front_path = Path(front)
    side_path = Path(side)

    for path in (front_path, side_path):
        if not path.is_file() or path.stat().st_size <= 0:
            raise ValueError(f"Invalid capture: {path}")

    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("height_cm and weight_kg must be positive")

    capture_dir = front_path.parent
    if side_path.parent != capture_dir:
        raise ValueError("Front and side captures must use the same session directory")

    try:
        transport.push_capture_pair(front_path, side_path)
        payload = transport.run_private_runtime(height_cm, weight_kg)
        result = EdgeFitResult.from_mapping(payload)
    except Exception:
        if cleanup_local:
            try:
                cleanup_local_captures(capture_dir)
            except OSError:
                pass
        try:
            transport.cleanup_remote_captures()
        except Exception:
            pass
        raise

    if cleanup_local:
        cleanup_local_captures(capture_dir)
    transport.cleanup_remote_captures()
    return result
