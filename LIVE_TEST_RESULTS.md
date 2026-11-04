# Concurrent regression monitor

This file is written by the independent tester while implementation continues. Desktop details and earlier findings are in TEST_RESULTS.md. The monitor reruns the application suite when source/tests change; it does not edit application code.

## Completed live testing pass

- First snapshot: 126 passes, one Windows-only skip.
- While changes landed: 134 passes, one Windows-only skip, one error in `test_pull_face_after_multiple_extrusions_keeps_exact_support_precision`. Desktop face-pull/boss volume assertions also failed. Results and logs were posted in TEST_RESULTS.md and IMPLEMENTATION_NOTES.md for the implementing agents.
- After the feature agent's precision fix: **135 passes, one Windows-only skip** (136 discovered). Full log: `/tmp/simuo-live-unit-tests-final.log`.
- Arc desktop test passes: drawing, explicit radius, closure, native reload, OBJ/STL, GPU scene import and physics playback.
- Feature desktop diagnostic passes: plane selection, sketch/extrusion dialogs, face picking, manual dimension, joined extrusion, direct face pull, undo/redo, native reload, GPU/physics. Actual volumes match expectations within test tolerances.
- Independent arc + extrusion + metadata/radius persistence + mesh-volume/watertightness + physics probes pass on Front, Right and Top planes.
- Existing `John.simuOPart`, `Triangle.simuOPart`, arc sample and sketch sample open/migrate/import successfully without altering those files.
- Dependencies and `git diff --check` pass. The source monitor observed no further edits for two minutes and has stopped. No background monitoring is promised after this turn.

Source/test hashes: `/tmp/simuo-live-snapshot.json` and `/tmp/simuo-live-final-snapshot.json`. Changed files during the pass included feature geometry/editor, plane viewport, feature GUI tests and new viewport tests. Native Windows GUI/build remain unverified here.
