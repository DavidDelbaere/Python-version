# part_viewport.py: frontend guide

Source: [src/part_viewport.py](../../src/part_viewport.py). [Documentation index](../README.md).

The Part Editor's orbitable 3D preview and planar face/reference-plane picking widget, implemented with Qt painting.

## How it works

`PartViewport` projects model triangles into the widget using an orbit camera basis, paints shaded triangles in depth order, draws exposed face boundaries and sketch curves, then adds the orientation triad. `pick()` uses nearest ray/triangle intersection; `pick_plane()` intersects visible finite plane patches.

A short left click selects; dragging orbits without selection. Middle drag pans, the wheel zooms, arrow keys orbit, and F fits solid plus draft geometry.

## Contracts and editing considerations

- This is a regular `QWidget`/`QPainter` view, separate from the scene's OpenGL renderer. Triangle painting uses average-depth sorting rather than a GPU depth buffer.
- Solid model coordinates are metres. `project()` returns pixel position plus camera depth, or None for clipped points.
- `face_selected(int)` and `plane_selected(str)` signals let the editor update support/tree state.
- The preview uses fixed colors and selected-face highlighting rather than the reusable part's appearance color. Check material colors in the scene viewport.
- `fit()` includes draft sketches; selected face supports and visible reference planes influence displayed patches and picking.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`unit(v)`](../../src/part_viewport.py#L13) | Normalize a direction vector, using positive Z when its length is zero. **Output:** numpy.ndarray: Unit vector, or [0, 0, 1] for zero length. |
| [`sketch_world_points(feature)`](../../src/part_viewport.py#L26) | Tessellate already validated sketch geometry and place it in its supporting plane. **Output:** numpy.ndarray: Shape (N, 3) world points in metres. |
| [`PartViewport.__init__(parent=None)`](../../src/part_viewport.py#L45) | Initialize an orbitable Qt-painted part preview with default Front support and empty model/selection. **Output:** None. |
| [`PartViewport.fit()`](../../src/part_viewport.py#L70) | Fit built solid and draft sketch points, reset panning, and repaint. **Output:** None. Updates target and camera distance without changing geometry. |
| [`PartViewport.basis()`](../../src/part_viewport.py#L92) | Calculate the orbit camera position and orthonormal viewing axes. **Output:** tuple: NumPy vectors (eye, forward, right, up). |
| [`PartViewport.project(point)`](../../src/part_viewport.py#L105) | Perspective-project a 3D point into widget coordinates, rejecting points too close to or behind the camera. **Output:** tuple or None: (QPointF pixels, camera depth in metres), or None when clipped. |
| [`PartViewport.ray(position)`](../../src/part_viewport.py#L125) | Construct a world-space picking ray through a widget position. **Output:** tuple: Camera origin and normalized 3D ray direction. |
| [`PartViewport.pick(position)`](../../src/part_viewport.py#L140) | Find the nearest solid face intersected by the pointer's ray using triangle tests. **Output:** int: Face index, or -1 if no face is hit. |
| [`PartViewport.plane_extent()`](../../src/part_viewport.py#L173) | Scale visible reference-plane patches to the current camera distance. **Output:** float: Plane patch half-extent in metres. |
| [`PartViewport.visible_planes()`](../../src/part_viewport.py#L181) | Select reference-plane frames to display according to solid and support state. **Output:** list: (plane name, frame) pairs; empty when a solid has only a face support selected. |
| [`PartViewport.pick_plane(position)`](../../src/part_viewport.py#L194) | Ray-test visible finite plane patches and choose the nearest hit. **Output:** str or None: Reference-plane name, or None if no patch is hit. |
| [`PartViewport.mousePressEvent(event)`](../../src/part_viewport.py#L219) | Capture focus and record the initial pointer position for orbit, pan, or click selection. **Output:** None. Initializes drag state. |
| [`PartViewport.mouseMoveEvent(event)`](../../src/part_viewport.py#L233) | Pan on middle-drag or orbit on left/right-drag, clamping camera pitch. **Output:** None. Updates camera state and repaints. |
| [`PartViewport.mouseReleaseEvent(event)`](../../src/part_viewport.py#L254) | Treat a short left click as face/plane selection, emit the selection signal, and finish dragging. **Output:** None. Updates highlight/support and clears drag state. |
| [`PartViewport.wheelEvent(event)`](../../src/part_viewport.py#L278) | Adjust orbit distance within limits according to wheel direction. **Output:** None. Schedules a repaint. |
| [`PartViewport.keyPressEvent(event)`](../../src/part_viewport.py#L291) | Orbit with horizontal arrow keys or fit the view with F; delegate other keys. **Output:** None. Updates view state for handled shortcuts. |
| [`PartViewport._path(points)`](../../src/part_viewport.py#L309) | Project a polygon into a closed painter path with average depth for draw ordering. **Output:** tuple or None: (QPainterPath, mean depth), or None for empty/clipped points. |
| [`PartViewport.paintEvent(event)`](../../src/part_viewport.py#L328) | Paint reference planes, depth-sorted shaded triangles, visible face boundaries, sketches, and the orientation triad. **Output:** None. Draws into the widget using QPainter, without an OpenGL context. |

## Existing checks

[test_plane_viewport.py](../../Testing/Developer_Tests/test_plane_viewport.py), [test_feature_parts.py](../../Testing/Developer_Tests/test_feature_parts.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[feature_editor](feature_editor.md), [renderer](renderer.md), [feature_geometry](../Backend/feature_geometry.md).
