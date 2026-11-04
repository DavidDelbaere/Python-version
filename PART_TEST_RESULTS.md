# Independent tests of the new JSON SimuO part prototype

Date: 2026-11-02. Tested `experiments/physics_parts`; application implementation files were not changed by this testing task. Work is concurrent, so results identify the tested snapshot. `part.py` SHA-256: `19fb0d7f782706b610b2c1c5af650cfceb9b3b4e71c854079148b1db37a86196`.

## Findings for the implementing agent

1. **Medium — accepted numeric inputs can crash the renderer.** Starting from `aluminum_cube.simuOPart`, set `initial_state.position` to `[1e16, 1.1, 0]`. `load_part()` succeeds, but `scene(part, Simulation(part), Camera(part))` raises `ZeroDivisionError` in `render.unit()`: floating-point cancellation collapses world-space geometry/camera vectors. Another reproducer: set box dimensions to `[1e-100, 1e-100, 1e-100]`, `physics.mass_source` to `explicit`, and `physics.mass` to `1`. The loader accepts positive finite inertia, but face-normal normalization underflows and divides by zero. The viewer catches ValueError/OSError/OverflowError, so ZeroDivisionError escapes headless execution and stops the GUI frame callback. Consider documented numerical limits/validation and robust normalization/local coordinates. These are extreme-scale robustness issues; the supplied sample renders correctly.
2. **Low — validation exception type is inconsistent for extreme numbers.** `material.density = 10**400` raises `OverflowError` from `math.isfinite()` in `part.number()`; dimensions `[1e200, 1, 1e-200]` raise `OverflowError` while squaring dimensions for inertia. Tests expecting the loader's usual ValueError fail. The viewer already catches OverflowError, so this is not an ordinary GUI crash. Normalize validation errors or document the loader's exception contract.
3. **Integration limit, expected by design:** production `src/renderer.py` still parses `.simuOPart` as OBJ. The new JSON sample belongs to the independent viewer and is not ready for import into the production editor. This matches FORMAT.md/COORDINATION.md; it is not a regression introduced by this prototype.

## Passing checks

- Author's suite: `python3 -m unittest discover -s experiments/physics_parts -v` — all 11 tests pass.
- Independent loader/physics suite: 14 test methods, 12 pass and the two extreme-number validation methods error as described above. Invalid-field coverage includes 27 mutations, required-field omissions, unexpected fields, forbidden mass-source combinations, duplicate JSON keys, NaN/Infinity, and static velocity.
- Sample: volume 0.008 m³, mass 21.6 kg, diagonal inertia 0.144 kg·m²; eight distinct vertices with the specified dimensions.
- Explicit-mass rectangular box: expected mass, volume, and independent inertia values.
- Gravity/free fall matches the semi-implicit Euler discrete solution. No horizontal drag in flight. Equal trajectories for different masses.
- Restitution and Coulomb friction match independently calculated one-step impulses.
- 24,000 steps (100 simulated seconds): finite state, no floor penetration, rest reached. Zero friction preserves horizontal speed. Static body remains stationary. Reset/replay is deterministic.
- CLI renders at t=0 and t=10 s. Both SVGs parse as XML and contain six cube faces. Unicode and XML-sensitive names roundtrip correctly.
- Initial SVG was rasterized and visually inspected: visible shaded cube, floor grid, height reference, and correct metadata.
- Desktop built-in smoke test: 40 frames, 234 physics steps, 41 canvas primitives, exit 0.
- Independent desktop interaction checks: six initial cube faces; paused t=0; single-step advances 1/240 s; orbit changes projection; Play advances physics; Pause invoked; SVG export writes a file; invalid Open shows an error and preserves the current part; valid Open updates the name/mass and resets/pauses simulation. No Tk callback errors observed. Final clean rerun recorded below.

## Reproduction artifacts

- `/tmp/simuo_part_qa.py` — independent loader/physics tests.
- `/tmp/simuo_part_gui_qa.py` — desktop interaction harness; invokes actual Tk buttons and mocks file-dialog selections only.
- `/tmp/simuo-part-initial.svg`, `/tmp/simuo-part-settled.svg`, `/tmp/simuo-part-initial.png`, `/tmp/simuo-part-gui-export.svg`.

The desktop sandbox cannot access DISPLAY=:0. Desktop checks were explicitly approved and run outside that sandbox. The first interaction harness run had an incorrect expected check-count assertion (seven versus six); the six actual application checks passed. That harness assertion was corrected before the final rerun.

Final desktop interaction rerun: `python3 /tmp/simuo_part_gui_qa.py` exited 0 with all six checks passing and no callback exceptions.
