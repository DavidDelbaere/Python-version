# Executed validation

Date: 2026-11-02. Host: this Linux device, system Python 3.12.3.

- **PASS — 11 automated checks**, via
  `python3 -m unittest discover -s Testing/Part_Playground -v`.
  Covers analytical mass/volume/inertia, dimension-driven mass updates, explicit
  mass and custom metadata, invalid/unsupported input, duplicate JSON keys,
  free fall compared to the analytic solution, impact restitution/friction,
  nonpenetration and settling over 10 seconds, deterministic reset, static
  bodies, frictionless motion, file-driven appearance, moving geometry and
  parseable SVG containing six faces.
- **PASS — headless rendering**, via
  `python3 Testing/Part_Playground/viewer.py --render Testing/Part_Playground/preview.svg`.
  The generated artifact is included. Subsequent checks also rendered the falling
  and settled states to `/tmp` and launched from a different working directory.
- **PASS — real desktop GUI**, via
  `python3 Testing/Part_Playground/viewer.py --smoke-test` outside the sandbox
  with display access approved. Output:
  `GUI smoke test passed: 40 frames, 222 physics steps, 41 canvas primitives`.
  The window opened, advanced simulation, drew frames and closed itself normally.
- **PASS — visual inspection** of the shared render commands rasterized with
  the host's Pillow installation for inspection only. The cyan box is solid,
  shaded, in perspective above the grid, with visible edges and a release marker.
  Pillow is not used by the application or its automated tests.

The initial sandbox-only GUI attempt failed because the sandbox cannot connect
to DISPLAY=:0. That restriction was bypassed only through an approved desktop
test. Headless rendering works inside the sandbox.

Limits: this is not a production-loader integration test or a general rigid-body
engine validation. File chooser/save dialogs and drag/wheel controls were not
manually exercised. The automated GUI check verifies frame drawing and physics
advancement, not every user interaction. See README.md for solver scope.
