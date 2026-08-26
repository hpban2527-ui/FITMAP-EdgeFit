from __future__ import annotations

from pathlib import Path

from .unoq_transport import UnoQTransport


def cleanup_local_captures(capture_dir: str | Path) -> None:
    root = Path(capture_dir)
    for name in ("front.jpg", "side.jpg"):
        (root / name).unlink(missing_ok=True)


def cleanup_session(
    capture_dir: str | Path,
    transport: UnoQTransport | None = None,
) -> None:
    cleanup_local_captures(capture_dir)
    if transport is not None:
        transport.cleanup_remote_captures()
