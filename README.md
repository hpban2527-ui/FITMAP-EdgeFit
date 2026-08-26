# FITMAP EdgeFit

**Local-first Edge AI for explainable fashion fit on Arduino UNO Q**

FITMAP EdgeFit is the competition Edge AI demonstrator built for **Qualcomm Hack The Challenge 2026**. A guided front-and-side RGB capture is transferred over a local USB/ADB link to a physical **Arduino UNO Q 2GB**, where the frozen EdgeFit runtime produces body measurements and fit-oriented outputs for the presentation layer.

This repository is a **public technical showcase**, not a full commercial source release. It documents the validated hardware path, public integration boundary, result contract, privacy behavior, and selected validation evidence while intentionally excluding FITMAP's model weights, training assets, calibration details, sizing internals, retailer data, and commercial product code.

> EdgeFit is a research and competition demonstrator. It is not a medical device, a certified measurement instrument, or a production retail service.

## Table of Contents

- [1. Overview](#1-overview)
- [2. System Architecture](#2-system-architecture)
- [3. Repository Layout](#3-repository-layout)
- [4. Hardware & Software](#4-hardware--software)
- [5. Public Interfaces](#5-public-interfaces)
- [6. Runtime Flow & Privacy](#6-runtime-flow--privacy)
- [7. Getting Started](#7-getting-started)
- [8. Demo Output](#8-demo-output)
- [9. Validation Evidence](#9-validation-evidence)
- [10. Known Gaps](#10-known-gaps)
- [11. License & Public-Release Boundary](#11-license--public-release-boundary)

---

## 1. Overview

Online apparel sizing often relies on static charts and user guesswork. EdgeFit explores a different interaction:

**capture → infer → recommend → explain**

The frozen competition flow is:

1. Enter height and weight.
2. Start a guided live scan with the Rapoo C280.
3. Capture a fresh front view.
4. Turn 90° and capture a fresh side view.
5. Transfer the pair locally to the Arduino UNO Q.
6. Run the frozen EdgeFit inference path on the UNO Q.
7. Return chest/bust, waist, hip, and body-shape information.
8. Produce a recommended garment size and region-level fit interpretation.
9. Return a structured result to the host presentation layer.
10. End the session and remove temporary raw captures from the active host and UNO Q session paths.

### Demonstrated capabilities

- Physical Edge AI execution on **Arduino UNO Q 2GB**.
- Guided **front + side** RGB acquisition with a Rapoo C280.
- Chest/bust, waist, and hip estimation.
- Body-shape classification.
- Garment size recommendation.
- Region-level fit output for chest, waist, and hip.
- Structured failure states instead of fabricated measurements.
- Local-session cleanup of temporary raw captures.
- Deterministic host-to-board deployment parity validation.

---

## 2. System Architecture

```text
Rapoo C280
    |
    | guided front + side capture
    v
+------------------------------+
|        Windows host          |
|  capture + orchestration     |
+--------------+---------------+
               | local USB / ADB
               v
+------------------------------+
|     Arduino UNO Q 2GB        |
|                              |
|  frozen EdgeFit runtime      |
|    + body measurements       |
|    + body shape              |
|    + size recommendation     |
|    + regional fit result     |
+--------------+---------------+
               | structured JSON
               v
+------------------------------+
|    Host presentation layer   |
|  explainable result display  |
+------------------------------+
```

The C280 is host-connected in the validated topology. The host handles guided capture and local transport; the inference-and-fit path executes on the UNO Q and returns structured data. No cloud round-trip is required for the demonstrated measurement-and-fit path.

The public repository exposes the code around this hardware boundary while keeping the proprietary EdgeFit runtime private.

---

## 3. Repository Layout

```text
FITMAP-EdgeFit/
├── README.md
├── LICENSE
├── NOTICE.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── docs/
│   ├── ARCHITECTURE.md
│   ├── UNO_Q_DEPLOYMENT.md
│   └── PUBLIC_RELEASE_SCOPE.md
├── evidence/
│   ├── VALIDATION.md
│   ├── validation_summary.json
│   ├── host_test_summary.txt
│   ├── unoq_parity_summary.txt
│   └── hardware_freeze_summary.txt
├── examples/
│   ├── sample_input.json
│   └── sample_output.json
├── scripts/
│   ├── capture_pair.py
│   ├── run_edgefit_session.py
│   └── run_public_demo.py
├── specs/
│   └── edgefit_result.schema.json
├── src/edgefit_demo/
│   ├── contracts.py
│   ├── session.py
│   ├── session_cleanup.py
│   └── unoq_transport.py
└── tests/
    ├── test_cleanup.py
    ├── test_contracts.py
    ├── test_examples.py
    ├── test_session.py
    └── test_transport.py
```

The repository includes meaningful capture, orchestration, transport, contract, cleanup, and test code. It deliberately stops at the boundary of the commercial inference engine.

No personal photographs, raw body captures, demo videos, trained model weights, or retailer-private assets are included.

---

## 4. Hardware & Software

### Validated competition hardware

| Component | Role | Validated configuration |
|---|---|---|
| Arduino UNO Q 2GB | EdgeFit execution target | Physical aarch64 board, local USB/ADB path |
| Rapoo C280 | Guided RGB capture | 1280 × 720 host capture path |
| Windows laptop | Capture orchestration and presentation | Local host ↔ UNO Q control |

### Frozen UNO Q runtime evidence

The final physical build recorded:

- Python `3.13.5`;
- PyTorch `2.11.0+cpu`;
- NumPy `2.5.1`;
- OpenCV `4.13.0`;
- Pillow `12.3.0`.

### Public host-side stack

- Python 3.10+
- OpenCV
- NumPy
- ADB available on the host for UNO Q transport

The public host utilities do not ship or install the proprietary EdgeFit model runtime.

---

## 5. Public Interfaces

### 5.1 Input boundary

```json
{
  "front_view": "front.jpg",
  "side_view": "side.jpg",
  "height_cm": 170.0,
  "weight_kg": 60.0
}
```

Both views are required. The guided host flow validates readable, non-empty session captures before handoff.

### 5.2 Result boundary

```json
{
  "status": "OK",
  "measurements_cm": {
    "bust": 91.4,
    "waist": 75.7,
    "hip": 97.4
  },
  "shape": "Pear",
  "recommended_size": "M",
  "regional_fit": {
    "chest": "Loose",
    "waist": "Loose",
    "hip": "Loose"
  },
  "execution_target": "Arduino UNO Q"
}
```

The example is sanitized and rounded. It demonstrates the public result contract; it is not presented as a population-level accuracy result.

The JSON Schema is available at `specs/edgefit_result.schema.json`.

### 5.3 Failure boundary

The public contract preserves explicit non-success states for missing/invalid captures, transport failures, and runtime failures. A failed result cannot carry fabricated body measurements; the public tests enforce this behavior.

---

## 6. Runtime Flow & Privacy

```text
START SESSION
    |
    v
Guided front capture
    |
    v
Guided side capture
    |
    v
Fresh capture validation
    |
    v
Local transfer to Arduino UNO Q
    |
    v
EdgeFit inference + fit result
    |
    v
Structured result returned to host
    |
    v
END SESSION
    |
    v
Temporary front/side captures removed
from active host and UNO Q session paths
```

### Privacy boundary

- The demonstrated EdgeFit path does not require a cloud inference service.
- Raw front and side images are not part of the structured result payload.
- Temporary front/side session files are removed from the active host and UNO Q capture paths at session end.
- The public session orchestrator keeps cleanup enabled by default.
- This is application-level file deletion; no claim of forensic secure erase is made.

---

## 7. Getting Started

### 7.1 Create a public-review environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 7.2 Run the hardware-independent result demo

```bash
python scripts/run_public_demo.py examples/sample_output.json
```

### 7.3 Run the public test suite

```bash
pytest -q
```

The public release currently contains **22 lightweight tests** covering result semantics, failure behavior, session cleanup, orchestration, transport guards, and example/schema structure. They are intentionally separate from the internal **32-test frozen baseline suite** cited in the validation evidence.

### 7.4 Guided camera capture

```bash
python scripts/capture_pair.py 0 session
```

The script guides front and side acquisition and writes `session/front.jpg` and `session/side.jpg`.

### 7.5 Authorized physical UNO Q integration

`scripts/run_edgefit_session.py` connects the public capture/transport/result/cleanup path. The private on-board runtime command is intentionally not included in this repository. Authorized reviewers can configure it through `EDGEFIT_REMOTE_COMMAND` and then run:

```bash
python scripts/run_edgefit_session.py   --front session/front.jpg   --side session/side.jpg   --height-cm 170   --weight-kg 60
```

See `docs/UNO_Q_DEPLOYMENT.md` for the exact public boundary and frozen-board environment.

---

## 8. Demo Output

Representative public output:

```text
Status: OK
Execution target: Arduino UNO Q
Bust / chest: 91.4 cm
Waist: 75.7 cm
Hip: 97.4 cm
Body shape: Pear
Recommended size: M
Regional fit: Chest: Loose | Waist: Loose | Hip: Loose
```

This repository intentionally contains no image or video assets.

---

## 9. Validation Evidence

### Internal host baseline

The frozen v1.0.1 internal suite recorded:

- **32 passed in 11.62 s** for the complete suite;
- **24 passed in 10.90 s** for the original regression suite after the patch;
- deterministic preprocessing/silhouette parity checks recorded exact agreement across the reference comparisons.

### Physical Arduino UNO Q parity

A deterministic **10-case physical parity run** compared the host reference path with the deployed UNO Q path:

| Metric | Result |
|---|---:|
| Cases executed | 10 |
| Measurements compared | 30 |
| Semantic agreement | **10 / 10** |
| Provenance agreement | **10 / 10** |
| Maximum absolute numeric difference | **1.52587890625 × 10⁻⁵ cm** |
| Mean absolute numeric difference | **4.06901041667 × 10⁻⁶ cm** |
| Maximum float32 ULP distance | **2** |

This is **deployment parity evidence**, not a claim of real-world human measurement accuracy.

### Final physical freeze

Sanitized freeze evidence records PASS for:

- aarch64 UNO Q runtime;
- UNO Q ADB connectivity;
- frozen UNO Q runtime preflight;
- Rapoo C280 preflight;
- Python compile/local-file preflight;
- fresh camera-first presentation flow;
- final live launcher.

Reviewable sanitized extracts are in `evidence/`.

---

## 10. Known Gaps

- EdgeFit is a **research / competition prototype**, not a production sizing-certification system.
- Current public evidence establishes software/deployment parity and physical end-to-end execution, not broad real-world accuracy across all body types, clothing conditions, poses, lighting environments, or cameras.
- The validated topology uses a **host-connected USB camera** and local host-to-UNO-Q handoff; it is not presented as a fully self-contained camera-on-board consumer device.
- Session cleanup is application-level deletion; no forensic secure-erase claim is made.
- A public clone cannot reproduce proprietary inference because trained weights, model code, calibration, sizing internals, and commercial fit rules are intentionally excluded.

---

## 11. License & Public-Release Boundary

FITMAP-specific materials in this repository are provided for competition judging, technical review, educational inspection, and other non-commercial evaluation under the accompanying `LICENSE`.

Intentionally excluded from the public release:

- trained model weights / checkpoints;
- model architecture and inference-core implementation;
- training datasets and training pipeline;
- private preprocessing/calibration details;
- anthropometric estimation formulas;
- proprietary size-selection thresholds and logic;
- proprietary regional-fit internals;
- retailer/private garment data and production adapters;
- the broader commercial FITMAP application;
- personal photos, raw body captures, and demo videos.

Third-party libraries, platforms, and trademarks remain subject to their respective owners and licenses.

---

**FITMAP EdgeFit — from two guided views to explainable fashion fit, with the critical inference path running at the edge.**
