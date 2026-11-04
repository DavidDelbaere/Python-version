# Linux compatibility handoff

Point-dragging handoff: user requested moving unconstrained points. Added `Sketch.move_point` and a drag mode in `SketchCanvas`, preserving the concurrent constraints implementation. `_solve` has an optional drag argument: only the selected endpoint is solved, without inferred axes or the first-point anchor; normal dimension/constraint edits keep prior behavior. Other endpoints stay fixed and explicit line/radius/H/V/Equal constraints remain enforced. Preview does not update feature-model history; release commits once and Esc cancels. Tests: 185 pass / one Windows-only skip; real desktop drag/constraint/undo/save checks pass. New harnesses: `tests/test_point_dragging.py`, `tests/gui_point_dragging.py`.

## Sketch visual and snapping fixes, 2026-11-03

The requested sketch-page fixes are in src/part_editor.py. Arc strokes/previews
explicitly use NoBrush after endpoint dots, preventing accidental chord/wedge
fill; intentional closed-face shading remains. Exact endpoint/origin snapping
runs before grid rounding, with pixel-based capture/release, stable locks and
nearby-point takeover. Clicks and closure use the same snapped coordinates.
The origin has a visible marker/label and View → Center sketch origin (O).
No file-format or solid/physics changes were needed. Existing plane, arc,
dimension and delete-tool code was retained.

Eight new tests in tests/test_sketch_snapping.py cover zoom-independent exact
snapping, hysteresis/takeover, origin placement/recentering, off-grid line and
arc closure, unfilled preview pixels and retained closed-face shading.
Offscreen rendering was visually checked in /tmp/simuo-unfilled-arc-preview.png.

## 3D feature editor completion

The 3D plane/face task is complete. Startup launches FeaturePartEditor, with a
3D viewport, Front/Right/Top hierarchy, clickable planes/faces, dimensioned
sketches on those supports, additive sketch extrusions and direct flat-face
pulls, feature undo/redo, v3 save/reopen, migration and joined-body OBJ/STL export.
Sample: Assets/feature_demo.simuOPart; usage/schema/limits: FEATURE_EDITOR.md.

Final snapshot: 138 automated tests, 137 pass / one Windows-only skip. The real
desktop feature harness passed initial plane extrusion, face sketch/dimension,
joined boss, repeated direct face pull, undo/redo, file reload, main OpenGL
scene import and live physics. The precision regression and missing-dependency
error are covered. Final dependency consistency and diff whitespace checks pass.
Manifold 3.5.4 is installed in .venv and pinned in requirements. Existing source,
arc tools, exports and plane-picking assistance were retained. No packaged
binary was rebuilt. No further shared application edits are planned here.

## 3D feature editor validation update

The latest desktop `tests/gui_feature_editor.py` passes all stages, INCLUDING
the repeated direct-face pull which earlier assistance runs caught failing.
The cause was float32 display coordinates leaking into support frames, followed
by one-ULP coplanar gaps in exact boolean joins. Fixed in feature_geometry.py:
keep native double precision for faces/supports, apply a tiny inward overlap
to outward face additions while preserving the requested end, and discard
GPU-collapsed zero-area triangles in display/export data. Regression test:
test_pull_face_after_multiple_extrusions_keeps_exact_support_precision.

Final workflow: Top-plane selection → real drawing → base extrusion → 3D face
pick → dimensioned face sketch → joined extrusion → direct face pull → undo/
redo → v3 file reload → main OpenGL scene → live physics Render. All passed.
Latest automated snapshot: 136 tests, 135 pass and one Windows-only skip.
Sample: Assets/feature_demo.simuOPart. Plane-picking assistance and arc outline
changes were detected and retained. Please preserve the native-frame/overlap
fix if doing further geometry edits. Remaining work in this session is docs
and final checks; no broad base-editor rewrite is planned.

## Active 3D feature-editor ownership

Final independent live retest: **135 tests pass, one Windows-only skip**, including `test_pull_face_after_multiple_extrusions_keeps_exact_support_precision` and the added plane-viewport tests. Arc GUI and complete feature GUI diagnostic both pass. The monitor stopped after two minutes without further source edits. No application source changes were made by this test pass. See LIVE_TEST_RESULTS.md for the consolidated handoff.

Independent tester follow-up: after the latest `feature_geometry.py` change, the desktop diagnostic now passes direct face pulling, undo/redo, save/reopen and GPU/physics integration. Volumes: boss .00030800000262260375; pull .0003180000029206267; undo .00030800000262260375. The prior `.000318`/support precision failure is therefore cleared in this desktop rerun; a fresh unit-suite pass is underway. See TEST_RESULTS.md for chronology.

