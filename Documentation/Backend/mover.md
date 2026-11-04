# mover.py: backend guide

Source: [src/mover.py](../../src/mover.py). [Documentation index](../README.md).

The incoming `Mover` owns a selected SceneObject's three world-axis arrows, their triangle geometry, ray hit testing, and single-axis drag state. It uses `localMin`/`localMax` from the loaded CPU mesh; GPU upload also refreshes those bounds for generated assets.

| API | Inputs and output |
| --- | --- |
| `Mover(scene_object)` | Attach mutable gizmo state to an instance. |
| `world_center()`, `half_extent()` | Return the current bounds-derived center/extents as glm vectors. |
| `axis_endpoints(axis_index)`, `axis_segments()` | Describe arrow shafts for axis indices 0/1/2. |
| `build_render_data()` | Return flat float32 XYZ triangles plus per-axis color and draw ranges. |
| `hit_test(ray_origin, ray_direction)` | Return an axis name within the fixed pick radius, or None. |
| `begin_drag(axis_name, origin, direction)` | Freeze the start position and axis reference. |
| `update_drag(origin, direction)` | Project a new ray onto the frozen axis and update the instance position. |
| `end_drag()` | Clear the active drag state. |
| `build_arrow_mesh(...)` | Build cylinder/cone triangle corners for an arrow. |
| `ray_segment_distance(...)`, `closest_point_on_line_t(...)` | Geometry helpers for shaft picking and drag projection. |

The viewport marks the scene dirty when an actual drag changes position. Selection clears on object removal or scene replacement, and focus loss ends a drag. Arrows render with depth testing temporarily disabled so they remain visible over the selected part.

Current arrows have fixed world-unit sizes and pick radius. Bounds placement uses local extents and instance scale rather than a fully rotated world bounding box. These are existing movement-tool limitations, not CAD snapping or general object-transform solving.

See [ray picking](ray.md), [viewport controls](../Frontend/renderer.md), and [integration tests](../../Testing/Developer_Tests/test_mover.py).
