from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess
from typing import Any


class UnoQTransportError(RuntimeError):
    pass


class UnoQTransport:
    def __init__(
        self,
        adb: str | Path | None = None,
        remote_root: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.adb = str(adb or os.environ.get("EDGEFIT_ADB", "adb"))
        self.remote_root = remote_root or os.environ.get(
            "EDGEFIT_REMOTE_ROOT",
            "/home/arduino/fitmap_competition",
        )
        self.timeout_seconds = float(timeout_seconds)

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        try:
            process = subprocess.run(
                [self.adb, *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise UnoQTransportError(str(exc)) from exc

        if process.returncode != 0:
            detail = process.stderr.strip() or process.stdout.strip()
            raise UnoQTransportError(detail or "ADB command failed")
        return process

    def shell(self, command: str) -> str:
        return self._run("shell", command).stdout

    def check_device(self) -> None:
        state = self._run("get-state").stdout.strip().lower()
        if state != "device":
            raise UnoQTransportError(f"Unexpected ADB device state: {state or 'unknown'}")

    def push_capture_pair(self, front: str | Path, side: str | Path) -> None:
        front_path = Path(front)
        side_path = Path(side)
        for path in (front_path, side_path):
            if not path.is_file() or path.stat().st_size <= 0:
                raise UnoQTransportError(f"Invalid capture: {path}")

        remote_captures = f"{self.remote_root}/captures"
        remote_results = f"{self.remote_root}/results"
        self.shell(
            f"mkdir -p {shlex.quote(remote_captures)} {shlex.quote(remote_results)}"
        )
        self._run("push", str(front_path), f"{remote_captures}/front.jpg")
        self._run("push", str(side_path), f"{remote_captures}/side.jpg")

    def run_private_runtime(self, height_cm: float, weight_kg: float) -> dict[str, Any]:
        command = os.environ.get("EDGEFIT_REMOTE_COMMAND")
        if not command:
            raise UnoQTransportError(
                "EDGEFIT_REMOTE_COMMAND is not configured. "
                "The proprietary EdgeFit runtime is intentionally excluded from this repository."
            )

        rendered = command.format(
            remote_root=self.remote_root,
            height_cm=float(height_cm),
            weight_kg=float(weight_kg),
        )
        self.shell(rendered)

        result_path = f"{self.remote_root}/results/result.json"
        raw = self.shell(f"cat {shlex.quote(result_path)}")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise UnoQTransportError("UNO Q returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise UnoQTransportError("UNO Q result must be a JSON object")
        return payload

    def cleanup_remote_captures(self) -> None:
        capture_root = f"{self.remote_root}/captures"
        front = f"{capture_root}/front.jpg"
        side = f"{capture_root}/side.jpg"
        self.shell(f"rm -f {shlex.quote(front)} {shlex.quote(side)}")
