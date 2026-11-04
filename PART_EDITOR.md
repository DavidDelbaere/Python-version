# SimuO Part Editor

**3D editor update:** startup now opens an orbitable model view with a hierarchy
of Front/Right/Top planes, selectable flat faces, multiple sketches and additive
extrusions. Use **New Sketch → Finish Sketch → Extrude** to build a solid, or
select a flat face and Extrude it directly. See [FEATURE_EDITOR.md](FEATURE_EDITOR.md)
for the current workflow and v3 format. The earlier v2 sketch details below
remain useful for dimensions and backward compatibility; closing an outline
alone no longer implicitly creates a solid in the new editor.

The opening screen has **New Part** and **Open Part…** buttons below the scene
options. They open a dedicated part editor rather than a scene. You can also
launch it from a terminal:

```bash
./run.sh --part-editor
./run.sh Assets/sketch_plate.simuOPart
```

`Assets/sketch_plate.simuOPart` is an editable 100 × 60 mm example with 10 mm
thickness. Existing JSON boxes open as rectangular sketches with their Z size
as thickness. Saving such a box writes the editable version-2 sketch format,
preserving its material, physical defaults, identity and custom metadata.
Legacy OBJ meshes have no editable sketch and produce an explanatory error.

## Sketch planes and faces

The feature editor opens in a 3D view with **Front**, **Right**, and **Top**
reference planes in the feature tree. Select a plane in the tree or click its
visible patch in the viewport. The selected plane is highlighted in orange.
Choose **New Sketch** to draw on it: Front uses XY, Right uses YZ, and Top uses
XZ. Curved draft outlines remain visible in 3D, and **Frame view** (F) includes
the whole curve.

After closing an outline, choose **Finish Sketch**, then **Extrude…** to add
material. To add a feature to an existing solid, click a flat face (or choose
one under **Solid faces**) and choose **New Sketch**. To extend a complete
existing face, select it and choose **Extrude…** directly. Orbit the model by
dragging, pan with the middle mouse button, and zoom with the wheel. A click
selects; dragging orbits without changing the selection.

Feature parts save as version 3, retaining each sketch's supporting plane or
face and extrusion history. Existing version-1 boxes and version-2 sketches
can be opened and migrated. The standalone sketch definition described below
remains the geometry used inside each feature.

## Draw and dimension

In **Select line** mode, drag an endpoint to move it. Unconstrained points move
freely, without drawing-grid snapping or implicit horizontal/vertical locks.
Other endpoints stay fixed. Explicit lengths, arc radii and Horizontal,
Vertical or Equal constraints remain active, so partly constrained points move
only in allowed directions. A fully constrained endpoint stays in place.
Moves that cross or collapse the outline are rejected. **Esc** cancels a drag;
releasing the mouse commits one **Undo** step. Saved part files retain the moved
coordinates and constraints.

Select a line or arc and press **Backspace** or **Delete** to remove it. In the
3D editor, use **Features → Delete Sketch… / Delete Extrusion…** for feature
removal. See [FEATURE_EDITOR.md](FEATURE_EDITOR.md) for dependent sketches,
splitting open outlines, confirmation and undo behavior.

1. Leave **Draw lines** active and click points in the XY workspace. Each click adds
   a connected straight line. Drawing snaps to a 1 mm grid and nearby horizontal
   or vertical alignment.
2. Click the first point, or choose **Close outline**, to enclose the outline. The
   enclosed face fills automatically. Crossed lines, collapsed edges, and zero
   area faces are rejected.
3. Dimensions are **manual**. Choose **Select line**, click an edge or its row
   in the line table, enter a length in millimeters, and click **Add dimension**.
   The toolbar's **Add dimension…** action or double-clicking a line also opens
   a length-entry dialog. Cancel leaves the line undimensioned.
4. Only segments you dimension show orange labels. Lines show length; arcs show
   **R** followed by radius in millimeters. Undimensioned segments
   show a dash in the table. Use **Update dimension** to edit a selected dimension.
   Changing a driving length resizes the sketch. Existing driving dimensions
   and horizontal/vertical relationships are retained. The first point is fixed.
   Conflicting dimensions show an error and leave the sketch unchanged. Use
   **Remove dimension** removes the label and constraint without resizing the
   line. Added dimensions are saved in the `.simuOPart` and restored on opening.
