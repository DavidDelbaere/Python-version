# Independent Linux test results

Updated 2026-11-02 after the Linux implementation handoff. This file is the handoff for the agent making Linux compatibility changes. This tester has not changed application code.

## Free point movement — 2026-11-03

Select line mode now supports dragging endpoints. Free points move off-grid, including the origin endpoint; incidental horizontal/vertical alignment does not constrain dragging. Explicit dimensions and geometric relations remain active. The dragged endpoint is the only solver unknown, so other endpoints remain unchanged. Arc radii are preserved, invalid/crossing/collapsed geometry is rejected, and numerical no-op moves do not dirty the sketch. Canvas preview is committed on release as a single undo step; Esc restores the original geometry. Feature models rebuild only after release, retaining the original model if commit fails.

Verification: **185 passed / 1 Windows-only skipped** (186 discovered), including twelve new geometry/editor tests in `tests/test_point_dragging.py`. Desktop `tests/gui_point_dragging.py` passes real pointer movement, one-step undo/redo, horizontal-constrained dragging, Esc cancellation and native save/reopen. The first desktop harness run used an incorrect constraint-method name; after correcting the harness to `apply_geometric_constraint`, the complete rerun passes. `git diff --check` passes.

## Sketch and feature deletion — 2026-11-03

Implemented at user request: Backspace/Delete on the sketch canvas or line table removes the selected segment. Closed outlines open with the other segments intact; the default feature editor splits open outlines at a middle-segment deletion into separate draft sketches. Arc curvature and surviving dimensions are preserved. Features menu commands and feature-tree Backspace/Delete support sketch/extrusion removal; deleting an extrusion keeps the sketch. Confirmations list dependent face-supported sketches, cancellation preserves all geometry, and deletion participates in Undo/Redo. Shortcuts are scoped so text/numeric entry still handles Backspace normally.

Verification: **150 passed / 1 Windows-only skipped** (151 discovered). Added `tests/test_sketch_deletion.py`: thirteen geometry/UI regressions cover real Qt key events on canvas/table/tree, field editing, arc/dimension preservation, connected-outline splitting and persistence, sketch versus extrusion deletion, dependency confirmation/cancellation, preserving unrelated plane sketches, and undo/redo. `git diff --check` passes. These keyboard events were tested with Qt's offscreen backend; native Windows remains pending CI.

## Live testing of concurrent arc and 3D feature work (in progress)

**Final result for this pass: 135 passed, 1 Windows-only skipped (136 discovered).** The precision regression reported below is resolved in the latest source. Arc and feature desktop workflows pass, as do independent cross-feature checks on all three planes. Existing user/sample part files remain loadable. The monitor stopped after two minutes without further source/test edits. See LIVE_TEST_RESULTS.md for the concise final handoff and `/tmp/simuo-live-unit-tests-final.log` for the full passing suite. Historical failures below are retained to show what was found and retested; they are no longer current failures.

**Desktop retest after the feature agent's precision change:** the diagnostic run now passes the entire feature workflow. Measured volumes are 0.00030800000262260375 m³ after the dimensioned boss, 0.0003180000029206267 m³ after the direct face pull, and 0.00030800000262260375 m³ after undo. Save/reopen, actual scene GPU import and live physics also pass. Reproduction harness: `/tmp/simuo-feature-debug.py` (current GUI test with added volume prints). The earlier failure is retained below for history; updated unit retest is underway.

**Second live suite result:** newer files now discover 136 tests; **134 pass, 1 Windows-only skips, 1 errors**. Failure: `test_pull_face_after_multiple_extrusions_keeps_exact_support_precision` in `test_feature_parts.FeatureGeometryTests`. Full output is `/tmp/simuo-live-unit-tests-latest.log`. A diagnostic desktop rerun also fails earlier at the `.000308` boss-volume assertion (line 121), so the desktop workflow is not yet a clean pass. Continue treating the feature-editor work as under active test.

**First desktop failure for feature agent:** `tests/gui_feature_editor.py` exits 1 at line 129: `assert abs(editor.model.volume-.000318)<1e-8`. Top Plane selection, initial sketch closure and first Extrude dialog passed before the failure. Full traceback is in `/tmp/simuo-live-desktop-tests.log`. Both `feature_editor.py` and the GUI harness changed during the testing pass; investigating whether this is a product regression or expected-volume error. Arc desktop checks pass, including manual R75 dimension, closure, reload, OBJ/STL and actual GPU/physics rendering. Please review the volume assertion while continuing feature work.

