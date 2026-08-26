import json
from pathlib import Path

import pytest

from edgefit_demo.unoq_transport import UnoQTransport, UnoQTransportError


def test_push_rejects_missing_capture(tmp_path: Path):
    transport = UnoQTransport(adb="adb")
    with pytest.raises(UnoQTransportError):
        transport.push_capture_pair(tmp_path / "front.jpg", tmp_path / "side.jpg")


def test_push_rejects_empty_capture(tmp_path: Path):
    front = tmp_path / "front.jpg"
    side = tmp_path / "side.jpg"
    front.write_bytes(b"")
    side.write_bytes(b"side")
    transport = UnoQTransport(adb="adb")
    with pytest.raises(UnoQTransportError):
        transport.push_capture_pair(front, side)


def test_private_runtime_requires_authorized_command(monkeypatch):
    monkeypatch.delenv("EDGEFIT_REMOTE_COMMAND", raising=False)
    transport = UnoQTransport(adb="adb")
    with pytest.raises(UnoQTransportError, match="intentionally excluded"):
        transport.run_private_runtime(170, 60)


def test_private_runtime_parses_structured_json(monkeypatch):
    monkeypatch.setenv("EDGEFIT_REMOTE_COMMAND", "private-runner {height_cm} {weight_kg}")
    transport = UnoQTransport(adb="adb")
    calls = []

    def fake_shell(command: str) -> str:
        calls.append(command)
        if command.startswith("cat "):
            return json.dumps({"status": "RETAKE_FRONT", "measurements_cm": None})
        return ""

    transport.shell = fake_shell
    payload = transport.run_private_runtime(170, 60)

    assert payload["status"] == "RETAKE_FRONT"
    assert any("private-runner 170.0 60.0" in call for call in calls)


def test_remote_cleanup_targets_only_front_and_side():
    transport = UnoQTransport(adb="adb", remote_root="/tmp/edgefit")
    calls = []
    transport.shell = lambda command: calls.append(command) or ""
    transport.cleanup_remote_captures()
    assert len(calls) == 1
    assert "/tmp/edgefit/captures/front.jpg" in calls[0]
    assert "/tmp/edgefit/captures/side.jpg" in calls[0]
