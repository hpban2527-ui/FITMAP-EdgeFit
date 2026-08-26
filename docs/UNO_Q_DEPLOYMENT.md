# Arduino UNO Q Deployment Notes

## Validated competition topology

```text
Rapoo C280 -> Windows host -> USB / ADB -> Arduino UNO Q 2GB
                                           |
                                           v
                                    frozen EdgeFit runtime
                                           |
                                           v
                                      structured JSON
```

The Rapoo C280 was connected to the host laptop in the frozen build. The host handled guided capture and local transport; the Arduino UNO Q executed the EdgeFit inference-and-fit path.

## Frozen-board environment

The final physical build evidence recorded:

- architecture: `aarch64`;
- Python: `3.13.5`;
- PyTorch: `2.11.0+cpu`;
- NumPy: `2.5.1`;
- OpenCV: `4.13.0`;
- Pillow: `12.3.0`.

These versions describe the validated competition image. They are not a requirement for the lightweight public host utilities.

## Public transport boundary

`src/edgefit_demo/unoq_transport.py` exposes only the host-to-board boundary:

1. verify that ADB can see the board;
2. create temporary capture/result directories;
3. push `front.jpg` and `side.jpg`;
4. invoke an authorized on-board runtime command;
5. read a structured JSON result;
6. remove temporary remote captures.

The public default remote root is `/home/arduino/fitmap_competition`. It is a configurable integration path, not a disclosure of the complete internal deployment layout.

### Host configuration

`EDGEFIT_ADB` may point to a specific ADB executable. `EDGEFIT_REMOTE_ROOT` changes the public session directory. `EDGEFIT_REMOTE_COMMAND` is intentionally left for an authorized private runner and may use these placeholders:

- `{remote_root}`
- `{height_cm}`
- `{weight_kg}`

The trained checkpoint, model implementation, preprocessing/calibration internals, and commercial fit-decision code are not present in this public repository, so a fresh clone is not expected to reproduce proprietary inference.

## Reviewer paths

Hardware-independent contract review:

```bash
python scripts/run_public_demo.py examples/sample_output.json
pytest -q
```

Authorized hardware integration, once the private runtime command is configured:

```bash
python scripts/run_edgefit_session.py   --front session/front.jpg   --side session/side.jpg   --height-cm 170   --weight-kg 60
```

Temporary captures are removed at session end by default. `--keep-local-captures` is available only for controlled development/review; remote temporary captures are still removed.