The user asked for independent testing while the other agents implement their features. No application source is changed by this live-testing pass. Please read this section for current results rather than the historical pass counts below.

- Baseline application suite: **126 passed / 1 Windows-only skipped** (127 discovered), using `.venv/bin/python -m unittest discover -s tests -v`. Full output: `/tmp/simuo-live-unit-tests.log`.
- Dependency consistency and whitespace checks pass: `.venv/bin/python -m pip check`, `git diff --check`.
- Independent integration probes pass on **Front, Right and Top** planes: create semicircular sketch, manually set 60 mm radius, close/extrude, compare volume against outline area × depth, save/reopen v3 with metadata and radius preserved, export OBJ/STL, reload OBJ, independently verify signed volume and two incident triangles per edge, load into a scene and advance Bullet with finite state.
- Real desktop arc and 3D feature workflows are being tested; results will follow. Output: `/tmp/simuo-live-desktop-tests.log`.
- Source/test SHA-256 snapshot: `/tmp/simuo-live-snapshot.json`. Concurrent changes will be checked and retested before concluding this pass. Native Windows validation remains pending Windows CI/desktop access.

## Manual line dimensions (latest)

Part Editor dimensions are now explicitly added by the user. New lines have no dimension annotation, and undimensioned table rows show a dash. Select an edge, enter a length and choose Add dimension; Update dimension edits it, and Remove dimension removes its constraint/label without changing the current geometry. The toolbar/dialog and double-click routes remain available. Only explicit dimensions are restored from the `.simuOPart` file. Sparse label hit-testing retains the original edge index.

Application suite: **90 passed, 1 Windows-only skipped** (91 discovered). Five additional regressions check no automatic labels, manually dimensioning a later edge, correct label selection, removal with unchanged geometry and undo/redo, canceled input keeping the document clean, and sparse-dimension save/reopen. README, PART_EDITOR.md and in-app guidance are updated.

Desktop verification: `.venv/bin/python tests/gui_part_editor.py` exits 0. Real mouse drawing/closure initially has no dimension labels, adding a dimension creates exactly one label, the saved part reopens correctly, and GPU scene import plus live physics rendering still pass. Both New Part/Open Part startup routes pass.

## Part menu exports and native save (latest)

At the user's request, the production sketch Part Editor now has **File → Export → OBJ… / STL…** and separate **Save SimuO Part / Save SimuO Part As…** actions. Export reuses the closed sketch's extruded mesh and atomic writes. Open outlines produce a clear instruction to close the sketch; draft sketches remain saveable as `.simuOPart`. Exports preserve the native file path, dirty flag, dimensions and material metadata in memory. Mesh geometry uses local coordinates in metres. The independent lab's File menu has matching OBJ/STL exports and a native definition save, preserving its existing SVG export.

Verification: production suite **81 passed / 1 Windows-only skipped** (82 discovered), independent lab **16 passed**. New tests check actual menu callbacks, OBJ reload, concave and reverse-wound geometry, STL signed volume and outward normals, native draft save, canceled dialogs, suffix normalization/overwrite cancellation, failure preservation, and explicit-mass/custom-property native saves. Desktop lab menu harness `python3 experiments/physics_parts/gui_part_files.py` exits 0: both export actions and native save work; cancellations write nothing and failed writes show errors. See `tests/test_part_exports.py` and `experiments/physics_parts/test_part_export.py`.

## Windows compatibility follow-up

Implemented at the user's request:

- `run.bat` launches the project's `.venv/Scripts/python.exe`, supports `SIMUO_PYTHON`, paths containing spaces, and arguments from another working directory. VS Code run/debug/build tasks now have Windows interpreter overrides.
- Fixed native Windows absolute model paths: valid drive-letter/UNC references must be tried before bundled same-name fallbacks. Existing portable relative and legacy recovery behavior is preserved.
- Atomic writes now close staging files before cleanup after a write failure, as required by Windows file locking. Failed writes retain the previous scene.
- Desktop test screenshots use `tempfile.gettempdir()` instead of Linux-only `/tmp` paths.
- README includes Windows 10/11 x64, Python 3.12, dependency installation, launching, desktop checks and native executable build steps. PyBullet 3.2.7 has no Windows wheels in its PyPI release listing, so source installation needs MSVC C++ tools and the Windows SDK. Linux dependencies are unchanged.
- Added `.github/workflows/windows.yml`: native Windows unit/lab tests, launcher from another folder, PyInstaller build and packaged `--help` startup, executable artifact. The workflow is configured locally; it has **not run** from this session.

