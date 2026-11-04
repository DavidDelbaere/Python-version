# sketch_geometry.py: backend guide

Source: [src/sketch_geometry.py](../../src/sketch_geometry.py). [Documentation index](../README.md).

The planar sketch model, constraint operations, curve tessellation, polygon triangulation, and extruded prism mesh generation.

## How it works

`Sketch` stores ordered endpoints, closure, per-edge driving dimensions, thickness, optional arc bulges, and explicit line relations. Editing operations generally validate a candidate before committing changed fields. `geometry()` serializes a copy; `from_geometry()` parses and validates one.

Closed outlines are triangulated by ear clipping. Arcs retain analytic bulges for editing but are sampled into segments of at most five degrees for area, centroid, triangulation, and mesh output. `prism_vertices()` builds outward-facing caps and walls.

## Contracts and editing considerations

- Sketch coordinates and thickness use metres. A dimension is line length or arc radius, never arc length. `length()` does return the full curved arc length.
- Arc bulge is `tan(signed_sweep / 4)`. Three-point construction rejects coincident or collinear points. Radius changes preserve side and minor/major branch where possible.
- Supported relations are horizontal, vertical, and equal on straight edges. `_solve()` uses iterative least squares; call it on a candidate if transactional behavior is required.
- Endpoint dragging solves only the dragged endpoint; other points stay fixed. Dimension edits can move other vertices while anchoring the first point.
- Limits include 256 control points, 4,096 tessellated boundary points, and 1,024 geometric relations. Self-intersections and zero-area closed faces are rejected.
- `triangles()` indices refer to `outline_points` when curves are tessellated. `prism_vertices()` returns flat float32 XYZ/normal data centered on the area centroid in XY and symmetric about Z=0.
- `without_segment()` returns independent open sketches, remapping surviving relations and removing invalid cross-section equality links. There is no general CAD solver or hole-outline support.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`radius_bulge(start, end, radius, previous)`](../../src/sketch_geometry.py#L11) | Compute arc bulge for a new radius while preserving the old side and minor/major branch with fixed endpoints. **Output:** float: Signed tan(sweep/4); an impossible radius raises ValueError. |
| [`three_point_bulge(start, through, end)`](../../src/sketch_geometry.py#L34) | Fit an arc through three distinct non-collinear planar points. **Output:** float: Signed tan(sweep/4) for the arc passing through the middle point; invalid points raise ValueError. |
| [`cross(a, b, c)`](../../src/sketch_geometry.py#L62) | Compute the signed 2D cross product of vectors AB and AC. **Output:** float: Twice the signed triangle area; positive for counterclockwise points. |
| [`intersects(a, b, c, d)`](../../src/sketch_geometry.py#L79) | Test whether two planar segments cross, touch, or overlap within tolerance. **Output:** bool: True if segments AB and CD intersect. |
| [`intersects.on(p, q, r)`](../../src/sketch_geometry.py#L96) | Test whether a point lies on a segment within the enclosing intersection tolerance. **Output:** bool: True if R is collinear with and inside segment PQ. |
| [`Sketch.circle(center, radius, thickness=0.01)`](../../src/sketch_geometry.py#L126) | Construct and validate an editable closed circle from two exact semicircular arcs. **Output:** Sketch: New circle with undimensioned arcs; invalid radius or coordinates raise ValueError. |
| [`Sketch.is_circle()`](../../src/sketch_geometry.py#L148) | Recognize the two-semicircle representation created for a circle. **Output:** bool: True for a closed two-point outline with two positive unit bulges. |
| [`Sketch.edges()`](../../src/sketch_geometry.py#L158) | Enumerate consecutive endpoint indices, adding the last-to-first edge for a closed outline. **Output:** list: Pairs of zero-based point indices. |
| [`Sketch.length(index)`](../../src/sketch_geometry.py#L167) | Measure a straight segment or the full curved length of an arc. **Output:** float: Segment length in metres, rather than the arc's driving radius. |
| [`Sketch.is_arc(index)`](../../src/sketch_geometry.py#L182) | Check whether an edge has a stored circular-arc definition. **Output:** bool: True when the segment has non-null arc data. |
| [`Sketch.arc_parameters(index)`](../../src/sketch_geometry.py#L193) | Recover an arc's circle and sweep from its endpoints and bulge. **Output:** tuple: Center [x, y] in metres, radius in metres, and signed sweep in radians. |
| [`Sketch.dimension_value(index)`](../../src/sketch_geometry.py#L210) | Measure the quantity used by a driving dimension. **Output:** float: Line length or arc radius, in metres. |
| [`Sketch.segment_points(index)`](../../src/sketch_geometry.py#L221) | Sample a segment, tessellating arcs at angular steps of at most five degrees. **Output:** list: XY point lists in metres, including both exact endpoints. |
| [`Sketch.outline_points()`](../../src/sketch_geometry.py#L242) | Collect the tessellated boundary in drawing order without repeating a closed outline's first point. **Output:** list: Independent XY coordinate lists in metres. |
| [`Sketch._polygon()`](../../src/sketch_geometry.py#L258) | Replace curves with sampled straight edges for area and triangulation calculations. **Output:** Sketch: Undimensioned polygon approximation retaining closure and thickness. |
| [`Sketch.signed_area()`](../../src/sketch_geometry.py#L268) | Compute oriented area, using a tessellated polygon for curves. **Output:** float: Signed square metres; positive for counterclockwise outlines and zero for drafts. |
| [`Sketch.centroid()`](../../src/sketch_geometry.py#L281) | Compute the polygon area centroid, approximating curves by tessellation. **Output:** tuple: XY centroid in metres, or (0, 0) for zero area. |
| [`Sketch.validate()`](../../src/sketch_geometry.py#L296) | Check coordinate limits, thickness, topology, dimensions, curves, and geometric relations without solving them. **Output:** None. Raises ValueError if geometry is malformed, self-intersecting, or violates a constraint. |
| [`Sketch._validate_constraints()`](../../src/sketch_geometry.py#L363) | Check relation structure, supported kinds, unique indices, and straight-edge references. **Output:** None. Raises ValueError for malformed or duplicate relations; does not solve geometry. |
| [`Sketch.add_constraint(kind, segments)`](../../src/sketch_geometry.py#L391) | Solve a new horizontal, vertical, or equal relation on a copy, then commit only a valid result. **Output:** bool: True if a relation was added, False if already present; conflicts raise ValueError without committing the candidate. |
| [`Sketch.remove_constraint(index)`](../../src/sketch_geometry.py#L432) | Remove one geometric relation without moving the outline. **Output:** None. Mutates constraints; an invalid index raises ValueError. |
| [`Sketch.add_point(point)`](../../src/sketch_geometry.py#L445) | Append an undimensioned straight segment to an open outline, committing only after validation. **Output:** None. Updates points and segment metadata; invalid geometry raises ValueError. |
| [`Sketch.without_segment(index)`](../../src/sketch_geometry.py#L467) | Remove an edge into independent open outlines, preserving surviving geometry and remapping constraints. **Output:** list: One or two validated Sketch objects, or an empty Sketch when no edges remain; this sketch is unchanged. |
| [`Sketch.add_arc(through, end, close=False)`](../../src/sketch_geometry.py#L507) | Append a three-point arc from the last endpoint, optionally closing at the first point. Commit only after validation. **Output:** None. Updates geometry and segment metadata; invalid arcs or closure raise ValueError. |
| [`Sketch.close()`](../../src/sketch_geometry.py#L537) | Close an open outline with an undimensioned straight edge after validation. **Output:** None. Updates closure and metadata; an already closed sketch is unchanged. |
| [`Sketch.set_dimension(index, length)`](../../src/sketch_geometry.py#L553) | Apply a driving line length or arc radius on a copy, solve affected geometry, and commit a valid result. A circle's radius edit resizes the whole circle. **Output:** None. Updates points, arcs, and/or dimensions; conflicts raise ValueError without committing the candidate. |
| [`Sketch.move_point(index, position)`](../../src/sketch_geometry.py#L590) | Move one endpoint while keeping other endpoints fixed and respecting explicit relations and dimensions. Commit only a validated solution. **Output:** None. Updates points and arcs when movement is possible; invalid positions or conflicts raise ValueError. |
| [`Sketch._solve(preserve_axes=True, orient=(), drag=None)`](../../src/sketch_geometry.py#L617) | Solve relations and dimensions in this candidate using iterative least squares. Call on a copy when transactional edits are required. **Output:** None. Mutates candidate points and driving arc bulges; unresolved constraints raise ValueError. |
| [`Sketch._solve.length_row(index)`](../../src/sketch_geometry.py#L653) | Form the current line length and its derivatives for the solver's working points. **Output:** tuple: Scalar length and flat Jacobian row; a collapsed edge raises ValueError. |
| [`Sketch.geometry()`](../../src/sketch_geometry.py#L729) | Serialize editable geometry, including optional curves and relations when present. **Output:** dict: Independent JSON-compatible sketch definition in metres. |
| [`Sketch.from_geometry(g)`](../../src/sketch_geometry.py#L745) | Validate a sketch envelope, copy its editable data, and check all geometry and constraints. **Output:** Sketch: Independent validated sketch; invalid input raises ValueError. |
| [`Sketch.triangles()`](../../src/sketch_geometry.py#L763) | Validate and triangulate a closed simple outline by ear clipping, tessellating curves first. **Output:** list: Counterclockwise index triples into outline_points; invalid or open geometry raises ValueError. |
| [`Sketch._triangles_unchecked()`](../../src/sketch_geometry.py#L778) | Ear-clip an already validated straight-edge polygon, removing redundant collinear vertices. **Output:** list: Counterclockwise triples indexing this sketch's points; triangulation failure raises ValueError. |
| [`prism_vertices(sketch)`](../../src/sketch_geometry.py#L814) | Build a flat-shaded closed prism with outward normals, centered on its area centroid in XY and symmetric about Z=0. **Output:** numpy.ndarray: Flat float32 XYZ/normal data for triangles; invalid or unrenderable geometry raises ValueError. |
| [`prism_vertices.triangle(a, b, c)`](../../src/sketch_geometry.py#L833) | Append one triangle and its computed flat normal to the enclosing output list. **Output:** None. Extends the prism builder's result with three XYZ/normal vertices. |

## Existing checks

[test_sketch_parts.py](../../Testing/Developer_Tests/test_sketch_parts.py), [test_arcs.py](../../Testing/Developer_Tests/test_arcs.py), [test_circles.py](../../Testing/Developer_Tests/test_circles.py), [test_sketch_constraints.py](../../Testing/Developer_Tests/test_sketch_constraints.py), [test_point_dragging.py](../../Testing/Developer_Tests/test_point_dragging.py), [test_sketch_deletion.py](../../Testing/Developer_Tests/test_sketch_deletion.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[part_format](part_format.md), [feature_geometry](feature_geometry.md), [part_document](part_document.md), [part_export](part_export.md), [part_editor](../Frontend/part_editor.md).
