# feature_editor.py: backend guide

Source: [src/feature_editor.py](../../src/feature_editor.py). [Documentation index](../README.md).

The current editor integration layer for transactional feature-model edits, dependent-feature removal, context geometry, migration, and persistence.

This file serves both layers. See the [frontend companion](../Frontend/feature_editor.md) for its other responsibilities.

## How it works

`snapshot()` stores independent serialized history, active ID, and support. `accept_model(candidate)` builds first, then records undo, clears redo, replaces the model, binds the active sketch, and refreshes UI. `commit(sketch)` applies an edited sketch through copied feature history.

`dependent_features(roots)` follows face-support parent IDs transitively. Extrusion and deletion operations rebuild a candidate before committing. `sketch_context_geometry()` evaluates history before the active sketch and projects visible faces/edges into its support frame, caching by model identity and active ID.

## Contracts and editing considerations

- Rebuild failures propagate out of core edit helpers; frontend callers display warnings. Do not mutate accepted history before validation.
- `active_feature` is a dictionary owned by the model. Serialized geometry/snapshots are copied to isolate undo state.
- Context cache validity assumes accepted model replacement; in-place model mutation can leave cached context stale.
- `open_path()` migrates via `open_feature_document()`. `_save_to()` saves v3 and updates clean/path state only on success.
- Export writes the complete built union, not only the active sketch. No solid means no mesh export; drafts can still be saved.
- These methods remain Qt-bound. `FeatureModel` and document helpers are the headless backend interfaces.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`FeaturePartEditor.active_feature()`](../../src/feature_editor.py#L98) | Look up the currently active sketch/extrusion feature. **Output:** dict or None: Feature owned by the current model, or None if absent. |
| [`FeaturePartEditor.snapshot()`](../../src/feature_editor.py#L106) | Capture editable model history, active feature, and selected support for undo. **Output:** tuple: Independent geometry dictionary, active ID, and copied support. |
| [`FeaturePartEditor.restore(state)`](../../src/feature_editor.py#L114) | Rebuild a saved snapshot and restore its active sketch and support selection. **Output:** None. Replaces the model and refreshes the UI. |
| [`FeaturePartEditor.accept_model(candidate, active_id=None)`](../../src/feature_editor.py#L129) | Build a candidate before committing it, record undo history, clear redo, and mark the document dirty. **Output:** None. Replaces the model on success; build errors propagate before commitment. |
| [`FeaturePartEditor.bind_active()`](../../src/feature_editor.py#L153) | Deserialize the active feature into the working sketch and update its plane label. **Output:** None. Uses an empty Sketch if no feature is active. |
| [`FeaturePartEditor.commit(candidate)`](../../src/feature_editor.py#L439) | Validate an edited sketch, put it into a copied feature history, and rebuild/commit the candidate model. **Output:** None. Records undo and marks dirty on success; invalid edits propagate errors before commitment. |
| [`FeaturePartEditor.dependent_features(roots)`](../../src/feature_editor.py#L479) | Find transitive descendants whose face supports depend on the supplied features. **Output:** set: Dependent feature IDs, excluding the supplied root IDs. |
| [`FeaturePartEditor.accept_deletion(candidate, active_id=None)`](../../src/feature_editor.py#L517) | Commit a deletion candidate, choose a surviving active feature/support, and clear stale selections. **Output:** None. Records undo and refreshes the editor. |
| [`FeaturePartEditor.extrude_face(index, distance, symmetric=False)`](../../src/feature_editor.py#L646) | Derive a sketch from a selected flat face and add a joined extrusion through a candidate model. **Output:** None. Commits history and frames the result; invalid boundaries or solids raise an error. |
| [`FeaturePartEditor.extrude_active(distance, symmetric=False)`](../../src/feature_editor.py#L671) | Set the active closed sketch's extrusion depth/mode in copied history and rebuild the solid. **Output:** None. Commits history and frames the result; invalid geometry raises an error. |
| [`FeaturePartEditor.sketch_context_geometry()`](../../src/feature_editor.py#L762) | Build the history before the active sketch and project visible solid faces/edges into its drawing frame. Cache by model identity and active ID. **Output:** tuple: Projected 2D triangles and boundary edges, or two empty lists with no active feature. |
| [`FeaturePartEditor.sketch_context_points()`](../../src/feature_editor.py#L791) | Flatten projected solid context triangles for sketch framing. **Output:** list: 2D points in metres in the active sketch frame. |
| [`FeaturePartEditor.open_path(path)`](../../src/feature_editor.py#L843) | Load/migrate a JSON part into feature history, replacing editor state only after successful loading. **Output:** bool: True on success; False after displaying a load error. |
| [`FeaturePartEditor._save_to(path)`](../../src/feature_editor.py#L872) | Save current version-3 history and update the path and clean state only on success. **Output:** bool: True when saved; False after displaying a save error. |
| [`FeaturePartEditor.export_mesh(kind)`](../../src/feature_editor.py#L891) | Prompt for a destination and export the built solid as OBJ or STL without changing document save state. **Output:** bool: True when exported; False for no solid, cancellation, or reported failure. |

## Existing checks

[test_feature_parts.py](../../Testing/Developer_Tests/test_feature_parts.py), [test_sketch_context.py](../../Testing/Developer_Tests/test_sketch_context.py), [test_sketch_deletion.py](../../Testing/Developer_Tests/test_sketch_deletion.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[feature_editor](../Frontend/feature_editor.md), [feature_geometry](feature_geometry.md), [feature_document](feature_document.md), [part_editor](part_editor.md), [part_export](part_export.md).