Local results: application suite **48 passed / 1 Windows-only test skipped**, lab suite **11 passed** (59 passes total). VS Code JSON, PyInstaller spec syntax, workflow YAML parsing and `git diff --check` pass. Regression tests are in `tests/test_portability.py`. Native Windows install/build/GUI are **not verified on this Linux host**; the CI job must run after the changes are pushed, and interactive graphics still need a Windows desktop smoke test.

Linux desktop regression checks after these changes: `gui_part_render.py`, `gui_obj_import.py`, and `gui_physics_playback.py` all exit 0. Verified actual GPU rendering, mixed-format scene save/reload, OBJ conversion with temporary/permanent save paths, and separate physics playback windows with controls and solver cleanup.

## Latest: usability fixes completed and verified

The user authorized the testing agent to implement the outstanding fixes. The prior statement about not changing application code applies to earlier test passes only.

- New/Open/Close now share Save/Discard/Cancel protection for unsaved changes, including temporary parts. Cancelled save dialogs and write failures block the destructive action.
- Imports, repositioning and rotation mark the scene dirty; successful Save/Open/New reset that state. Saved unchanged scenes close without an unnecessary prompt.
- Save As keeps the original path/title and scene after failure, displays the failed destination with recovery guidance, and uses the atomic-save support already added by the OBJ agent. A failed atomic replacement preserves the previous file and removes its staging file.
- Added Help → Controls, camera hints in the status bar, clearer project/part action labels, and keyboard shortcuts. Unimplemented toolbar tools are disabled; the Window menu can reopen the temporary-parts panel.
- README describes both supported part formats and separates editor behavior from the standalone physics lab, and now documents controls and unsaved-work protection.

Verification: **31/31 editor tests pass**, including ten new project-safety tests and the OBJ import/save regression suite. **11/11 physics-lab tests pass**. Real desktop GPU integration passes again: colored JSON render, camera framing, mixed legacy/JSON imports, portable save/reload, invalid-input preservation. `git diff --check` passes. See `tests/test_project_safety.py` for permanent failure/cancellation regressions. The earlier usability defects listed below are resolved by this pass.

## Latest retest: passed

Using the new `.venv/bin/python`, all three menu checks (New, Import, Close) now pass with explicit Tk callback exception capture and no callback errors. The `<Map>` binding fix resolves the failure recorded below. Real GPU rendering, cube import, temporary scene save/reload with transforms, and bundled scene rendering also pass again. `.venv/bin/python -m pip check` and `git diff --check` pass.

The separate physics experiment's documented unittest discovery command currently discovers zero tests; it does not establish a passing experiment test suite.

## Usability and combined regression pass (latest)

Both implementing agents have usability feedback in `IMPLEMENTATION_NOTES.md` and `experiments/physics_parts/COORDINATION.md`. These are shared-file handoffs; direct access to their separate sessions is unavailable.

### Confirmed usability defects to resolve

Reproduction harness: `/tmp/simuo_usability_qa.py` using `.venv/bin/python` with desktop access. The harness prints diagnostic PASS/FAIL results (its exit status alone is not a usability pass).

1. **Unsaved work lost on Open:** populate a scene, choose Open Project and an empty valid scene. Even with the confirmation dialog mocked to Cancel, no confirmation is shown and the scene is replaced.
2. **Unsaved work lost on Close:** a populated unsaved scene closes without a Save/Discard/Cancel prompt.
3. **Save As failure escapes and changes the project path:** select a destination under a nonexistent parent directory. `FileNotFoundError` propagates without an error dialog, and `projectPath` changes to the failed destination. Preserve the original path and report the problem. A failed save must never authorize New/Open/Close to discard work.
4. **Discoverability review:** Help is empty; Select/Pan/Rotate/Move toolbar choices have no implemented branch in `toolSelected`. Disable unavailable actions or implement them, and display the actual camera controls.
5. **Documentation review:** root README still says all `.simuOPart` files contain OBJ, while the editor now accepts JSON parts. Explain both supported formats and distinguish editor capabilities from standalone-lab physics playback.

### Passing combined checks

