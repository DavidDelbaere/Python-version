# feature_geometry.py: backend guide

Source: [src/feature_geometry.py](../../src/feature_geometry.py). [Documentation index](../README.md).

Construct a connected 3D solid from supported planar sketches and ordered additive extrusions.

## How it works

A `FeatureModel` deep-copies feature history. `new_sketch(support)` appends an unextruded feature; `build()` validates and evaluates the history with `manifold3d`, unions joined extrusions, and updates triangle data, planar faces, bounds, and volume. `from_geometry()` parses and builds a serialized model.

A feature records ID, name, plane/face support, sketch geometry, optional depth, and symmetry. Named frames are Front, Right, and Top. `to_world()` and `to_plane()` convert between the sketch frame and 3D.

## Contracts and editing considerations

- All lengths are metres; axes u/v must be orthogonal unit vectors. Plane normal is their cross product.
- Face supports reference earlier extrusions and preserve their local frame. Builds reject references whose supporting face moved/disappeared.
- At most 64 sketches are supported. Extrusions require closed sketches, finite signed depth, and a single connected resulting solid.
- Additive geometry is unioned rather than concatenated, so overlapping material is not counted twice in volume.
- Face supports retain double precision. Display/export vertices use float32 position/normal data; triangles collapsing at that precision are removed.
- Geometry retains feature placement; it is not automatically recentered on its centroid.
- `planar_faces()` supplies labels, triangles, normal, frame, and exposed boundary edges. `face_sketch()` rejects boundaries with holes or complex loops.
- `build()` mutates derived fields and can fail partway through evaluation; UI callers build a candidate before replacing the accepted model.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`validate_frame(frame)`](../../src/feature_geometry.py#L17) | Check finite bounded origin/axes and orthogonal unit sketch axes. **Output:** dict: Original frame; raises ValueError for an invalid frame. |
| [`support_frame(support)`](../../src/feature_geometry.py#L38) | Resolve a reference plane or validate a saved face frame. **Output:** dict: Independent reference-plane frame, or the validated face frame from the support. |
| [`to_world(points, frame)`](../../src/feature_geometry.py#L60) | Map planar coordinates into 3D using the frame origin and axes. **Output:** numpy.ndarray: Shape (N, 3) world points in metres. |
| [`to_plane(points, frame)`](../../src/feature_geometry.py#L75) | Project 3D points into a frame's two orthogonal sketch axes. **Output:** numpy.ndarray: Coordinates with the input's leading dimensions and a final dimension of 2. |
| [`planar_faces(vertices)`](../../src/feature_geometry.py#L91) | Group edge-connected coplanar triangles into selectable faces and extract their boundaries. **Output:** list: Face dictionaries containing label, triangles, normal, frame, and boundary edges; empty for an empty mesh. |
| [`FeatureModel.__init__(features=None)`](../../src/feature_geometry.py#L150) | Copy feature history and initialize empty derived mesh, face, and volume data. Call build to evaluate the history. **Output:** None. |
| [`FeatureModel.has_solid()`](../../src/feature_geometry.py#L167) | Check whether a built display mesh exists. **Output:** bool: True when the vertex buffer is nonempty. |
| [`FeatureModel.size()`](../../src/feature_geometry.py#L176) | Measure the built mesh's axis-aligned bounding-box dimensions. **Output:** tuple: XYZ extents in metres, or (0.001, 0.001, 0.001) for a draft. |
| [`FeatureModel.last_extrusion()`](../../src/feature_geometry.py#L185) | Find the last feature with an extrusion depth in history order. **Output:** str or None: Feature ID, or None if no extrusion exists. |
| [`FeatureModel.geometry()`](../../src/feature_geometry.py#L193) | Serialize the editable feature history without derived mesh data. **Output:** dict: feature_part geometry with a deep copy of the feature list. |
| [`FeatureModel.new_sketch(support)`](../../src/feature_geometry.py#L201) | Validate a support and append an empty sketch feature with a new UUID. Does not build the model. **Output:** dict: Newly appended feature, also owned by this model. |
| [`FeatureModel.build()`](../../src/feature_geometry.py#L218) | Validate ordered features and rebuild one connected solid with manifold3d. Updates volume, float32 triangles/normals, and double-precision face supports; invalid history or geometry raises ValueError. **Output:** FeatureModel: This model after rebuilding; a draft can have no solid. |
| [`FeatureModel.from_geometry(g)`](../../src/feature_geometry.py#L326) | Validate a feature_part geometry envelope and evaluate its history. **Output:** FeatureModel: New built model; invalid geometry raises ValueError. |
| [`FeatureModel.face_support(index)`](../../src/feature_geometry.py#L339) | Describe a built face as a sketch support tied to the last extrusion. **Output:** dict: Face support with parent ID, label, and copied frame. |
| [`FeatureModel.face_sketch(index)`](../../src/feature_geometry.py#L351) | Trace a flat face's single boundary into an editable closed outline. Rejects holes or complex boundaries. **Output:** Sketch: Validated outline in the face's local frame. |

## Existing checks

[test_feature_parts.py](../../Testing/Developer_Tests/test_feature_parts.py), [test_plane_viewport.py](../../Testing/Developer_Tests/test_plane_viewport.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[sketch_geometry](sketch_geometry.md), [feature_document](feature_document.md), [feature_editor](feature_editor.md), [part_viewport](../Frontend/part_viewport.md), [part_assets](part_assets.md).
