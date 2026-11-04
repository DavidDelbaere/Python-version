# Physics-capable part rendering migration

**Subsequent feature:** the user requested live physics playback. This is now
available through Test → Render and the Render toolbar button. See
PHYSICS_RENDER.md for the current implementation and checks; statements below
about physics playback being outside scope describe the earlier migration.

The main editor now renders version-1 JSON `.simuOPart` assets while preserving
legacy OBJ-based parts. This is the production integration of the previously
isolated format experiment, authorized by the user's follow-up request.

## Try it

Run `./run.sh --new`, choose **Import**, and select
`Assets/aluminum_cube.simuOPart`. The editor frames a cyan 20 cm cube at its
file-defined starting position. Save and reopen the scene to retain its instance
transforms/motion and reload its physical definition.

## Implementation

- `src/part_format.py`: renderer-independent v1 validation and domain object,
  promoted from the frozen experiment. Density-derived/explicit mass, analytical
  box inertia, material coefficients, metadata and spawn defaults are retained.
  The prototype floor-overlap restriction is removed because the editor has no
  physical floor. Numerical overflow is normalized to a validation error.
- `src/part_assets.py`: content dispatch, legacy OBJ parsing and box mesh
  generation. Invalid JSON is never retried as OBJ. GPU data is interleaved
  float32 position/normal vertices; analytic box normals avoid underflow.
  Non-finite or collapsed GPU geometry and initial positions with insufficient
  float32 precision are rejected. The normal model-editing controls keep their
  existing behavior; arbitrary subsequent transforms are not a physics contract.
- `src/scene.py`: CPU asset data and the validated part definition belong to
  scene objects. JSON spawn defaults initialize imported instances; explicit
  scene data overrides them. Asset geometry is parsed once before GPU upload.
- `src/renderer.py`: both live imports and initial scene uploads share one GPU
  upload routine. Color is a per-object shader uniform, including the original
  gray for legacy meshes. Camera framing makes the supplied SI-sized part
  visible without rescaling its geometry.
- `src/simuO.py`: validates assets before replacing a scene or adding imports,
  reports import failures, frames JSON imports and single-part JSON scenes, and
  saves/restores instance velocity, acceleration and angular velocity alongside
  existing transforms. Scenes still reference external parts with portable paths.

The experiment is left intact for comparisons. Production code has no runtime
dependency on `experiments/`. Existing PyInstaller asset/source collection covers
the added source modules and sample; no build-spec or dependency change is needed.
Packaged executables were not rebuilt in this task.

## Executed checks (2026-11-02)

- **PASS:** `.venv/bin/python -m unittest discover -s tests -v`: nine tests for
  topology, outward normals, dimensions, color, mass/inertia, scene spawn data,
  custom metadata, real legacy cube/teapot assets, malformed JSON, version/shape
  rejection, UTF-8 BOM handling, negative coordinates, legacy negative indices,
  zero-index rejection and the other tester's extreme-number cases.
- **PASS:** `.venv/bin/python tests/gui_part_render.py` on the actual desktop,
  with approved display access. OpenGL 4.6 Core Profile, Mesa Intel UHD 620.
  Startup JSON upload rendered 36 vertices with 3,889 cyan pixel samples;
  screenshot `/tmp/simuo-json-part.png` was visually inspected. Save/reload
  preserved transforms and all motion fields, with material and metadata loaded
  from the referenced asset. Legacy and JSON parts imported into one viewport.
  Invalid part imports and projects displayed errors and preserved both scene
  objects and GPU objects. No uncaught Qt callback errors.
- **PASS:** Python compilation of all changed/new production modules and
  `git diff --check`.

## Scope

JSON v1 supports solid boxes. Arbitrary legacy OBJ meshes continue to render,
but do not acquire physical material data automatically. The production editor
stores/loads physics-ready data; it does not run the experiment's gravity/floor
solver. Full rotational dynamics, generalized colliders and property-editing UI
remain outside this rendering migration. Scene saves reference part definitions
rather than embedding material/metadata snapshots.

The Linux-agent handoffs were consulted, including PART_TEST_RESULTS.md. The
launcher, startup-menu and build work were preserved. Direct sessions for those
agents were unavailable; coordination is recorded in the experiment's shared
COORDINATION.md.
