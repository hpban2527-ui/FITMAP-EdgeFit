from pathlib import Path

import pytest

from edgefit_demo.session import run_edgefit_session


class FakeTransport:
    def __init__(self, payload):
        self.payload = payload
        self.pushed = False
        self.cleaned = False

    def push_capture_pair(self, front, side):
        self.pushed = True

    def run_private_runtime(self, height_cm, weight_kg):
        return self.payload

    def cleanup_remote_captures(self):
        self.cleaned = True


def write_pair(tmp_path: Path):
    front = tmp_path / "front.jpg"
    side = tmp_path / "side.jpg"
    front.write_bytes(b"front")
    side.write_bytes(b"side")
    return front, side


def success_payload():
    return {
        "status": "OK",
        "measurements_cm": {"bust": 91.4, "waist": 75.7, "hip": 97.4},
        "shape": "Pear",
        "recommended_size": "M",
        "regional_fit": {"chest": "Loose", "waist": "Loose", "hip": "Loose"},
        "execution_target": "Arduino UNO Q",
    }


def test_session_connects_transport_contract_and_cleanup(tmp_path: Path):
    front, side = write_pair(tmp_path)
    transport = FakeTransport(success_payload())

    result = run_edgefit_session(front, side, 170, 60, transport)

    assert result.status == "OK"
    assert transport.pushed
    assert transport.cleaned
    assert not front.exists()
    assert not side.exists()


def test_session_can_keep_local_captures_for_controlled_review(tmp_path: Path):
    front, side = write_pair(tmp_path)
    transport = FakeTransport(success_payload())

    run_edgefit_session(front, side, 170, 60, transport, cleanup_local=False)

    assert transport.cleaned
    assert front.exists()
    assert side.exists()


def test_session_rejects_nonpositive_metadata(tmp_path: Path):
    front, side = write_pair(tmp_path)
    transport = FakeTransport(success_payload())
    with pytest.raises(ValueError, match="positive"):
        run_edgefit_session(front, side, 0, 60, transport)


def test_session_rejects_captures_from_different_directories(tmp_path: Path):
    first = tmp_path / "a"
    second = tmp_path / "b"
    first.mkdir()
    second.mkdir()
    front = first / "front.jpg"
    side = second / "side.jpg"
    front.write_bytes(b"front")
    side.write_bytes(b"side")
    transport = FakeTransport(success_payload())
    with pytest.raises(ValueError, match="same session directory"):
        run_edgefit_session(front, side, 170, 60, transport)


def test_session_cleans_up_when_result_contract_is_invalid(tmp_path: Path):
    front, side = write_pair(tmp_path)
    transport = FakeTransport({"status": "OK", "measurements_cm": None})

    with pytest.raises(ValueError):
        run_edgefit_session(front, side, 170, 60, transport)

    assert transport.cleaned
    assert not front.exists()
    assert not side.exists()