Independent live tester result: current desktop `tests/gui_feature_editor.py` failed its volume assertion `.000318` at line 129 after initial Top Plane/first extrusion passed. Application/harness files changed concurrently. Detailed traceback: `/tmp/simuo-live-desktop-tests.log`; current findings at top of TEST_RESULTS.md. Investigating actual volume versus test expectation; no production source changes made by tester. Arc GUI and cross-feature arc/radius/save/export/physics integration on all three planes pass.

This session is implementing the user's Front/Right/Top hierarchy, 3D viewing,
flat-face sketching and additive extrusions in NEW modules feature_geometry.py,
feature_document.py, feature_editor.py and part_viewport.py. It adds JSON v3
feature parts alongside v1/v2, plus Manifold 3.5.4 for joined solids. Existing
arc/export/menu work is being preserved. Only small hooks are needed in the
base part_editor.py: context drawing/plane label and run_part_editor launching
FeaturePartEditor. Please retain those hooks when editing the base editor.
The feature subclass reuses existing sketch/dimension controls and will use
outline_points for curved contours from the concurrent arc task. Shared
part_format.py will retain the arc task's v2 changes and add a v3 branch.

Manual dimension follow-up: user requested explicit dimensions instead of automatic labels. `src/part_editor.py` now draws/hit-tests labels only for non-null dimension entries, preserving sparse edge indices. Undimensioned rows show a dash; Add/Update/Remove dimension controls make the operation explicit. Existing file geometry already stores null versus explicit driving lengths, so no format change was needed. Five new regressions in `tests/test_sketch_parts.py` cover drawing without dimensions, adding on a later edge, removal/undo/redo, dialog cancellation, and persistence. Latest application suite: 90 pass, one Windows-only skip.

## Part editor completion handoff

The user's sketch-editor task is complete: startup New Part/Open Part, direct
`.simuOPart` routing and `--part-editor`, a Qt line/face editor with driving
dimensions in mm, sketch undo/redo, thickness, draft/closed saves and reopen,
plus production JSON v2 import/render/physics support. Details: PART_EDITOR.md.
New modules: sketch_geometry.py, part_document.py, part_editor.py; sample:
Assets/sketch_plate.simuOPart. The new format retains editable points and lengths
in SI meters. Version-1 boxes and legacy OBJ scene imports remain supported.
Dynamic sketch collisions use a convex hull, with a visible note in Properties.

Concurrent part-export changes to part_editor.py and the standalone viewer were
detected and preserved, including Save SimuO Part labels and OBJ/STL export. The
desktop harness selects Save by Ctrl+S so it tolerates the updated label. Final
automated snapshot: 82 tests, 81 pass / one Windows-only skip. Real desktop
tests/gui_part_editor.py passes startup routes, real drawing, face closure,
dimension editing, save/open, scene GPU upload and live physics Render. Narrow
window screenshots were inspected. No dependencies or packaged binaries changed.

Part-export ownership update: user requested File → Export → OBJ/STL and separate Save SimuO Part. This agent added `src/part_export.py` and updated only the imports, File actions and new `export_mesh` method in `src/part_editor.py`. Please preserve these during ongoing sketch-editor edits. Export reuses `prism_vertices`, keeps the document/path/dirty state, uses atomic writes, and rejects unfinished outlines with an actionable message.

Windows follow-up completed locally at user request: `run.bat`, VS Code Windows overrides, native absolute-path fix, Windows-safe atomic staging cleanup, portable GUI screenshot paths, Windows README setup/build guidance, and a Windows CI workflow. Windows source installation of the pinned PyBullet requires MSVC Build Tools; no alternative dependency was substituted. `tests/test_portability.py` covers path and file-cleanup regressions. 59 tests pass locally, one Windows-only test skips. Native Windows execution is pending CI/desktop verification; see TEST_RESULTS.md.

Changes are ready for retesting. `run.sh` now uses the new `.venv`, with all requirements installed and `pip check` passing. `SIMUO_PYTHON` still supports the existing environment.

The startup callback error reported in TEST_RESULTS.md was fixed by replacing the nested `wait_visibility()` call with a `<Map>` binding. `_grab_when_visible` only grabs when the menu itself is mapped and viewable. Please rerun New, Import, and Close with callback exception capture against the current source.

Other changes: working-directory-independent resource lookup and launcher; portable scene mesh references with legacy Windows path recovery; missing-project/model error dialogs; camera key state reset on focus loss and auto-repeat handling; corrected asset inclusion in both PyInstaller specs; Linux VS Code run/build configuration; setup and testing instructions in README.md.

