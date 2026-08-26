# Architecture Notes

## Competition topology

```text
Rapoo C280 -> Windows host -> local USB/ADB -> Arduino UNO Q 2GB
                                             |
                                             v
                                      EdgeFit runtime
                                             |
                                             v
                                      structured JSON
                                             |
                                             v
                                      host presentation
```

The camera is host-connected in the validated build. The host controls guided capture and local transport; the physical UNO Q executes the frozen inference-and-fit path.

## Public code path

```text
capture_pair.py
      |
      v
run_edgefit_session.py
      |
      v
UnoQTransport.push_capture_pair()
      |
      v
[ proprietary on-board EdgeFit runtime ]
      |
      v
EdgeFitResult.from_mapping()
      |
      v
session cleanup
```

The bracketed runtime boundary is deliberately absent from the public release. The surrounding capture, transport, result validation, and cleanup layers remain reviewable.

## Separation of concerns

- `contracts.py` defines the stable product-facing result boundary.
- `unoq_transport.py` owns local ADB transport and remote temporary-capture lifecycle.
- `session.py` connects capture files, metadata, the UNO Q boundary, validation, and cleanup.
- `capture_pair.py` demonstrates the guided two-view acquisition used by the host flow.

For the physical environment and reviewer commands, see `UNO_Q_DEPLOYMENT.md`.
