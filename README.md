# FITMAP EdgeFit

**Local-first Edge AI for explainable fashion fit on Arduino UNO Q**

FITMAP EdgeFit is an Edge AI sizing demonstrator developed for **Qualcomm Hack The Challenge 2026**. It combines guided front-and-side RGB capture with on-device inference on a physical **Arduino UNO Q 2GB** to produce body measurements, body-shape information, garment size recommendations, and region-level fit insights.

The project is designed around a simple idea: move the most sensitive part of the sizing workflow closer to the user, keep the interaction understandable, and return results in a structured form that can be explained by the application layer.

> **EdgeFit is a research and competition prototype.** It is not a medical device or certified measurement instrument.

## Highlights

* **Arduino UNO Q inference** on the validated competition path.
* **Guided dual-view capture** using front and side RGB images.
* Estimation of **chest/bust, waist, and hip** measurements.
* **Body-shape classification**.
* **Garment size recommendation**.
* **Regional fit interpretation** for chest, waist, and hip.
* Structured success and failure responses for predictable integration.
* Local session cleanup for temporary raw captures.
* Physical host ↔ UNO Q parity validation on deterministic reference cases.

---

## 1. Overview

Traditional online sizing often reduces fit to a static chart and a single size label. EdgeFit explores a richer workflow:

```text
capture → infer → recommend → explain
```

A typical session follows this sequence:

1. Enter height and weight.
2. Start a guided scan with the Rapoo C280.
3. Capture a fresh front view.
4. Turn 90° and capture a fresh side view.
5. Transfer the capture pair locally to the Arduino UNO Q.
6. Run the EdgeFit inference path on the board.
7. Return chest/bust, waist, hip, and body-shape information.
8. Generate a garment size recommendation and region-level fit result.
9. Present the structured output in the host application.
10. End the session and remove temporary capture files from the active session paths.

This separation keeps the hardware path clear: the laptop handles capture and presentation, while the UNO Q serves as the EdgeFit execution target.

---

## 2. System Architecture

```text
Rapoo C280
    │
    │ guided front + side capture
    ▼
┌──────────────────────────────┐
│        Windows host          │
│  capture + orchestration     │
└──────────────┬───────────────┘
               │ local USB / ADB
               ▼
┌──────────────────────────────┐
│     Arduino UNO Q 2GB        │
│                              │
│      EdgeFit runtime         │
│    ├─ body measurements      │
│    ├─ body shape             │
│    ├─ size recommendation    │
│    └─ regional fit result    │
└──────────────┬───────────────┘
               │ structured JSON
               ▼
┌──────────────────────────────┐
│    Host presentation layer   │
│  explainable result display  │
└──────────────────────────────┘
```

The demonstrated measurement-and-fit path does **not require a cloud inference round-trip**. The repository focuses on the validated competition integration, interfaces, and engineering evidence; trained model assets and product-specific implementation details are outside the scope of this release.

---

## 3. What EdgeFit Produces

For a successful session, EdgeFit returns four groups of information:

### Body measurements

* Chest / bust
* Waist
* Hip

### Body shape

A structured body-shape label used by the presentation layer.

### Recommended size

A garment size recommendation derived from the completed inference result.

### Regional fit

Fit is evaluated separately across key body regions rather than reduced to one global label.

| Region | Example interpretation          |
| ------ | ------------------------------- |
| Chest  | tighter / balanced / looser fit |
| Waist  | tighter / balanced / looser fit |
| Hip    | tighter / balanced / looser fit |

This allows the UI to explain **where** a garment is expected to fit differently, not only **which size** was selected.

---

## 4. Hardware & Software

### Validated hardware

| Component             | Role                                   | Validated configuration          |
| --------------------- | -------------------------------------- | -------------------------------- |
| **Arduino UNO Q 2GB** | EdgeFit execution target               | Direct USB connection to host    |
| **Rapoo C280**        | Guided RGB capture                     | 1280 × 720 observed capture path |
| **Windows laptop**    | Capture orchestration and presentation | Local host ↔ UNO Q control       |

### Host-side software

* Python 3.10+
* OpenCV
* NumPy
* ADB available on the host for UNO Q transport

The competition runtime used a PyTorch-based inference environment on the UNO Q.

---

## 5. Repository Structure

```text
FITMAP-EdgeFit/
├── README.md
├── LICENSE
├── NOTICE.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
│
├── src/
│   └── edgefit_demo/
│       ├── contracts.py
│       ├── session.py
│       ├── session_cleanup.py
│       └── unoq_transport.py
│
├── scripts/
│   ├── capture_pair.py
│   ├── run_edgefit_session.py
│   └── run_public_demo.py
│
├── examples/
│   ├── sample_input.json
│   └── sample_output.json
│
├── specs/
│   └── edgefit_result.schema.json
│
├── evidence/
│   ├── VALIDATION.md
│   ├── validation_summary.json
│   ├── host_test_summary.txt
│   ├── unoq_parity_summary.txt
│   └── hardware_freeze_summary.txt
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── UNO_Q_DEPLOYMENT.md
│   └── PUBLIC_RELEASE_SCOPE.md
│
└── tests/
    ├── test_cleanup.py
    ├── test_contracts.py
    ├── test_examples.py
    ├── test_session.py
    └── test_transport.py
```

