# feature_editor.py: frontend guide

Source: [src/feature_editor.py](../../src/feature_editor.py). [Documentation index](../README.md).

The current Part Editor window: a feature tree plus switchable 3D model preview and 2D sketch workspace.

This file serves both layers. See the [backend companion](../Backend/feature_editor.md) for its other responsibilities.

## How it works

The constructor extends `PartEditor`, installs a `PartViewport` and hierarchy dock, and adds Features actions. Reference planes, sketch/extrusion history, and solid faces appear in the tree. Selecting a plane/face establishes support; New Sketch enters drawing; Finish Sketch returns to the model; Extrude opens the distance/direction/symmetry dialog.

Selection is synchronized across tree and viewport. Deletion commands show dependent-feature warnings before accepting a candidate edit.

## Contracts and editing considerations

- Tree user data distinguishes plane, face, feature, and extrusion rows. Double-clicking a feature edits its sketch; double-clicking a support creates a sketch.
- Extrusion UI uses millimetres and converts to signed metres. Reverse direction changes sign; symmetry centers about the sketch plane.
- Drawing actions ensure a valid sketch exists; circle mode creates a new empty sketch when needed.
- `frame_view()` fits the active canvas or 3D viewport. Projected context is painted behind sketches and supplies snap targets.
- Delete Sketch removes its extrusion and dependent sketches. Delete Extrusion keeps its sketch and removes face dependents. Segment deletion may split into separate open sketches.
- Model transactions and persistence are documented in the backend companion.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`FeaturePartEditor.__init__(path=None)`](../../src/feature_editor.py#L21) | Build the feature-tree editor with 3D and sketch views, optionally opening a part document. **Output:** None. |
| [`FeaturePartEditor.refresh(rebuild=True)`](../../src/feature_editor.py#L166) | Refresh inherited sketch controls, 3D model references, summary, and optionally the feature tree. **Output:** None. Updates UI state without building new geometry. |
| [`FeaturePartEditor.rebuild_tree()`](../../src/feature_editor.py#L200) | Repopulate reference planes, sketches/extrusions, and selectable faces while blocking selection signals. **Output:** None. Replaces tree items and restores the active feature selection. |
| [`FeaturePartEditor.tree_clicked(item, column=0)`](../../src/feature_editor.py#L232) | Select the plane, face, or feature described by a tree item's stored role data. **Output:** None. Updates active sketch/support and refreshes controls. |
| [`FeaturePartEditor.tree_double_clicked(item, column=0)`](../../src/feature_editor.py#L260) | Open a feature's sketch for editing, or create a sketch on a selected plane/face. **Output:** None. Switches views and may create feature history. |
| [`FeaturePartEditor.select_plane(name)`](../../src/feature_editor.py#L280) | Select a named reference plane in the hierarchy and switch to the model view. **Output:** None. Updates support and status text if the plane is found. |
| [`FeaturePartEditor.select_face(index)`](../../src/feature_editor.py#L300) | Select a valid built planar face as the support for a new sketch. **Output:** None. Synchronizes viewport highlight, tree selection, and support; invalid indices are ignored. |
| [`FeaturePartEditor.new_sketch()`](../../src/feature_editor.py#L322) | Create a sketch on the selected support via a candidate model and enter sketch editing. **Output:** None. Records undo on success; shows a warning for invalid supports or rebuild failures. |
| [`FeaturePartEditor.edit_sketch()`](../../src/feature_editor.py#L339) | Bind the active sketch, show the 2D canvas, and fit its geometry; create a sketch first if needed. **Output:** None. |
| [`FeaturePartEditor.finish_sketch()`](../../src/feature_editor.py#L355) | Leave drawing mode, show the 3D model, and frame its geometry. **Output:** None. Does not implicitly extrude the sketch. |
| [`FeaturePartEditor.view_model()`](../../src/feature_editor.py#L365) | Leave drawing mode and display the 3D viewport. **Output:** None. Schedules a viewport repaint. |
| [`FeaturePartEditor.frame_view()`](../../src/feature_editor.py#L375) | Fit whichever viewport is currently displayed, including sketch context when applicable. **Output:** None. Changes camera or canvas framing only. |
| [`FeaturePartEditor.set_drawing(value)`](../../src/feature_editor.py#L384) | Toggle straight-line drawing and show or create an editable sketch when enabling it. **Output:** None. Updates drawing actions and the active view. |
| [`FeaturePartEditor.set_arcs(value)`](../../src/feature_editor.py#L402) | Toggle arc drawing and ensure a sketch canvas is available when enabled. **Output:** None. Updates drawing actions and may create a new sketch. |
| [`FeaturePartEditor.set_circles(value)`](../../src/feature_editor.py#L420) | Toggle circle drawing, creating an empty sketch when the active sketch already has geometry. **Output:** None. Updates drawing actions and active view. |
| [`FeaturePartEditor.change_thickness(value)`](../../src/feature_editor.py#L462) | Convert the control's millimetres to the active sketch's stored thickness and report the next extrusion distance. **Output:** None. Commits an edited sketch when one is active. |
| [`FeaturePartEditor.confirm_feature_deletion(message, dependent)`](../../src/feature_editor.py#L497) | Ask whether to delete a feature, listing dependent sketches that will also be removed. **Output:** bool: True only when the user confirms deletion. |
| [`FeaturePartEditor.delete_selected_segment()`](../../src/feature_editor.py#L540) | Remove the selected sketch edge, split surviving outlines when needed, and remove affected extrusion/dependent features after confirmation. **Output:** None. Commits a valid deletion or displays an error; cancellation preserves the model. |
| [`FeaturePartEditor.selected_tree_feature()`](../../src/feature_editor.py#L573) | Resolve the selected sketch or extrusion row to its model feature. **Output:** dict or None: Selected feature; shows selection guidance when absent. |
| [`FeaturePartEditor.delete_tree_item()`](../../src/feature_editor.py#L586) | Dispatch feature-tree deletion to sketch or extrusion removal based on the current row. **Output:** None. Non-feature rows are ignored. |
| [`FeaturePartEditor.delete_sketch()`](../../src/feature_editor.py#L600) | Confirm and remove a sketch, its extrusion, and face-dependent descendants through a rebuilt candidate. **Output:** None. Records undo on success; warnings report rebuild failures. |
| [`FeaturePartEditor.delete_extrusion()`](../../src/feature_editor.py#L622) | Confirm and remove an extrusion and its dependents while retaining its sketch. **Output:** None. Commits a valid candidate, or preserves the model on cancellation/failure. |
| [`FeaturePartEditor.extrude_dialog()`](../../src/feature_editor.py#L694) | Collect extrusion distance, reverse direction, and symmetry, then extrude the selected face or active sketch. **Output:** None. Converts millimetres to metres and displays build errors without committing invalid geometry. |
| [`FeaturePartEditor.undo()`](../../src/feature_editor.py#L736) | Restore the previous feature-model snapshot and move the current snapshot to redo history. **Output:** None. Marks the document dirty; no change when undo history is empty. |
| [`FeaturePartEditor.redo()`](../../src/feature_editor.py#L749) | Restore the next feature-model snapshot and save the current snapshot in undo history. **Output:** None. Marks the document dirty; no change when redo history is empty. |
| [`FeaturePartEditor.paint_sketch_context(painter, canvas)`](../../src/feature_editor.py#L800) | Paint projected solid faces and boundaries behind the active sketch while preserving painter state. **Output:** None. Draws into the supplied painter. |
| [`FeaturePartEditor.new_part()`](../../src/feature_editor.py#L822) | Protect unsaved changes, then reset to an empty feature document with Front plane selected. **Output:** None. Clears file path, history, selections, and dirty state after confirmation. |
| [`FeaturePartEditor.show_controls()`](../../src/feature_editor.py#L920) | Display the feature editor's sketching, extrusion, selection, and navigation guidance. **Output:** None. Opens an informational dialog. |

## Existing checks

[test_feature_parts.py](../../Testing/Developer_Tests/test_feature_parts.py), [test_sketch_deletion.py](../../Testing/Developer_Tests/test_sketch_deletion.py), [test_sketch_context.py](../../Testing/Developer_Tests/test_sketch_context.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[feature_editor](../Backend/feature_editor.md), [part_editor](part_editor.md), [part_viewport](part_viewport.md), [feature_geometry](../Backend/feature_geometry.md).