Implementation checks: Python/spec AST syntax, shell syntax, `git diff --check`, dependency consistency, and launcher `--help`. GUI, rendering, and packaged build verification belong to the independent tester. Existing packaged binaries were not rebuilt.

## Usability feedback from independent tester (2026-11-02)

Ownership update: the user has now asked this testing agent to fix the outstanding usability items directly. I am editing `src/simuO.py` for shared unsaved-change protection, dirty tracking, save-error regressions, control guidance, and clear action labels, plus adding regression tests. Please avoid overlapping edits to those sections until this handoff is updated.

Completion update: these fixes are now implemented and verified. Shared Save/Discard/Cancel protection covers New/Open/Close, edits track dirty state, failed saves retain the scene and original project path, and control guidance/action labels are updated. The OBJ agent's atomic-write and temporary-parts workflow is preserved. Added ten permanent project-safety regression tests and adjusted GUI/test cleanup to discard test data explicitly under the new close prompt. Results: 31 editor tests, 11 lab tests, and the actual GPU integration check pass. See the newest section of TEST_RESULTS.md; older listed usability defects are historical.

The user explicitly asks both implementing agents to prioritize user friendliness and regression tests. Please review these production-editor issues before marking work complete:

- Protect unsaved work when opening another project and closing the editor, with Save / Discard / Cancel. Currently only New has a save prompt. Cancel must preserve the current scene.
- Catch save/write failures and show an actionable error dialog; preserve the original project path if Save As fails. Do not let failed saves discard the current scene.
- Make available tools discoverable: Help currently has no actions, and Select/Pan/Rotate/Move appear selectable but have no behavior in `toolSelected`. Provide visible camera/control guidance and disable tools that are not implemented.
- Name file actions clearly: Open Project, Import Part, Save As. Keep README model-format guidance consistent with the JSON part integration as it lands.

Independent automated regression results and usability reproductions will be added to TEST_RESULTS.md. The other sessions are not directly reachable through this session's collaboration tools; this shared file is the handoff.

Executed follow-up: all 20 combined unit tests and desktop rendering/playback/startup regressions pass. Usability harness `/tmp/simuo_usability_qa.py` confirms Open and Close do not protect unsaved work, and failed Save As raises FileNotFoundError and changes projectPath. New Cancel correctly preserves the scene. See TEST_RESULTS.md for exact results. Please fix and provide a completion handoff for retesting before the requested Git branch is finalized.

## OBJ import workflow handoff

The OBJ task has added `src/temporary_parts.py`, the Temporary parts dock, OBJ import confirmation, and per-part permanent save dialogs in `saveFile`. Unsaved-change protection from the usability task was detected and preserved. No more edits to the shared `simuO.py` sections are planned by the OBJ task. Added tests: `tests/test_obj_import.py` and `tests/gui_obj_import.py`. The first 21 combined tests passed before the usability changes landed; the final combined suite is being rerun. Noticed and retained the usability task's Discard patch in test cleanup to avoid prompting on dirty scenes. OBJ copies deliberately use the supported legacy mesh-part format, preserving arbitrary geometry without inventing physical properties or a new JSON schema.

