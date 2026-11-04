# ray.py: backend guide

Source: [src/ray.py](../../src/ray.py). [Documentation index](../README.md).

`Ray` stores an origin and direction as NumPy float32 vectors. It supports camera-ray visualization in the scene viewport; it does not implement scene selection, intersections, or physics collision detection.

| Function / property | Inputs and output |
| --- | --- |
| `Ray(position, direction)` | Three-component vectors; stores them as float32 arrays without normalizing the direction. |
| `position`, `direction` | Expose the stored arrays. |
| `at(t)` | Returns `position + direction * t`. Distance is in metres when the direction is normalized. |
| `render(t=100.0)` | Returns six float32 values describing the line's start and end, suitable for GL_LINES. |
| `RayPosition(position)`, `Direction(direction)` | Compatibility helpers returning their argument unchanged. |
| `checkCollisions()` | Reserved placeholder; currently returns None and performs no checks. |

`Camera.mouse_ray()` unprojects a pointer position and returns a normalized world-space direction. `OpenGLViewport.RenderRay()` stores its line data and requests a repaint; the viewport creates the line shader and GPU buffers in its GL initialization callback.

See [frontend camera/rendering](../Frontend/renderer.md), [backend GPU rendering](renderer.md), and [test_rays.py](../../Testing/Developer_Tests/test_rays.py).