- Production suite: `.venv/bin/python -m unittest discover -s tests -v` — **9/9 pass**.
- Standalone lab suite: `python3 -m unittest discover -s experiments/physics_parts -v` — **11/11 pass**. This supersedes the earlier zero-discovered-tests result while those files were still being created.
- `.venv/bin/python tests/gui_part_render.py` — **pass on actual GPU**: visible colored JSON part and camera framing, relative-path save/reload with transforms/motion/material/custom properties, live JSON and legacy imports in one viewport, invalid imports and projects preserve scene/GPU objects.
- Startup New/Import/Close, with explicit Tk callback exception capture — **all pass** again.
- `/tmp/simuo_part_gui_qa.py` — **all six interaction checks pass**: initial paused display, step/orbit, play/pause, SVG export, invalid Open preserves previous part, valid Open updates metadata and resets/pauses.
- New Project Cancel preserves current scene — **pass**.

The production JSON integration supersedes the earlier prototype-only limitation in PART_TEST_RESULTS.md. Standalone extreme-number findings in that report remain separate from production loader validation.

## Confirmed so far

- Host: Linux x86_64, kernel 6.8.0-38-generic; system Python 3.12.3; desktop DISPLAY=:0 (X11).
- `src/path/to/venv/bin/python` imports all dependencies in `src/requirements.txt`. `pip check` passes.
- System Python and `path/to/venv/bin/python` lack the application dependencies. Use the environment inside `src` for existing-install testing.
- All Python source files parsed successfully, including newly added `resources.py` and `project_paths.py`.
- Desktop startup via `timeout 10s src/path/to/venv/bin/python src/main.py` stayed running until the intentional timeout with no stderr when launched outside the sandbox. This confirms startup only; interaction and OpenGL checks follow.
- The sandbox blocks the desktop display and CustomTkinter font writes. `_tkinter.TclError: couldn't connect to display ":0"` inside the sandbox is a test-environment restriction, not an established application defect.

## Check scope

- Parse all bundled meshes and validate finite vertices and unit normals.
- Exercise startup menu New, Import, and Close callbacks.
- Create real OpenGL viewport, import cube, save/reload transforms, and open bundled scene.

Temporary test harness: `/tmp/simuo_qa.py`. More results will be appended here.

## Desktop results (first pass)

- PASS: Real OpenGL 4.6 Core Profile on Mesa 24.2.8, Intel UHD Graphics 620. Both shader programs initialized and framebuffer capture succeeded.
- PASS: Import cube (36 vertices), save temporary project, reload position `[1,2,3]` and rotation `[10,20,30]`, and reopen bundled `Assets/SimuOPart.simuO` with one GPU object.
- PASS: All five bundled meshes parse with finite vertices and unit normals: cube 12 triangles; teapot 6,320; stress_test 44,402; screw 197,870; Car 192,985. Large mesh parsing takes about 7–8 seconds per model on this system.
- ISSUE FOR IMPLEMENTING AGENT: All three startup actions return correct values, but stderr contains a Tk callback error from `src/startMenu.py:58` in `_grab_when_visible`: `self.wait_visibility()` raises `_tkinter.TclError: window ".!simuostartmenu" was deleted before its visibility changed`. Reproduced New, Import, Close with callbacks scheduled after 500 ms. Treat these as functional return-value passes with callback errors, not clean startup passes. Check visibility/grab handling with the withdrawn root; guard against the menu being destroyed during the nested visibility wait. Reproduction: `src/path/to/venv/bin/python /tmp/simuo_qa.py menu new` (requires desktop access).
- Screenshots: `/tmp/simuo-empty.png` and `/tmp/simuo-cube.png`.

## Portability checks

- PASS: `project_paths.resolve_mesh_path` resolves existing absolute paths, legacy Windows absolute paths with backslashes, missing legacy Unix absolute paths using bundled fallback, and a bare bundled mesh name.
- PASS: `stored_mesh_path` / `resolve_mesh_path` roundtrip across different project and mesh directories, including spaces in the repository path.
- PASS: Missing model raises `FileNotFoundError` with a diagnostic.
- PASS: `bash -n run.sh` and `src/path/to/venv/bin/python src/main.py --help`.
- PASS: Launching `run.sh --help` from `/tmp`, with `SIMUO_PYTHON` set to the existing interpreter's absolute path, succeeds.
- CONFIRMED FAILURE: Repeated all three menu checks with explicit Tk callback exception capture. New, Import, and Close each exit 1 due to the same `wait_visibility()` error. Render/import/save/reload checks exit 0.

## Limits

This pass checks the source installation and actual GPU rendering. It does not establish that the old packaged executable contains the current fixes. No application source was changed by the tester. Test output may reflect files changing during the other agent's work; rerun `/tmp/simuo_qa.py` after fixes stabilize. The menu harness now treats Tk callback exceptions as failures, rather than relying only on its return value.
