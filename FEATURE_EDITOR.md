# 3D part editor: planes, faces and extrusions

The startup screen's **New Part** / **Open Part** options now open the 3D
feature editor. Direct launch also works:

```bash
./run.sh --part-editor
./run.sh Assets/feature_demo.simuOPart
```

The example has a base sketched on Top Plane and a second extrusion sketched on
its upper face. Existing JSON boxes and version-2 sketch parts open in 3D,
migrated in memory to a base feature. The source is only rewritten if you save.
Legacy OBJ parts have no editable feature history and cannot be edited here.

## Workflow

1. Select **Front Plane**, **Right Plane**, or **Top Plane** in the feature tree.
   Visible reference-plane patches can also be selected directly in 3D.
2. Choose **New Sketch**. The editor switches to a view normal to that plane.
   Draw connected lines (or use the existing arc tool), close the outline, and
   add dimensions with the existing sketch controls. Lengths use millimeters.
3. Choose **Finish Sketch**, then **Extrude**. Enter a distance. Reverse and
   symmetric options are available. The solid appears in the 3D viewport.
4. Click a flat face on the solid, or select it under **Solid faces** in the tree.
   Choose **New Sketch** to draw a new profile on that face. Its boundary is
   shown as a dashed reference while sketching. Finish and extrude to add a boss.
5. To extend a whole flat face without drawing another profile, select it and
   choose **Extrude** directly. This creates an editable face-extrusion feature.

Every extrusion adds material and joins the existing body. Detached additions
are rejected with an explanatory message. **Features** in the menu bar contains
the same commands as the top toolbar, including commands hidden by a narrow
window's toolbar overflow. **3D View** returns to the model at any time.

## Delete sketch geometry and features

To reshape a sketch, choose **Select line** and drag an endpoint. Free points
follow the pointer; explicit dimensions and geometric relations limit motion.
Other endpoints stay fixed. Esc cancels; Ctrl+Z undoes the complete drag. Changes
to an extruded sketch are rebuilt on release; an invalid feature rebuild keeps
the original model.

Sketch relations are available in **Constraints** and the properties panel:
select straight lines for **Horizontal** or **Vertical**, or Ctrl-click two or
more for **Equal**. The Constraints list also contains length/radius dimensions.
Select an entry and use **Delete selected constraint**, its context menu, or
Delete/Backspace while the list is focused to remove the rule and keep the
geometry. Undo/redo and saved feature parts retain these relations.

Select a line or arc in the sketch canvas or line table and press **Backspace**
or **Delete**. Deleting an edge from a closed outline opens it without moving
the remaining geometry. Deleting the middle edge of an open outline keeps both
sections as separate draft sketches. Remaining arc shapes and dimensions are
preserved. Removing a segment from an extruded sketch requires confirmation
because its extrusion and face-dependent sketches must also be removed.

Select a sketch or extrusion in the feature tree, then choose **Features →
Delete Sketch…** or **Delete Extrusion…**. Backspace/Delete or the tree's
right-click delete command removes the selected node as well. Removing an
extrusion keeps its original sketch; removing a sketch removes its extrusion.
The confirmation lists sketches attached to affected faces before deleting
them. Reference planes cannot be deleted. Invalid remaining feature chains
are rejected without changing the document.

**Ctrl+Z / Ctrl+Shift+Z** undo and redo deletion. Backspace in a name or numeric
field continues to edit that field rather than deleting sketch geometry.

Drag in 3D to orbit, middle-drag to pan, and use the wheel to zoom. The arrow
keys turn the view. **F** frames the current 3D model or the current 2D sketch.
In the sketch view, the marked **Origin (0, 0)** is a snap target. Press **O**
or use **View → Center sketch origin** to center it without changing geometry.
Existing endpoints snap to their exact coordinates before grid rounding; a
yellow marker and “locked” label show the active target. Snapping uses screen
distance at every zoom and holds gently to prevent jitter, while allowing a
nearby endpoint directly under the cursor to take over. Open arc previews are
outline-only; closed profiles retain their intentional face shading.
The Front plane is XY (+Z normal), Right is YZ (+X normal), and Top is XZ (+Y
normal); the basis orientation is preserved in the saved features.

