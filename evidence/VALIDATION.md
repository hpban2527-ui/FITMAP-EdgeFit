# Validation Summary

This directory contains a public, sanitized view of the frozen competition evidence. It deliberately excludes trained model assets, raw captures, internal reference cases, checkpoint hashes, private retailer data, and proprietary implementation details.

## Evidence files

- `host_test_summary.txt` — sanitized extract of the v1.0.1 host validation results.
- `unoq_parity_summary.txt` — sanitized extract of the 10-case physical host ↔ UNO Q parity run.
- `hardware_freeze_summary.txt` — sanitized extract of the final physical runtime and launcher preflight.
- `validation_summary.json` — machine-readable summary of the same public claims.

## Host baseline

- Complete v1.0.1 host suite: **32 passed in 11.62 s**.
- Original regression suite after the patch: **24 passed in 10.90 s**.
- Training-oracle preprocessing: **126 / 126 exact comparisons**, maximum absolute difference `0`.
- Runtime preprocessing: **126 / 126 exact comparisons**, maximum absolute difference `0`.
- Runtime silhouette comparison: **126 / 126 exact**.

## Physical Arduino UNO Q parity

A deterministic 10-case run compared the host reference path and the deployed UNO Q path.

- Cases executed: **10**.
- Body-measurement values compared: **30**.
- Semantic agreement: **10 / 10**.
- Provenance agreement: **10 / 10**.
- Global maximum absolute difference: **1.52587890625 × 10⁻⁵ cm**.
- Global mean absolute difference: **4.06901041667 × 10⁻⁶ cm**.
- Maximum float32 ULP distance: **2**.

These figures establish deployment parity on the tested reference cases. They do **not** establish real-world body-measurement accuracy.

## Frozen live path

The final competition freeze records PASS for the physical UNO Q runtime, Rapoo C280 preflight, camera-first presentation flow, host-to-board handoff, structured result bridge, and end-session cleanup.

## Stage distinction

The earlier host-baseline report correctly stated that physical hardware had not yet been validated at that stage. Physical UNO Q and C280 evidence was generated later during integration. The public summary keeps those stages separate rather than retroactively changing the earlier result.
