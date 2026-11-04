# part_editor.py: backend guide

Source: [src/part_editor.py](../../src/part_editor.py). [Documentation index](../README.md).

The base sketch editor's candidate-commit, undo/redo, file persistence, and mesh export integration.

This file serves both layers. See the [frontend companion](../Frontend/part_editor.md) for its other responsibilities.

## How it works

`commit(candidate)` validates before replacing the working sketch, preserves undo history, clears redo, marks dirty, and refreshes controls. Undo/redo move independent sketches between history stacks.

`open_path()` loads data before replacing active editor state. `_save_to()` writes through `save_document()` and only then updates path/data/clean state. `save()` and `save_as()` select the destination. `export_mesh()` exports a closed sketch without taking over the document's save path or clearing dirty state.

## Contracts and editing considerations

- These methods belong to a Qt editor and may refresh controls or show dialogs. Use `part_document`, `sketch_geometry`, and `part_export` for direct headless operations.
- The base editor uses version-2 sketches. Current startup opens `FeaturePartEditor`, whose overrides persist v3 feature history.
- Open sketches can be saved as drafts. Mesh export requires a closed outline; feature-editor export instead requires a built solid.
- Save/open failures preserve existing path/document state where handled. Save/Discard/Cancel decisions are made by the frontend's `confirm_changes()`.
- Backend updates should pass independently edited candidates; changing the active sketch directly bypasses undo and validation boundaries.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`PartEditor.commit(candidate)`](../../src/part_editor.py#L933) | Validate a sketch candidate before replacing the working sketch and recording undo history. **Output:** None. Clears redo, marks dirty, and refreshes controls; invalid candidates raise ValueError. |
| [`PartEditor.undo()`](../../src/part_editor.py#L953) | Restore the previous sketch and move the current one to redo history. **Output:** None. Updates drawing mode and dirty state if undo history exists. |
| [`PartEditor.redo()`](../../src/part_editor.py#L967) | Restore a redo sketch and preserve the current one in undo history. **Output:** None. Updates drawing mode and dirty state if redo history exists. |
| [`PartEditor.open_path(path)`](../../src/part_editor.py#L1356) | Load an editable document before replacing sketch/editor state and framing its geometry. **Output:** bool: True when loaded; False after a warning if loading fails. |
| [`PartEditor.save()`](../../src/part_editor.py#L1383) | Save to the current path, or prompt for a path when the document has never been saved. **Output:** bool: True on successful save; False on cancellation or failure. |
| [`PartEditor.export_mesh(kind)`](../../src/part_editor.py#L1392) | Prompt for an OBJ/STL destination and export a closed sketch without changing the editable document's path or dirty state. **Output:** bool: True when exported; False for an open sketch, cancellation, or reported failure. |
| [`PartEditor.save_as()`](../../src/part_editor.py#L1428) | Prompt for a .simuOPart destination, confirm extension-adjusted overwrites, and save. **Output:** bool: True when saved; False on cancellation or failure. |
| [`PartEditor._save_to(path)`](../../src/part_editor.py#L1445) | Write a validated sketch document and only then update the editor's path and clean state. **Output:** bool: True on success; False after displaying a save error. |

## Existing checks

[test_sketch_parts.py](../../Testing/Developer_Tests/test_sketch_parts.py), [test_part_exports.py](../../Testing/Developer_Tests/test_part_exports.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[part_editor](../Frontend/part_editor.md), [feature_editor](feature_editor.md), [part_document](part_document.md), [part_export](part_export.md), [sketch_geometry](sketch_geometry.md).