OBJ task final verification: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v` passed all 31 combined tests. `.venv/bin/python tests/gui_obj_import.py` passed on the desktop with real OpenGL 4.6/Mesa Intel UHD 620: OBJ conversion, temporary file/list, rendering, cancellation, permanent part save, relative scene reference, and GPU reload. Changed Python syntax and `git diff --check` pass. No further shared application edits are planned by the OBJ task. Packaged executables have not been rebuilt.

## Part identifier rename

At the user's request, JSON part `format` is now `.simuOPart` instead of `simuo.part`. Both production/lab loaders, both aluminum samples, the lab format documentation/duplicate-key fixture, and root README were updated. A regression test checks the new identifier and rejection of the old identifier. Final checks: 42 production tests and 11 lab tests pass; `git diff --check` passes. Existing private JSON assets must update their `format` field; OBJ-based parts are unaffected.

## Properties button (bounce and velocity)

Added a toolbar Properties action with object selection, bounce (0–1), and starting velocity X/Y/Z (m/s). OK applies per-instance scene overrides; Cancel preserves the object. Original part files and other instances remain unchanged. Scene serialization stores restitution alongside velocity, with part-default fallback for older scenes. PhysicsWorld now uses the instance's restitution for both JSON bodies and static mesh colliders. Static behavior remains unchanged and is explained in the dialog. Open a new Render window after editing to use the new values. Unedited fields preserve their original numeric precision.

Verification: all 10 new Properties tests pass; combined suite ran 59 tests with 58 passing and one Windows-only test skipped on Linux. Real desktop `tests/gui_properties.py` passes: toolbar action, actual dialog input/OK, scene save/reload, updated restitution in Bullet, rendering, and source-scene isolation. Syntax and `git diff --check` pass. README includes usage instructions. No packaged executable rebuild was performed.

## Part viewer visual alignment

The standalone `experiments/physics_parts/viewer.py` now follows the main scene editor's charcoal palette, top menus, left toolbar, central viewport, right properties panel, and bottom status/control bars. Added Frame Part and panel visibility controls; the inspector hides in narrow/tiled windows. Matching grid/export colors and `preview.svg` were updated. Concurrent native-part/OBJ/STL export additions from the other task were preserved. No production editor files were changed for this styling task.

Verification: all 16 current standalone tests pass. The desktop interaction harness passes all six checks (rendered faces, step/orbit, play/pause, SVG export, invalid Open preservation, valid Open/reset); narrow and full-size screenshots were inspected. `git diff --check` passes.

## Current part-menu review ownership

The user requested checking the other agent's progress and menu usability. This session is making small UI-only changes in `src/part_editor.py`: action labels/tooltips, explicit Select, Help/View menus, and matching canvas colors. Sketch geometry, file/export implementations, and startup routing will be preserved. Other agent progress is visible via shared files rather than direct session status. A menu regression test and the existing desktop sketch workflow will be run after the review.

Part-menu review complete: production PartEditor now has explicit Draw lines / Select line controls, Close outline / Set length / Frame sketch labels, tooltips, F framing, F1 controls/workflow, View → Part properties, and a left toolbar with matching charcoal canvas colors. The fixed properties column was converted to a scrollable dock that hides/restores for narrow windows; screenshots confirmed the tiled-window clipping issue and the resulting usable canvas. File/export/geometry implementations were preserved. Added four menu/layout regression tests. Final combined results: 86 tests run, 85 passed, one Windows-only skip; actual desktop startup New/Open Part, mouse drawing, dimensions, Save/Open, scene import and physics Render all pass. README updated. This session has finished editing the shared part-editor file.

## Arc feature ownership

The user requested editable arcs with radius dimensions. This session is editing `src/sketch_geometry.py`, the canvas/action/dimension sections of `src/part_editor.py`, and geometry bounds in `src/part_format.py`, plus arc tests/docs. Existing file/export/startup implementations are preserved. Arcs will be stored as optional per-edge bulge definitions in sketch geometry, keeping line-only v2 files compatible; scene/export meshes will tessellate curves.

## Arc feature completion handoff

Editable circular arcs are implemented in the production PartEditor. Draw arcs uses start / through / end clicks; connected arcs reuse the previous endpoint. Lines and arcs can close one outline, including two-arc circles. Esc cancels a pending arc. Selection/hit testing and sketch drawing use analytic circular geometry. Manual Add/Update/Remove dimension behavior from the other task is preserved: arc dimensions show `R` and edit radius in mm; line dimensions still edit length. Radius changes keep endpoints fixed and preserve minor/major branch, with actionable errors below half-chord radius. Undo/redo and file roundtrips retain arcs and radius constraints.

Sketch v2 geometry now accepts optional `arcs`, one null or `{"bulge": tan(signed_sweep/4)}` entry per logical segment. Old line-only serialization is unchanged. Use `sketch.outline_points` rather than `sketch.points` for rendered/mesh contours and bounds: points stores logical endpoints only. Added the one-line contour change to `feature_geometry.py` so the other agent's feature extrusions include curves; no other feature implementation was changed. `feature_document.py` endpoint translation preserves bulges correctly. Scene/export tessellation uses <=5° angular steps, and mesh area/centroid/volume are based on that approximation. New sample: `Assets/arc_plate.simuOPart`. README and PART_EDITOR.md explain the workflow and schema.

Checks: 18 arc-specific tests pass (including new feature extrusion integration). The combined suite most recently ran 122 tests with 121 passing and one Windows-only skip before the final extra arc/feature test was added. The real desktop `tests/gui_arcs.py` passes drawing, manual R75 input, line closure, .simuOPart save/reopen, OBJ/STL exports, actual OpenGL scene import, and live physics. Screenshot `/tmp/simuo-arcs.png` was inspected. `git diff --check` passes. This session has finished shared application edits for arcs; please preserve these during the ongoing feature-editor integration.

Arc verification update after the other agent connected FeaturePartEditor to startup: the new editor inherits the Arc tool correctly. An added test exercises automatic sketch creation from Draw arcs, mouse input, radius editing, extrusion, v3 save/reopen and asset load. All 19 arc-specific tests pass. The full suite ran 123 tests with 122 passing and one Windows-only skip immediately before that final feature-editor test was added. Updated FeaturePartEditor's Help wording to mention arcs/radius; its feature logic remains unchanged. The two touched feature-module locations are the outline_points extrusion contour and the Help text only.

## Plane/face support assistance ownership

The user explicitly asked this session to help the other agent's sketch-plane/face goal. I am taking the isolated PartViewport support task: clickable reference planes with visible selection, scale-consistent plane patches, curved draft outlines and framing, plus viewport-specific regressions. I will edit `src/part_viewport.py` and add `tests/test_plane_viewport.py`. In `feature_editor.py`, only a plane_selected signal hookup and small select_plane routing slot will be added, preserving the owner's feature/extrusion logic. Direct other-session messaging is unavailable; this file is the shared coordination point.

Plane/face assistance interim checks: all seven new viewport tests pass; full suite ran 135 tests with 134 passing and one Windows-only skip. The shared desktop feature harness passed initial Top-plane drawing/extrusion but failed its newer direct-face-pull volume assertion (`tests/gui_feature_editor.py`, expected .000318). `feature_editor.py` and that harness were being edited concurrently around the run. I am leaving the owner's extrusion implementation alone and rerunning against the latest saved code before drawing conclusions. Please retain the PartViewport plane signal and select_plane routing added by this task.

## Plane/face support assistance complete

Completed the viewport support task: reference-plane picking and orange selection, synchronized tree selection via plane_selected/select_plane, face-over-plane selection priority, scale-consistent plane patches, and curved sketch preview/framing using outline_points on every support. Only PartViewport and the small plane-routing hookup/slot in FeaturePartEditor were changed; the other agent's model/extrusion implementation was preserved. PART_EDITOR.md now explains plane/face selection, New Sketch, Finish Sketch, extrusion, direct face extrusion, and v3 feature files.

All seven new tests in test_plane_viewport.py pass. Combined suite: 135 run, 134 pass and one Windows-only skip. Additional offscreen mouse checks pass for all three planes and a curved Top-plane draft; `/tmp/simuo-plane-support.png` was inspected. The latest actual desktop `tests/gui_feature_editor.py` now passes ALL checks, including direct face extrusion and expected volume, joined geometry, undo/redo, file reload, scene import and physics. The earlier failure noted above was a concurrent-edit snapshot and does not reproduce against the owner's latest saved implementation. `git diff --check` passes. This support task is complete; no more shared source edits are planned by this session.

## Sketch constraints ownership

The user requested Horizontal, Vertical and Equal line relations plus deletion of constraints. This session is editing sketch_geometry.py and the base PartEditor selection/constraint UI, with new tests/docs. Constraints will be optional serialized sketch data inherited by feature parts; old files and arcs are retained. Segment deletion must remap/drop affected relations, and removal of a relation will preserve current geometry. No feature/extrusion logic changes are planned.

## Sketch constraints completion

Implemented Horizontal, Vertical and Equal relations on selected straight segments. Ctrl-click multi-selection works in canvas and table. Controls are in a Constraints menu and the properties panel. The Constraints list includes geometric relations plus length/radius dimensions; selecting an entry highlights its edges. Delete button/context menu and focused-list Delete/Backspace remove the rule without deleting geometry. A dedicated ConstraintList key handler avoids reliance on window activation for deleting list entries. Relation markers on the sketch are grouped to avoid overlapping labels.

Optional sketch `constraints` records have `type` and zero-based `segments`; v2 sketches and v3 features persist/validate them. Solver updates honor explicit relations and existing dimensions; conflicts are transactional and opposite orientation rules report how to resolve them. Removing constraints preserves geometry. Segment deletion remaps surviving relations and drops invalid/split equality references. Undo/redo and feature extrusion/save/reload are supported. No feature/extrusion implementation changes were made; FeaturePartEditor's Help text was updated for the inherited controls.

Tests: 15 new constraint geometry/editor regressions pass. Latest full application run: 186 tests, 185 pass / one Windows-only skip. The desktop `tests/gui_constraints.py` passes actual drawing, Horizontal/Vertical menu use, Ctrl-click Equal, linked driving dimensions, Delete from the constraint list, geometry preservation, undo/redo, constrained extrusion and file roundtrip. Screenshots were inspected; a layout review prompted grouped H/V/= markers. README, PART_EDITOR.md and FEATURE_EDITOR.md contain usage/schema guidance. `git diff --check` passes. This task is complete and no further shared source edits are planned by this session.
