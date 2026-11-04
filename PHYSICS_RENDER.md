# Live physics rendering

Click **Render** on the top menu bar beside **File**, or press **Ctrl+R** in the
main editor. Import a part first. Each invocation opens a separate OpenGL window
with an independent Bullet world and a snapshot of the editor's scene.

Playback starts immediately. Play/Pause, Step, Reset, Frame scene, gravity Y,
and a floor checkbox are available above the viewport. Step pauses and advances
1/240 second. Reset restores the snapshot and pauses; it keeps the chosen
gravity and floor setting. Changing the floor resets playback. Close/reopen
Render to pick up later edits in the main editor. Nothing is written back to
the edited scene or its part files. Closing a render window disconnects its
solver and stops both timers; closing the editor closes its render windows.

## Physical behavior

`src/physics_world.py` uses PyBullet 3.2.7 in DIRECT mode; the existing OpenGL
renderer draws the results. The fixed outer step is 1/240 s, with four internal
substeps and 80 solver iterations. The engine handles full rigid-body motion,
orientation/inertia, gravity, collisions between dynamic/static boxes, contact
with static triangle meshes and a floor, restitution and Coulomb friction.
The implementation follows the [official Bullet API guide](https://github.com/bulletphysics/bullet3/blob/master/docs/pybullet_quickstart_guide/PyBulletQuickstartGuide.md.html).

- JSON v1 boxes use `body_type`, `size`, mass, friction and restitution. Rotation
  is initialized from the current editor transform, using its Rx × Ry × Rz
  degree convention. Engine orientations are converted back to that convention
  for rendering. Linear velocity uses m/s; angular velocity uses **world-space
  rad/s**. Scene acceleration is a constant additional world-space acceleration
  in m/s², added to the configured gravity.
- Positive scene scale resizes visual geometry and collision shapes together.
  Density-derived mass scales with volume; explicit mass stays constant.
  Analytical inertia is recalculated from the resulting dimensions and mass.
  Zero/negative scale and non-finite scene state are rejected for simulation.
- Properties has a **Dynamic body** checkbox. Checked objects move; unchecked
  objects stay fixed. The per-instance choice is saved in the scene as
  `body_type`, overrides the part's default, and applies to newly opened Render
  windows. Unchanged older scenes keep their original defaults. Cancel does not
  apply edits. Static bodies retain their starting velocity for a later switch
  back to dynamic, but that velocity has no effect while static.
- Legacy OBJ-based parts default to static triangle-mesh colliders with friction
  0.5 and restitution 0 (unless overridden in Properties). Checking Dynamic body
  gives them a moving convex collision hull and a default mass of 1 kg. The hull
  fills concavities, and inertia is approximated by Bullet about the object's
  local origin; physical mass properties cannot be inferred reliably from these
  legacy meshes. The status line identifies legacy bodies.
- The optional floor is an infinite immovable collision plane at y=0, shown
  as a finite shaded patch. Bullet multiplies the contacting friction and
  restitution coefficients. The floor uses factors of 1 so each part's own
  coefficients determine its floor contact. Box-to-box contact combines both
  materials using Bullet's product rule.
- Gravity starts at [0,-9.81,0] m/s². It can be changed live or set to zero.
  Body linear/angular damping is zero because the file format has no damping
  setting; contact friction still dissipates energy.

This is real-time rigid-body playback. Rendering follows simulated time rather
than guaranteeing wall-clock time: GUI catch-up caps at 0.1 s per frame to keep
the window responsive. A discrete contact solver permits small transient
penetration and numerical error; this is not a high-speed impact accuracy
guarantee. The schema does not yet specify deformable/thermal/fluid behavior,
joint constraints, force curves or physical extensions. Such metadata is not
silently treated as a physical law. JSON geometry remains limited to boxes.

## Validation on this device (2026-11-02)

- `.venv/bin/python -m unittest discover -s tests -v`: **41 tests passed**,
  including ten new physics tests. Checks cover analytic free fall, additional
  acceleration, editor rotation conversion, angular motion, floor bounce and
  settling, reset repeatability, equal-mass collision momentum exchange,
  friction, static legacy mesh contact, scaled density/explicit mass and inertia,
  independent clients, editor isolation and invalid scale.
- `.venv/bin/python tests/gui_physics_playback.py`: **passed on the actual
  desktop**, using approved display access and OpenGL 4.6 on Intel UHD 620.
  Checks exercise the real Render QAction, separate visible window, automatic
  simulation advancement, editor isolation, Play/Pause/Step/Reset, live gravity,
  floor removal/restoration, camera framing, multiple windows, valid framebuffer
  capture and solver cleanup. No Qt callback errors occurred.
- The playback framebuffer `/tmp/simuo-physics-playback.png` was visually
  inspected: visible cyan part, floor and axes. Production modules compile;
  dependency consistency (`pip check`) and `git diff --check` pass.

The dependency was built and installed into this project's `.venv`; no global
Python installation was changed. Existing packaged executables have not been
rebuilt. Linux/OBJ-import work from other agents was preserved, and its existing
automated tests passed with these changes.