The repository is intentionally organized around four things: **capture, transport, contracts, and validation**.

---

## 6. Input & Result Contract

### Input

A session uses:

```json
{
  "front_view": "front.jpg",
  "side_view": "side.jpg",
  "height_cm": 170.0,
  "weight_kg": 60.0
}
```

Both views are required. The host flow verifies that the capture files are present, readable, non-empty, and fresh before the inference handoff.

### Result

A successful response follows a structured contract such as:

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

The schema is available at `specs/edgefit_result.schema.json`.

### Failure behavior

Missing views, unreadable captures, transport failures, and runtime errors are represented as explicit failure states. EdgeFit does not substitute failed inference with fabricated measurements.

---

## 7. Runtime Flow & Privacy

```text
START SESSION
    ↓
Guided front capture
    ↓
Guided side capture
    ↓
Fresh-image validation
    ↓
Local transfer to Arduino UNO Q
    ↓
EdgeFit inference + fit result
    ↓
Structured result returned to host
    ↓
END SESSION
    ↓
Temporary front/side captures removed
from active host and UNO Q session paths
```

The demonstrated flow keeps raw front and side images out of the structured result payload and does not require a cloud inference service. At the end of a session, temporary captures are removed from the active host and UNO Q working paths.

This is application-level file cleanup rather than forensic secure erase.

---

## 8. Getting Started

### 8.1 Create an environment

```bash
python -m venv .venv
```

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 8.2 Run the structured-result demo

```bash
python scripts/run_public_demo.py examples/sample_output.json
```

### 8.3 Run the test suite

```bash
pip install -r requirements-dev.txt
pytest -q
```

### 8.4 Run guided dual-view capture

```bash
python scripts/capture_pair.py 1 captures
```

Camera index `1` was used in the validated competition setup; the correct index may differ by machine.

### 8.5 Review the UNO Q integration path

The host-to-board transport boundary is implemented in:

```text
src/edgefit_demo/unoq_transport.py
```

The end-to-end session orchestration is represented in:

```text
scripts/run_edgefit_session.py
```

Additional deployment notes are available in `docs/UNO_Q_DEPLOYMENT.md`.

---

## 9. Validation

EdgeFit was validated at both the reference-host level and on the physical Arduino UNO Q deployment path.

### Reference baseline

* Complete v1.0.1 host suite: **32 tests passed**.
* Original regression suite after the patch: **24 tests passed**.
* Training-oracle preprocessing parity: **126 / 126 exact comparisons**.
* Runtime preprocessing parity: **126 / 126 exact comparisons**.
* Runtime silhouette parity: **126 / 126 exact comparisons**.

### Physical host ↔ Arduino UNO Q parity

A deterministic 10-case run compared reference-host execution with the deployed UNO Q path:

| Metric                              |                  Result |
| ----------------------------------- | ----------------------: |
| Cases executed                      |                      10 |
| Measurements compared               |                      30 |
| Semantic agreement                  |                 10 / 10 |
| Provenance agreement                |                 10 / 10 |
| Maximum absolute numeric difference | 1.52587890625 × 10⁻⁵ cm |
| Mean absolute numeric difference    | 4.06901041667 × 10⁻⁶ cm |
| Maximum float32 ULP distance        |                       2 |

These results demonstrate **deployment parity** between the tested host and UNO Q paths. They are not presented as real-world body-measurement accuracy figures.

### End-to-end hardware flow

The final competition validation recorded successful execution of:

* Rapoo C280 preflight;
* guided front capture;
* guided side capture;
* automatic capture → UNO Q handoff;
* physical UNO Q inference;
* structured result bridge;
* size recommendation output;
* regional fit output;
* session cleanup;
* cold-start live rehearsal.

More detail is available in `evidence/VALIDATION.md` and `evidence/validation_summary.json`.

---

## 10. Design Principles

### Edge-first execution

The critical measurement-and-fit path runs on the Arduino UNO Q rather than depending on remote inference.

### Explainable output

The application receives structured measurements, shape, size, and region-level fit information instead of an opaque single prediction.

### Predictable integration

Inputs, outputs, and failure states are explicit and machine-readable, making the EdgeFit runtime easier to integrate with a host UI.

### Privacy-aware sessions

Temporary raw captures are treated as session data and removed from active working paths when the session ends.

### Evidence over claims

Deployment parity, hardware execution, and integration behavior are documented separately from real-world accuracy claims.

---

## 11. Current Scope

EdgeFit is a competition-grade prototype, so several areas remain outside the current validation scope:

* population-scale measurement accuracy across diverse bodies and capture conditions;
* latency, power, thermal, and long-duration reliability benchmarking on UNO Q;
* fully self-contained camera-on-board operation;
* production retailer integration and catalog-scale deployment;
* certified or medical-grade body measurement.

The current repository is centered on the validated Edge AI workflow, hardware integration, data contract, and reproducible engineering checks around the competition build.

---

## 12. License

FITMAP-specific materials in this repository are provided under the terms in `LICENSE`.

Third-party software remains subject to its respective licenses. Arduino and Arduino UNO Q are referenced as the hardware platform used for the demonstrated deployment.

---

**FITMAP EdgeFit** — two guided views, local Edge AI, and a fit result designed to be understood.