5. Set **Thickness** to create a solid when importing the part into a scene.
   Use **Save SimuO Part** (Ctrl+S), or **Save SimuO Part As…**, to save it.

**Undo/Redo** restores sketch geometry, dimensions and thickness. **Draw lines** can
be turned off (or Esc pressed) to select edges while a sketch is still open.
Pan with the middle mouse button, zoom with the wheel, and choose **Frame sketch** to
frame the sketch. File → New/Open/Close protects unsaved changes with
Save/Discard/Cancel. Cancelled or failed saves keep the current document.

Open outlines can be saved and reopened as drafts. Scene import requires a
closed face and gives a clear error for a draft. Import a completed part through
the scene editor's **Import Part**, then choose **Render** to simulate it.
Concurrent export work also provides File → Export → OBJ/STL for closed meshes.

### Circular arcs

Select **Draw arcs** and click three points: the start, a point on the curve,
and the end. If there is already an open outline, its last endpoint supplies
the start, so only the point on the curve and the end are needed. A dashed
preview follows the cursor. You can mix straight lines and arcs; click the
first outline point to close with an arc, or use **Close outline** for a straight
closing edge. Two arcs can form a complete circle. Esc cancels a pending arc
and switches to selection.

Choose **Select line**, click the arc or its table row, and use **Add dimension**.
The input is labeled **Arc radius** and the canvas label reads, for example,
**R 50 mm**. Updating a radius keeps the endpoints fixed and preserves the side
and minor/major branch of the curve. A radius smaller than half the endpoint
separation is impossible; an error leaves the sketch intact. Removing the
dimension removes the constraint and label while retaining the current curve.
`Assets/arc_plate.simuOPart` is an editable semicircular plate with an R50 dimension.

## Line constraints

Select a straight line in the sketch or segment table, then choose
**Constraints → Make horizontal** or **Make vertical**. The properties panel
offers the same buttons. Multiple selected straight lines can receive the same
orientation rule. Arcs continue to use radius dimensions; these line relations
do not apply to curves.

For **Equal**, Ctrl-click two or more straight lines on the canvas or in the
table, then choose **Constraints → Make equal**. The lines share a length:
adding or updating a driving length on one propagates to the others. Relation
markers are displayed near the affected lines: **H**, **V**, or matching **=N**
markers for an Equal group.

The **Constraints** list in the properties panel includes orientation/equality
relations and driving length/radius dimensions. Selecting an entry highlights
its affected segments. Use **Delete selected constraint**, its right-click
menu, or Delete/Backspace while the list is focused to remove the rule.
This preserves the current geometry. Deleting a length or radius entry also
removes its dimension label. Undo/redo restores both geometry and constraints.
Delete while the canvas or segment table is focused still deletes geometry.

Conflicting rules show an error and leave the sketch intact. For example,
remove a Horizontal rule before applying Vertical to the same line. Equal
lines cannot retain different fixed length dimensions. Deleting an edge drops
relations involving that edge and remaps surviving ones; equality across
outlines split into separate sketches is removed.

Constraints are retained in saved drafts, closed sketch parts and feature
parts. They apply to the current sketch on its own supporting plane.

## Format and integration

Version 2 uses `format: ".simuOPart"`, the same units, coordinates, identity,
appearance, material, physical defaults and metadata fields as version 1. Its
geometry is an editable sketch:

```json
{
  "type": "sketch",
  "points": [[0, 0], [0.1, 0], [0.1, 0.06], [0, 0.06]],
  "closed": true,
  "dimensions": [0.1, 0.06, null, null],
  "thickness": 0.01
}
```

All stored lengths are **meters**. UI values are **millimeters**. The points
list contains segment endpoints (the first point is not repeated). For a
closed sketch, dimensions contains one entry per edge including the final
closing edge; an open sketch has one fewer edge than points. Null means a
measured, unconstrained segment. Non-null entries are positive driving line lengths or arc radii and
must agree with the geometry. An empty draft has empty point/dimension lists.