Double-click a sketch in the tree to edit it. Select its extrusion and choose
Extrude to change its distance. To edit an existing extrusion, first select its
feature in the tree so a separately selected model face is no longer active.
Undo/redo includes sketch creation, dimensions and extrusion operations. Save
retains all sketches, their supports and their extrusion distances. Drafts can
be saved; scene import/export requires at least one completed extrusion.

The properties panel supplies dimensions and the **Next extrusion** distance.
The extrusion dialog is the control that changes the solid's actual depth.
Properties and feature-tree docks can be shown through View. The properties
dock hides automatically in narrow/tiled windows to preserve sketch space.

## Geometry and persistence

JSON version 3 stores `geometry.type = "feature_part"` and an ordered `features`
list. Each feature retains a stable ID, name, complete editable sketch, support,
signed extrusion depth (or null for an unextruded sketch), and symmetric flag.
Reference supports identify Front/Right/Top. Face supports retain a parent
extrusion ID and an orthonormal local frame. Distances remain SI meters on disk.

The solid is rebuilt from those features using
[Manifold](https://github.com/elalish/manifold). Additions are Boolean unions,
so internal faces and overlapping volume are not counted twice. The display
and export mesh contains the entire joined body. Face supports retain kernel
double precision independently of float32 GPU buffers. Outward face additions
overlap inward by a tiny scale-dependent tolerance to avoid one-ULP gaps while
keeping the requested outward end. Zero-area triangles collapsed by float32
conversion are excluded from display/export data.

`feature_geometry.py` builds solids and connected planar faces;
`feature_document.py` handles migration and atomic saves; `part_viewport.py`
provides 3D viewing and ray-based face/plane selection; `feature_editor.py`
extends the reusable 2D sketch editor. The startup launcher now opens this
feature editor. The earlier `PartEditor` class remains as the underlying sketch
UI and supports the existing line/arc regression tests.

Version-1 and version-2 files still load in scenes. New feature parts also load
in the main OpenGL editor, physics Render and OBJ/STL export. Density-derived
mass uses the joined solid's volume. As with the earlier arbitrary sketch
meshes, dynamic physics uses a convex hull and approximate inertia; concave
visual geometry is not an exact dynamic collider. Static physics uses the actual
triangle mesh.

## Current limits

- Additive extrusions of one connected solid, up to 64 sketches. Cuts, fillets,
  assemblies, lofts and analytic curved-face supports are not implemented.
- Whole-face extrusion requires one boundary loop. If a face surrounds a boss
  and contains a hole, create a new sketch on it instead of pulling that whole
  face. Concave single-loop sketch outlines can still be extruded.
- Face sketches retain their chosen placement. If an upstream change removes
  or moves the supporting plane, the rebuild is rejected and the prior model
  stays intact. Automatic face-reference repair is not implemented; create a
  new sketch on the updated face. Face labels are descriptive, while stored
  frames and parent feature IDs carry the support information.
- Curves are tessellated using the existing arc implementation. Numerical
  tolerances and rendering precision make this an introductory part modeler,
  rather than an engineering-grade CAD kernel/constraint workflow.

## Validation on this device

The final automated snapshot ran **138 tests: 137 passed and one Windows-only
test was skipped** on this Linux device. The real desktop workflow also passes.
The feature-specific
checks cover all three plane orientations; cap and side-face sketches; joined
and overlapping additions; reverse/symmetric extrusions; direct face pulls;
holes and detached-body errors; stale support rejection; manifold edge counts;
exact volume/mass accounting within tolerance; migration; draft and feature-file
roundtrips; export; undo/redo; picking; save/open failures; and physics import.

`tests/gui_feature_editor.py` passed on the actual desktop: real tree selection
of Top Plane, mouse sketching, the Extrude dialog, a ray-picked face, a dimensioned
sketch on that face, a joined boss, a direct pull of its top face, undo/redo,
v3 save/reopen, main-scene OpenGL upload and live physics Render. The final test
includes the repeated-extrusion precision regression. Screenshots
`/tmp/simuo-features-editor.png` and `/tmp/simuo-features-viewport.png` were inspected.
The earlier failed run exposed that precision issue and was corrected before
the passing rerun.

Run:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tests/gui_feature_editor.py
```

Manifold 3.5.4 is installed in the project's `.venv` and pinned in
`src/requirements.txt`. Other environments need the updated project requirements.
No packaged executables were rebuilt. Concurrent arc, export and plane-picking
assistance was preserved; coordination is recorded in IMPLEMENTATION_NOTES.md.
