# scene.py: backend guide

Source: [src/scene.py](../../src/scene.py). [Documentation index](../README.md).

Hold mutable scene-instance state separately from reusable part definitions and CPU meshes.

## How it works

`SceneObject(meshPath=...)` loads a `PartAsset`, exposes its optional `Part`, and initializes JSON spawn position/velocity. Default object names become the part name or legacy filename stem. Position, rotation, scale, velocity, acceleration, and angular velocity belong to the instance.

`Scene` owns an object list, optional filepath, and dirty flag. `addObject()` only appends; render upload and dirty-state bookkeeping remain the caller's responsibility.

## Contracts and editing considerations

- Position is in metres, rotation uses Euler degrees (`Rx * Ry * Rz`), velocity is m/s, acceleration is m/s², and angular velocity is rad/s. Scale is dimensionless.
- Restitution/body type resolve instance override → part default → legacy default (bounce 0 and static).
- `setPhysicsProperties()` validates all requested values before applying bounce/velocity/optional body type. The part definition stays unchanged.
- Basic transform/motion setters do not validate inputs or mark a scene dirty. Positive finite scale is checked when physics starts.
- A static instance may retain a stored velocity; the solver initializes static motion to zero.
- Creating multiple instances reparses assets; there is no global asset cache or automatic disk refresh.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`SceneObject.__init__(name='Object', meshPath=None)`](../../src/scene.py#L21) | Initialize instance transform and motion state, optionally loading an asset and applying its spawn position, velocity, and default name. **Output:** None. |
| [`SceneObject.setPosition(x, y, z)`](../../src/scene.py#L70) | Replace the instance's XYZ position without validating or marking its scene dirty. **Output:** None. Stores a new position list. |
| [`SceneObject.setRotation(x, y, z)`](../../src/scene.py#L84) | Replace the instance's Euler angles without validating or marking its scene dirty. **Output:** None. Stores a new rotation list; rendering uses Rx * Ry * Rz. |
| [`SceneObject.setVelocity(x, y, z)`](../../src/scene.py#L98) | Replace the instance's starting linear velocity without validation. **Output:** None. Stores a new velocity list. |
| [`SceneObject.restitution()`](../../src/scene.py#L112) | Resolve bounce from the instance override, then the part default, then the legacy default. **Output:** float: Effective restitution, defaulting to 0 for legacy meshes. |
| [`SceneObject.restitution.setter(value)`](../../src/scene.py#L124) | Validate and store an instance bounce override without changing the part definition. **Output:** None. Raises ValueError for values outside [0, 1] or non-finite numbers. |
| [`SceneObject.body_type()`](../../src/scene.py#L137) | Resolve body behavior from the instance override or part definition. **Output:** str: dynamic or static; legacy meshes default to static. |
| [`SceneObject.body_type.setter(value)`](../../src/scene.py#L148) | Store a validated instance body-type override. **Output:** None. Raises ValueError unless the value is dynamic or static. |
| [`SceneObject.setPhysicsProperties(bounce, velocity, body_type=None)`](../../src/scene.py#L161) | Validate all requested physics edits before applying instance overrides and velocity. Does not mark the containing scene dirty. **Output:** None. Updates bounce, velocity, and optional body type; validation failures leave state unchanged. |
| [`SceneObject.setAcceleration(x, y, z)`](../../src/scene.py#L184) | Replace the instance's additional acceleration without validation. **Output:** None. Stores a new acceleration list used as force divided by mass during physics. |
| [`Scene.__init__()`](../../src/scene.py#L202) | Initialize an empty scene with no filepath and no unsaved-change flag. **Output:** None. |
| [`Scene.addObject(obj)`](../../src/scene.py#L212) | Append an object without uploading GPU data or marking the scene dirty. **Output:** None. Mutates the scene's objects list. |
| [`Scene.sceneHasObjects()`](../../src/scene.py#L223) | Check whether any scene object exists. **Output:** bool: True when objects is nonempty. |

## Existing checks

[test_properties.py](../../Testing/Developer_Tests/test_properties.py), [test_part_assets.py](../../Testing/Developer_Tests/test_part_assets.py), [test_scene_deletion.py](../../Testing/Developer_Tests/test_scene_deletion.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[part_assets](part_assets.md), [part_format](part_format.md), [simuO](simuO.md), [physics_world](physics_world.md), [properties_dialog](../Frontend/properties_dialog.md).
