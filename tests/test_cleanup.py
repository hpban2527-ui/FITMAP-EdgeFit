from pathlib import Path

from edgefit_demo.session_cleanup import cleanup_local_captures, cleanup_session


class CleanupTransport:
    def __init__(self):
        self.called = False

    def cleanup_remote_captures(self):
        self.called = True


def test_local_cleanup_removes_only_session_capture_names(tmp_path: Path):
    (tmp_path / "front.jpg").write_bytes(b"front")
    (tmp_path / "side.jpg").write_bytes(b"side")
    (tmp_path / "notes.txt").write_text("keep", encoding="utf-8")

    cleanup_local_captures(tmp_path)

    assert not (tmp_path / "front.jpg").exists()
    assert not (tmp_path / "side.jpg").exists()
    assert (tmp_path / "notes.txt").exists()


def test_session_cleanup_calls_remote_cleanup(tmp_path: Path):
    transport = CleanupTransport()
    cleanup_session(tmp_path, transport)
    assert transport.called