Curved sketches add an optional `arcs` list with one entry per segment. A null
entry is straight; `{"bulge": b}` defines a circular arc, where
`b = tan(signed_sweep / 4)`. The signed sweep determines direction and can
describe either a minor or major arc. The endpoints and bulge preserve the
editable circle; its `dimensions` entry, if present, is its radius. Older
line-only files omit `arcs` and load as before. For example, a closed
semicircle and its straight diameter use:

```json
{
  "type": "sketch",
  "points": [[-0.05, 0], [0.05, 0]],
  "closed": true,
  "dimensions": [0.05, null],
  "thickness": 0.01,
  "arcs": [{"bulge": -1}, null]
}
```

An optional `constraints` list stores geometric relations using zero-based
segment indices. Horizontal and Vertical each reference one straight segment;
Equal references two or more. For example:

```json
"constraints": [
  {"type": "horizontal", "segments": [0]},
  {"type": "vertical", "segments": [1]},
  {"type": "equal", "segments": [0, 2]}
]
```

Length and radius constraints continue to use the `dimensions` list. Geometry
must satisfy every saved relation and dimension. Unknown or malformed relations
are rejected. Files without `constraints` remain compatible, and empty lists
are omitted when saving. The same definitions are stored inside v3 features.

The editor draws smooth circular arcs. Scene meshes, physical volume/centroid,
and OBJ/STL exports use tessellation with angular steps of at most 5 degrees;
these are approximations of the saved analytic curve. Outlines are limited to
4,096 tessellated boundary points. Changing straight-edge dimensions retains
existing driving arc radii when feasible, or reports a conflict.

`sketch_geometry.py` validates the outline, solves length constraints and
triangulates concave polygons using ear clipping. `part_document.py` handles
editable documents and atomic saves. `part_editor.py` supplies the Qt UI.
`part_format.py`, `part_assets.py` and `physics_world.py` integrate the new
format with existing scenes and the OpenGL/physics renderer. Production code
does not depend on the standalone experiment.

Imported geometry is extruded symmetrically along local Z and centered on the
outline's area centroid. Density-derived mass uses actual polygon area times
thickness, including concave outlines. Static parts use the actual triangle
mesh for collision. Dynamic parts use a **convex hull**, so concavities are
filled for collision, and Bullet estimates inertia. The reusable part's
`inertia` accessor currently estimates the sketch inertia using its bounding box;
it is not an exact concave-solid inertia tensor. Visual geometry remains concave.
The Properties dialog explains the dynamic collision approximation.

## Scope and validation

This sketch format supports one simple outline, at most 256 control points, straight
lines, circular arcs, driving edge lengths/radii, axis alignment, face creation and thickness. It
does not provide holes, arbitrary CAD assemblies,
angle constraints or a general constraint solver. Use clear dimension errors
to resolve conflicts. Numerical solver limits remain those of the existing
renderer and Bullet, rather than engineering-grade CAD precision guarantees.

Validation on this Linux device (2026-11-02): the final automated suite ran
82 tests, with 81 passing and one Windows-only test skipped on Linux,
including 12 sketch-specific checks for closure, driving dimensions,
transactional conflicts, concave/CW/collinear meshing, mesh volume/normals,
draft and closed-document roundtrips, mass and physics contact, legacy JSON
box conversion, UI dimension/undo/redo, cancelled/failed save and failed open.
One existing Windows-specific test is skipped on Linux.

`tests/gui_part_editor.py` passed on the actual desktop with approved access:
both startup routes; real mouse drawing and closure; dimension-button input;
File save/open; a valid OpenGL import; and live physics rendering of the saved
part. Screenshots `/tmp/simuo-part-editor.png` and
`/tmp/simuo-sketch-scene.png` were inspected. The initial desktop harness needed
an update because concurrent export work renamed Save to Save SimuO Part; the
final test selects the action by its shortcut. Each Tk startup check runs in
its own process to match real startup and avoid leftover Tk timer callbacks.

Run checks:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tests/gui_part_editor.py
```

No new dependencies were added for the sketch editor. Existing packaged
executables were not rebuilt.
