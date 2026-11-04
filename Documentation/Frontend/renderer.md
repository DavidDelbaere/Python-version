# renderer.py: frontend guide

Source: [src/renderer.py](../../src/renderer.py). [Documentation index](../README.md).

The scene and playback OpenGL widget's camera, navigation, framing, and interaction layer.

This file serves both layers. See the [backend companion](../Backend/renderer.md) for its other responsibilities.

## How it works

`Camera` stores world position, yaw/pitch in degrees, and a normalized viewing basis. `OpenGLViewport` requests regular repaints and tracks held keys and captured right-mouse movement. Every frame calls `update_camera(delta_time)` before drawing.

`frameObject()` sets a usable viewing position around scaled/translated local mesh bounds without resizing geometry. GPU upload, shader behavior, and rendering resource ownership are documented in the backend companion.

## Contracts and editing considerations

- WASD moves along camera forward/right; Space/Ctrl moves along world Y. Left/right arrows turn at a time-scaled rate.
- Right-mouse look hides/captures the pointer and recenters it. Recenter-generated events are ignored to avoid unwanted rotation.
- Focus loss clears held keys and mouse capture. Escape requests window closure through the owning window's unsaved-change handling.
- Camera pitch is clamped to avoid flipping. Pointer sensitivity is degrees per pixel.
- Framing bounds do not include instance rotation; physics playback builds transformed scene bounds before calling it.
- Pointer warping depends on the desktop backend; normal Linux startup selects X11/XWayland via xcb when available.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`createAxisLines(minimum=-2000, maximum=2000, tickSize=0.15)`](../../src/renderer.py#L165) | Generate three world axes with integer-spaced tick marks for GL_LINES. **Output:** numpy.ndarray: Flat float32 XYZ positions, two vertices per line segment. |
| [`Camera.__init__()`](../../src/renderer.py#L246) | Initialize camera position and Euler view angles, then compute its viewing basis. **Output:** None. |
| [`Camera.update_vectors()`](../../src/renderer.py#L290) | Recompute normalized forward, right, and up vectors from yaw/pitch in degrees. **Output:** None. Mutates the camera basis. |
| [`Camera.rotate(dx, dy, sensitivity=0.12)`](../../src/renderer.py#L332) | Apply pointer deltas to yaw/pitch, clamp pitch to avoid flipping, and rebuild the basis. **Output:** None. Mutates camera angles and vectors. |
| [`Camera.view_matrix()`](../../src/renderer.py#L368) | Build the camera's world-to-view transform from position and basis. **Output:** glm.mat4: Look-at view matrix. |
| [`OpenGLViewport.__init__(parent=None, scene=None)`](../../src/renderer.py#L410) | Initialize viewport input/camera state and a repaint timer; GPU allocation is deferred until initializeGL. **Output:** None. |
| [`OpenGLViewport.frameObject(sceneObject)`](../../src/renderer.py#L610) | Position the camera around scaled/translated local mesh bounds so SI-sized assets are visible without resizing them. Bounds do not include instance rotation. **Output:** None. Updates camera position/orientation and repaints. |
| [`OpenGLViewport.update_camera(delta_time)`](../../src/renderer.py#L1137) | Move and turn the camera from held keys, scaling speeds by elapsed time. **Output:** None. Updates camera position and viewing basis. |
| [`OpenGLViewport.keyPressEvent(event)`](../../src/renderer.py#L1195) | Track a pressed key for continuous movement and request window closure on Escape. **Output:** None. Mutates held-key state. |
| [`OpenGLViewport.keyReleaseEvent(event)`](../../src/renderer.py#L1219) | Remove a released key from held state, ignoring synthetic auto-repeat releases. **Output:** None. |
| [`OpenGLViewport.focusOutEvent(event)`](../../src/renderer.py#L1238) | Clear held keys and release mouse capture/cursor hiding when the viewport loses focus. **Output:** None. Delegates the focus event after resetting input state. |
| [`OpenGLViewport.mousePressEvent(event)`](../../src/renderer.py#L1260) | Pick a part or movement arrow on left click; capture mouse look on right click. **Output:** None. Updates selection/drag state or captures the pointer for mouse look. |
| [`OpenGLViewport.mouseReleaseEvent(event)`](../../src/renderer.py#L1293) | End a movement-arrow drag or release captured right-button mouse look. **Output:** None. |
| [`OpenGLViewport.mouseMoveEvent(event)`](../../src/renderer.py#L1315) | Drag the selected part, update arrow hover, or rotate captured mouse look. **Output:** None. Updates a selected part and dirty state, or the camera and pointer. |
| [`OpenGLViewport.center_mouse()`](../../src/renderer.py#L1377) | Warp the system pointer to the widget center in global screen coordinates. **Output:** None. Changes the desktop cursor position. |

## Existing checks

[test_properties.py](../../Testing/Developer_Tests/test_properties.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[renderer](../Backend/renderer.md), [simuO](simuO.md), [physics_render](physics_render.md), [main](main.md).

## Part selection and movement

Left-click a part to select it using a camera ray against its rendered triangles. The selected instance gets three colored world-axis arrows. Drag an arrow to move along its axis; release or lose focus to end the drag. Actual moves mark the scene dirty so normal save protection and scene persistence apply. Removing a selected part or replacing the scene clears its movement tool.

The ray also has debug-line data. Right-mouse camera controls continue to work independently. See [ray picking](../Backend/ray.md) and [movement geometry](../Backend/mover.md).
