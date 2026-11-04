# ray.py: backend guide

Source: [src/ray.py](../../src/ray.py). [Documentation index](../README.md).

`Ray` stores an origin and direction as float32 vectors, produces line data, and finds the nearest forward triangle hit. `at(t)` evaluates the original parameterized ray; `render(t=100.0)` returns six floats for its line endpoints.

## Picking contract

`checkCollisions(objects)` accepts a SceneObject, a `.obj`/`.simuOPart` path at the local origin, or an iterable of those targets. It returns None on a miss, or a dictionary with `object`, world-space `point`, world-space `distance`, the original ray parameter `t`, and `triangleIndex`.

- Loaded instances use their CPU `asset.vertices`, matching the currently rendered mesh even if its source file changes or is removed.
- Direct file targets use a stat-keyed triangle cache. OBJ-style faces and JSON box/sketch/feature definitions are supported.
- Instance transforms follow the renderer's `T * Rx * Ry * Rz * S` order. Both triangle sides, edges, and origins inside a mesh are supported.
- Picking validates finite three-component ray vectors and rejects zero direction. It normalizes internally, then adjusts `t` for the original direction length.
- This is visual triangle picking, separate from Bullet physics collision shapes. Use it for pointer interaction rather than every render frame.

`Camera.mouse_ray()` returns a normalized world-space camera ray. `OpenGLViewport` gives existing movement arrows priority, otherwise calls `checkCollisions()` to select a part and attach a `Mover`.

See [movement geometry](mover.md), [frontend interaction](../Frontend/renderer.md), [backend rendering](renderer.md), [collision checks](../../Testing/Developer_Tests/test_ray.py), and [camera-ray checks](../../Testing/Developer_Tests/test_rays.py).
