# part_editor.py: frontend guide

Source: [src/part_editor.py](../../src/part_editor.py). [Documentation index](../README.md).

The base sketch-editor UI, constraint list, and 2D drawing canvas reused by the current feature-based Part Editor.

This file serves both layers. See the [backend companion](../Backend/part_editor.md) for its other responsibilities.

## How it works

`SketchCanvas` translates pointer events into line, three-point arc, circle, selection, pan/zoom, and constrained endpoint-drag interactions. It draws geometry, context, dimensions, relation markers, and snap previews using `QPainter`.

`PartEditor` owns sketch controls/actions and forwards edits through candidate commits. `run_part_editor()` actually opens `FeaturePartEditor`, which extends this base with the feature tree and 3D view.

## Contracts and editing considerations

- UI lengths/radii/thickness use millimetres; model coordinates use metres. Arcs dimension by radius.
- Drawing snaps to endpoints, visible context corners/edges, grid, and axis hints. Snap capture/release tolerances are in pixels to remain usable across zoom levels.
- In selection mode, endpoint dragging previews a candidate; release produces one undo step, while Escape restores the original.
- Ctrl-selection supports equal-line relations. Focus determines whether Delete removes a geometric segment or a selected constraint entry.
- Signals report selected segments, requested dimensions, and drawing errors. Dimension-label locations also support hit testing.
- The properties dock hides automatically below 800 logical pixels and is restored only when its hiding was automatic.
- Sketch state transactions and file operations are in the backend companion.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`ConstraintList.keyPressEvent(event)`](../../src/part_editor.py#L21) | Emit delete_requested for unmodified Delete/Backspace; delegate other keys to the list widget. **Output:** None. Accepts handled key events. |
| [`SketchCanvas.__init__(editor)`](../../src/part_editor.py#L45) | Create a sketch canvas with drawing, selection, snapping, drag, and pan state linked to its editor. **Output:** None. |
| [`SketchCanvas.screen(p)`](../../src/part_editor.py#L79) | Convert sketch XY metres to canvas pixels using zoom and an inverted screen Y axis. **Output:** QPointF: Widget-local pixel coordinates. |
| [`SketchCanvas.world(p)`](../../src/part_editor.py#L91) | Convert a screen position to sketch coordinates with endpoint/edge snapping, 1 mm grid rounding, and drawing-axis hints. **Output:** list: XY metres; also updates snap target and hysteresis lock state. |
| [`SketchCanvas.center_origin()`](../../src/part_editor.py#L168) | Center the sketch origin in the widget and clear snapping locks. **Output:** None. Schedules a repaint without moving geometry. |
| [`SketchCanvas.hit(p)`](../../src/part_editor.py#L178) | Hit-test dimension labels, straight segments, and analytic arcs within screen- space tolerances. **Output:** int: Nearest segment index, or -1 if nothing is close enough. |
| [`SketchCanvas.segment_path(index)`](../../src/part_editor.py#L216) | Construct a screen-space painter path for a straight segment or analytic circular arc. **Output:** QPainterPath: Segment path using current pan and zoom. |
| [`SketchCanvas.mousePressEvent(event)`](../../src/part_editor.py#L240) | Start panning/endpoint dragging, select segments, or add line/arc/circle geometry according to the active tool. **Output:** None. Commits valid candidates through the editor and emits selection/error signals as needed. |
| [`SketchCanvas.mouseDoubleClickEvent(event)`](../../src/part_editor.py#L319) | Request a dimension editor for a hit segment when drawing is inactive or the outline is closed. **Output:** None. Emits dimension_requested with the segment index when applicable. |
| [`SketchCanvas.mouseMoveEvent(event)`](../../src/part_editor.py#L334) | Preview a constrained endpoint drag or update panning, snapped cursor position, and drawing preview. **Output:** None. Repaints; drag previews are committed only on mouse release. |
| [`SketchCanvas.mouseReleaseEvent(event)`](../../src/part_editor.py#L363) | Commit one valid endpoint-drag edit on left release, or finish middle-button panning. **Output:** None. Restores the original before committing so the drag produces one undo step. |
| [`SketchCanvas.leaveEvent(event)`](../../src/part_editor.py#L390) | Clear cursor/snapping preview when the pointer leaves the canvas and delegate the event. **Output:** None. Schedules a repaint. |
| [`SketchCanvas.wheelEvent(event)`](../../src/part_editor.py#L406) | Zoom around the pointer while keeping the underlying screen location stable. **Output:** None. Updates zoom/origin within supported limits and repaints. |
| [`SketchCanvas.keyPressEvent(event)`](../../src/part_editor.py#L422) | Cancel an endpoint drag or leave drawing mode on Escape; delegate other keys. **Output:** None. Restores uncommitted drag geometry when cancelled. |
| [`SketchCanvas.fit()`](../../src/part_editor.py#L443) | Fit the outline and optional projected solid context into the canvas with a margin. **Output:** None. Updates zoom and origin, then repaints. |
| [`SketchCanvas.paintEvent(event)`](../../src/part_editor.py#L462) | Draw grid, context, outline, dimensions, relations, endpoints, snapping markers, and tool previews. **Output:** None. Paints the canvas and refreshes dimension-label hit-test positions. |
| [`PartEditor.__init__(path=None)`](../../src/part_editor.py#L585) | Build the sketch editor, default draft, property controls, actions, and undo stacks; optionally load a document. **Output:** None. |
| [`PartEditor.make_actions()`](../../src/part_editor.py#L708) | Create file/edit/view/help menus, sketch tools, constraint actions, and keyboard shortcuts. **Output:** None. Connects UI actions to editor callbacks. |
| [`PartEditor.resizeEvent(event)`](../../src/part_editor.py#L811) | Hide properties automatically below 800 pixels and restore them when space returns. **Output:** None. Delegates resize handling and tracks whether hiding was automatic. |
| [`PartEditor.show_controls()`](../../src/part_editor.py#L832) | Display the sketch editor's drawing, dimensioning, constraints, export, and navigation help. **Output:** None. Opens an informational dialog. |
| [`PartEditor.set_drawing(value)`](../../src/part_editor.py#L854) | Toggle straight-line drawing and clear incompatible arc/circle modes and previews. **Output:** None. Updates canvas state and schedules a repaint. |
| [`PartEditor.set_arcs(value)`](../../src/part_editor.py#L876) | Toggle three-point arc drawing and clear incompatible modes and pending curve points. **Output:** None. Updates action checks and canvas state. |
| [`PartEditor.set_circles(value)`](../../src/part_editor.py#L897) | Toggle circle drawing and clear incompatible modes and previews. **Output:** None. Updates actions, canvas state, and enabled-tool guidance. |
| [`PartEditor.select_mode()`](../../src/part_editor.py#L919) | Disable all drawing tools and discard pending curve preview points. **Output:** None. Leaves geometry unchanged and schedules a repaint. |
| [`PartEditor.refresh()`](../../src/part_editor.py#L981) | Synchronize title, segment table, dimensions, thickness, constraints, summary, and canvas with the current sketch. **Output:** None. Blocks control signals while populating values to avoid recursive edits. |
| [`PartEditor.select_line(index, sync_table=True)`](../../src/part_editor.py#L1010) | Select an edge and configure its line-length or arc-radius controls, optionally synchronizing the table row. **Output:** None. Invalid indices clear the canvas selection and disable dimension controls. |
| [`PartEditor.selected_segments()`](../../src/part_editor.py#L1046) | Collect selected table rows, falling back to the canvas selection. **Output:** list: Sorted valid segment indices, or an empty list. |
| [`PartEditor.on_segment_selection_changed()`](../../src/part_editor.py#L1060) | Synchronize the active canvas edge and dimension controls with table selection. **Output:** None. Keeps multiple selected rows intact. |
| [`PartEditor.select_segments(indices)`](../../src/part_editor.py#L1070) | Replace table/canvas selection with the supplied valid edge indices. **Output:** None. Selects rows while blocking recursive selection signals. |
| [`PartEditor.toggle_segment_selection(index)`](../../src/part_editor.py#L1091) | Toggle one edge in the current table multi-selection. **Output:** None. Updates the table and canvas through select_segments. |
| [`PartEditor.apply_geometric_constraint(kind)`](../../src/part_editor.py#L1106) | Add a relation to selected edges on a copy, then commit a solved sketch. **Output:** None. Displays duplicate guidance or a warning on conflicts without committing invalid geometry. |
| [`PartEditor.refresh_constraints()`](../../src/part_editor.py#L1125) | Rebuild the constraints list from geometric relations and driving dimensions, preserving a matching selection. **Output:** None. Updates list contents and deletion-button availability. |
| [`PartEditor.select_constraint(item, previous=None)`](../../src/part_editor.py#L1154) | Highlight the segments affected by the selected relation or dimension entry. **Output:** None. Enables deletion when a constraint item exists. |
| [`PartEditor.delete_selected_constraint()`](../../src/part_editor.py#L1173) | Remove the selected relation or driving dimension on a copy without deleting geometry. **Output:** None. Commits a valid sketch or displays an error/guidance. |
| [`PartEditor.apply_dimension()`](../../src/part_editor.py#L1195) | Convert the selected dimension control from millimetres to metres and apply it through a candidate sketch. **Output:** None. Commits valid geometry or displays a dimension error. |
| [`PartEditor.dimension_dialog(index)`](../../src/part_editor.py#L1209) | Prompt for a selected segment's line length or arc radius in millimetres and apply an accepted value. **Output:** None. Cancelling leaves the geometry unchanged. |
| [`PartEditor.clear_dimension()`](../../src/part_editor.py#L1231) | Remove the selected edge's driving dimension while preserving its current geometry. **Output:** None. Commits only when a dimension exists. |
| [`PartEditor.delete_selected_segment()`](../../src/part_editor.py#L1243) | Remove the selected edge while retaining one outline; reject edits that split into multiple sketches in this base editor. **Output:** None. Commits the deletion or displays guidance; the feature editor supports split outlines. |
| [`PartEditor.close_face()`](../../src/part_editor.py#L1262) | Validate and close the current outline through a sketch candidate. **Output:** None. Commits valid closure or displays an error. |
| [`PartEditor.change_name(value)`](../../src/part_editor.py#L1275) | Update the document's name, mark it dirty, and refresh the window title. **Output:** None. Does not validate the name until saving. |
| [`PartEditor.change_thickness(value)`](../../src/part_editor.py#L1288) | Convert the thickness control's millimetres to metres and commit an edited sketch. **Output:** None. Updates history and dirty state through commit. |
| [`PartEditor.confirm_changes()`](../../src/part_editor.py#L1303) | Protect dirty documents with Save/Discard/Cancel before replacing or closing them. **Output:** bool: True if clean, discarded, or successfully saved; False on cancellation/save failure. |
| [`PartEditor.new_scene()`](../../src/part_editor.py#L1316) | Open an independent empty scene editor and retain a reference to its window. **Output:** None. Leaves the current part open. |
| [`PartEditor.new_part()`](../../src/part_editor.py#L1328) | Protect unsaved changes, then reset the base editor to a new empty sketch document. **Output:** None. Clears path, history, selection, and dirty state after confirmation. |
| [`PartEditor.open_part()`](../../src/part_editor.py#L1346) | Prompt for a part file and open it after protecting unsaved changes. **Output:** None. Cancellation preserves the current document. |
| [`PartEditor.closeEvent(event)`](../../src/part_editor.py#L1465) | Protect unsaved work before accepting or ignoring the window-close event. **Output:** None. Controls closure through the event object. |
| [`run_part_editor(path=None)`](../../src/part_editor.py#L1478) | Create/show the current feature-based editor, reuse or create QApplication, and enter the Qt event loop. **Output:** int: Qt event-loop exit code after the editor application finishes. |

## Existing checks

[test_arcs.py](../../Testing/Developer_Tests/test_arcs.py), [test_circles.py](../../Testing/Developer_Tests/test_circles.py), [test_point_dragging.py](../../Testing/Developer_Tests/test_point_dragging.py), [test_sketch_snapping.py](../../Testing/Developer_Tests/test_sketch_snapping.py), [test_edge_snapping.py](../../Testing/Developer_Tests/test_edge_snapping.py), [test_sketch_constraints.py](../../Testing/Developer_Tests/test_sketch_constraints.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[part_editor](../Backend/part_editor.md), [feature_editor](feature_editor.md), [part_viewport](part_viewport.md), [sketch_geometry](../Backend/sketch_geometry.md).
