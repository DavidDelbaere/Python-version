# renderer.py: backend guide

Source: [src/renderer.py](../../src/renderer.py). [Documentation index](../README.md).

The OpenGL 3.3 asset-upload and triangle-rendering integration shared by scene editing and physics playback.

This file serves both layers. See the [frontend companion](../Frontend/renderer.md) for its other responsibilities.

## How it works

`initializeGL()` enables depth testing, compiles axis/object shaders, creates axis buffers, caches uniforms, and uploads initial scene objects. Live imports use `addNewObject()`; both paths call `_uploadObject()`.

`paintGL()` builds projection/view matrices and each instance model matrix `T * Rx * Ry * Rz * S`, reads current color/transform state, then draws triangle arrays. Vertex normals use the inverse-transpose model matrix; fragment color combines ambient and camera-directed diffuse lighting.

## Contracts and editing considerations

- Input is flat float32 interleaved XYZ/normal data. Attribute 0 is position, attribute 1 is normal, with a 24-byte stride. No index buffer is used.
- `_uploadObject()` requires the caller to own a current GL context; public live upload/removal helpers manage the widget context.
- Render records hold SceneObject, VAO, VBO, and vertex count. Adding an upload does not add the instance to the CPU scene list; removing it does not remove the CPU instance.
- Transform/color changes are read during repaint. Geometry changes require rebuilding the CPU asset and re-uploading the VBO.
- `removeObject()`/`clearRenderObjects()` delete per-object GPU buffers. The axis has separate resources.
- Camera and event callbacks are documented in the frontend companion. A working desktop graphics context is needed to exercise GPU rendering.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`OpenGLViewport.clearRenderObjects()`](../../src/renderer.py#L401) | Acquire the GL context, delete all uploaded object VAOs/VBOs, clear render records, and repaint. **Output:** None. Leaves the CPU scene and axis resources intact. |
| [`OpenGLViewport.removeObject(sceneObject)`](../../src/renderer.py#L435) | Release uploaded buffers for an instance using the current widget context and remove its render records. **Output:** None. Leaves the CPU scene list unchanged and schedules a repaint. |
| [`OpenGLViewport._uploadObject(sceneObject)`](../../src/renderer.py#L457) | Upload validated CPU position/normal data and append a VAO/VBO render record. The caller must own a current OpenGL context. **Output:** None. Allocates GPU resources; partial allocations are released if setup fails. |
| [`OpenGLViewport.addNewObject(sceneObject)`](../../src/renderer.py#L491) | Acquire the viewport's GL context, upload one instance, then schedule repaint. **Output:** None. Adds GPU render records without adding the instance to the scene list. |
| [`OpenGLViewport.initializeGL()`](../../src/renderer.py#L530) | Enable depth testing, compile shaders, create axis buffers, and upload existing scene assets under Qt's current GL context. **Output:** None. Initializes GPU handles and cached uniform locations. |
| [`OpenGLViewport.resizeGL(width, height)`](../../src/renderer.py#L661) | Set the physical-pixel GL viewport using the widget's device-pixel ratio. **Output:** None. Updates GL viewport dimensions with a minimum of one pixel. |
| [`OpenGLViewport.paintGL()`](../../src/renderer.py#L702) | Update camera movement, clear buffers, and draw axes and uploaded triangles using current instance transforms and colors. **Output:** None. Draws one frame; geometry remains in static GPU buffers. |

## Existing checks

[gui_part_render.py](../../Testing/Developer_Tests/gui_part_render.py), [gui_obj_import.py](../../Testing/Developer_Tests/gui_obj_import.py), [gui_physics_playback.py](../../Testing/Developer_Tests/gui_physics_playback.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[renderer](../Frontend/renderer.md), [part_assets](part_assets.md), [scene](scene.md), [simuO](simuO.md), [physics_render](physics_render.md).
