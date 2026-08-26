# Public Release Scope

This repository is a reviewable technical subset of FITMAP EdgeFit created for competition sharing. The objective is to show the real system boundary and engineering evidence without publishing the commercial implementation.

## Included

- guided front/side capture utility;
- host-to-Arduino UNO Q transport boundary;
- end-to-end public orchestration layer around the private runtime;
- structured input/output contracts;
- local-session cleanup behavior;
- public unit tests;
- sanitized validation evidence;
- architecture and deployment notes.

## Intentionally excluded

- trained checkpoints or model weights;
- model architecture implementation;
- training data or training pipeline;
- preprocessing and calibration internals;
- anthropometric estimation formulas;
- proprietary sizing rules and thresholds;
- regional-fit decision internals;
- retailer/private garment datasets and production adapters;
- full FITMAP commercial application code;
- personal photos, raw body captures, and demo videos.

A clone of this repository can review and test the public interfaces, but it cannot reconstruct or reproduce the proprietary EdgeFit inference engine.
