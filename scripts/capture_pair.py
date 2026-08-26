from __future__ import annotations

from collections import deque
from pathlib import Path
import sys
import time

import cv2
import numpy as np


FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
ROI_LEFT = 0.20
ROI_RIGHT = 0.80
MIN_HEIGHT = 0.40
MAX_CENTER_OFFSET = 0.18
STABILITY_FRAMES = 8
MAX_CENTER_JITTER = 0.045
MAX_SIZE_JITTER = 0.060
COUNTDOWN_SECONDS = 3
SIDE_WIDTH_RATIO = 0.93
SIDE_FALLBACK_SECONDS = 8.0


def centered_text(frame, text, y, scale=0.7, thickness=2):
    size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    x = max(20, (frame.shape[1] - size[0]) // 2)
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


def foreground_bbox(frame, background_gray):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    diff = cv2.absdiff(gray, background_gray)
    _, mask = cv2.threshold(diff, 22, 255, cv2.THRESH_BINARY)

    h, w = mask.shape
    roi = np.zeros_like(mask)
    roi[:, int(w * ROI_LEFT) : int(w * ROI_RIGHT)] = 255
    mask = cv2.bitwise_and(mask, roi)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        np.ones((17, 17), np.uint8),
        iterations=3,
    )
    mask = cv2.dilate(mask, np.ones((9, 9), np.uint8), iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame_area = frame.shape[0] * frame.shape[1]
    useful = [c for c in contours if cv2.contourArea(c) >= frame_area * 0.002]
    if not useful:
        return None

    x, y, bw, bh = cv2.boundingRect(np.vstack(useful))
    if bh < frame.shape[0] * 0.20:
        return None
    return x, y, bw, bh


def alignment_status(bbox, frame_width, frame_height):
    if bbox is None:
        return False, "STEP INTO THE FRAME"

    x, y, width, height = bbox
    if height / frame_height < MIN_HEIGHT:
        return False, "MOVE A LITTLE CLOSER"

    center_x = x + width / 2
    center_y = y + height / 2
    if abs(center_x - frame_width / 2) / frame_width > MAX_CENTER_OFFSET:
        return False, "MOVE TO THE CENTER"
    if abs(center_y - frame_height / 2) / frame_height > MAX_CENTER_OFFSET:
        return False, "CENTER YOUR FULL BODY"
    return True, "GOOD - HOLD STILL"


def normalized_bbox(bbox, frame_width, frame_height):
    x, y, width, height = bbox
    return (
        (x + width / 2) / frame_width,
        (y + height / 2) / frame_height,
        width / frame_width,
        height / frame_height,
    )


def is_stable(history):
    if len(history) < STABILITY_FRAMES:
        return False
    values = np.asarray(history, dtype=np.float32)
    return (
        np.ptp(values[:, 0]) <= MAX_CENTER_JITTER
        and np.ptp(values[:, 1]) <= MAX_CENTER_JITTER
        and np.ptp(values[:, 2]) <= MAX_SIZE_JITTER
        and np.ptp(values[:, 3]) <= MAX_SIZE_JITTER
    )


def calibrate_background(cap):
    samples = []
    started = time.time()
    while time.time() - started < 2.5:
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        display = frame.copy()
        centered_text(display, "KEEP CAPTURE AREA EMPTY", 70, 0.9)
        cv2.imshow("FITMAP EdgeFit - Guided Capture", display)
        if cv2.waitKey(1) & 0xFF == 27:
            raise KeyboardInterrupt

    for _ in range(35):
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        samples.append(cv2.GaussianBlur(gray, (7, 7), 0))

    if len(samples) < 15:
        raise RuntimeError("Background calibration failed")
    return np.median(np.stack(samples), axis=0).astype(np.uint8)


def capture(camera_index: int, output_dir: Path):
    backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
    cap = cv2.VideoCapture(camera_index, backend)
    if not cap.isOpened():
        raise RuntimeError(f"Camera open failed: index={camera_index}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    output_dir.mkdir(parents=True, exist_ok=True)

    for _ in range(20):
        cap.read()
        time.sleep(0.03)

    try:
        background = calibrate_background(cap)
        stage = "FRONT"
        history = deque(maxlen=STABILITY_FRAMES)
        countdown_start = None
        front_width = None
        side_started = None

        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                raise RuntimeError("Camera read failed")

            frame_h, frame_w = frame.shape[:2]
            bbox = foreground_bbox(frame, background)
            aligned, status = alignment_status(bbox, frame_w, frame_h)

            if aligned and bbox is not None:
                history.append(normalized_bbox(bbox, frame_w, frame_h))
            else:
                history.clear()

            stable = aligned and is_stable(history)
            display = frame.copy()
            centered_text(display, f"{stage} CAPTURE", 55, 0.95, 3)
            centered_text(display, status, 105, 0.68, 2)

            if bbox is not None:
                x, y, width, height = bbox
                cv2.rectangle(display, (x, y), (x + width, y + height), (255, 255, 255), 2)

            ready = stable
            if stage == "SIDE" and ready and bbox is not None and front_width is not None:
                elapsed = time.time() - float(side_started)
                narrower = bbox[2] <= front_width * SIDE_WIDTH_RATIO
                ready = narrower or elapsed >= SIDE_FALLBACK_SECONDS

            if ready:
                if countdown_start is None:
                    countdown_start = time.time()
                elapsed = time.time() - countdown_start
                remaining = COUNTDOWN_SECONDS - int(elapsed)
                if remaining > 0:
                    centered_text(display, str(remaining), frame_h // 2, 4.0, 7)
                else:
                    target = output_dir / f"{stage.lower()}.jpg"
                    if not cv2.imwrite(str(target), frame):
                        raise RuntimeError(f"Could not write {target.name}")
                    print(f"CAPTURE_{stage}_PASS {target}")

                    if stage == "FRONT":
                        assert bbox is not None
                        front_width = bbox[2]
                        stage = "SIDE"
                        side_started = time.time()
                        history.clear()
                        countdown_start = None
                    else:
                        print("AUTO_CAPTURE_PAIR_PASS")
                        return
            else:
                countdown_start = None

            cv2.imshow("FITMAP EdgeFit - Guided Capture", display)
            if cv2.waitKey(1) & 0xFF == 27:
                raise KeyboardInterrupt
    finally:
        cap.release()
        cv2.destroyAllWindows()


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python scripts/capture_pair.py CAMERA_INDEX OUTPUT_DIR")
        return 2
    try:
        capture(int(sys.argv[1]), Path(sys.argv[2]))
    except KeyboardInterrupt:
        print("CAPTURE_CANCELLED")
        return 130
    except Exception as exc:
        print(f"CAPTURE_ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
