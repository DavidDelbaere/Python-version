# physics_world.py: backend guide

Source: [src/physics_world.py](../../src/physics_world.py). [Documentation index](../README.md).

Run an independent rigid-body snapshot of a scene using a private PyBullet DIRECT connection.

## How it works

Construction copies mutable instance state and shares CPU asset definitions. `_build()` creates collision bodies, material response, initial velocity, and optional floor. `step(count)` advances fixed `1/240` second steps, adds force from per-object acceleration, then `sync()` copies solver motion into the simulation scene.

`reset()` clears contacts and rebuilds initial state. `close()` disconnects the owned Bullet client and is safe to repeat.

## Contracts and editing considerations

- Boxes use analytic box colliders/inertia. Static meshes use concave triangle meshes; dynamic sketch/feature/legacy geometry uses convex hulls, filling visual concavities for collision.
- Density-derived mass scales by the product of positive instance scales. Explicit mass remains unchanged. Static solver mass is zero.
- Dynamic legacy meshes use 1 kg and friction 0.5 by default. Custom metadata has no solver effect.
- Orientation helpers convert between editor `Rx * Ry * Rz` Euler degrees and Bullet quaternions/matrices. Angular velocity is rad/s.
- Gravity is a finite Y acceleration in m/s². Contact coefficients combine across surfaces; floor friction/restitution are each 1.
- The source editor scene's transform/motion lists remain untouched. Shared definitions are not deeply immutable and should not be mutated during playback.
- Bullet import is lazy; construction cleans up its connection on initialization failure. Playback owners must call `close()`.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`quaternion(rotation)`](../../src/physics_world.py#L10) | Convert editor Euler degrees to Bullet orientation with the renderer's Rx * Ry * Rz convention. **Output:** tuple: Quaternion components (x, y, z, w). |
| [`editor_rotation(matrix)`](../../src/physics_world.py#L27) | Convert a rotation matrix into editor Euler degrees, choosing Z=0 at gimbal lock. **Output:** list: X, Y, Z angles compatible with the renderer's rotation order. |
| [`state_vector(value, label, positive=False)`](../../src/physics_world.py#L45) | Normalize finite three-component instance state, optionally requiring positive components. **Output:** list: Three floats; invalid shape, numbers, or positivity raise ValueError. |
| [`PhysicsWorld.__init__(source_scene, gravity=-9.81, floor=True)`](../../src/physics_world.py#L69) | Create a private Bullet DIRECT world from a scene snapshot. Copy mutable instance state, share asset definitions, and release the client if initialization fails. **Output:** None. Creates a solver connection and collision bodies; invalid state or missing dependencies propagate errors. |
| [`PhysicsWorld._build()`](../../src/physics_world.py#L114) | Create floor and part collision bodies, masses, material response, inertia, and initial velocities. Dynamic mesh bodies use convex hulls; static meshes retain concavities. **Output:** None. Populates body and mass lists in the connected solver; invalid shapes or numeric ranges raise ValueError. |
| [`PhysicsWorld.time()`](../../src/physics_world.py#L192) | Calculate elapsed simulated time from the fixed-step count. **Output:** float: Simulation time in seconds. |
| [`PhysicsWorld.set_gravity(value)`](../../src/physics_world.py#L200) | Validate and set uniform gravity along world Y. **Output:** None. Updates this world and Bullet; non-finite gravity raises ValueError. |
| [`PhysicsWorld.step(count=1)`](../../src/physics_world.py#L214) | Advance fixed 1/240-second steps, applying per-object acceleration forces, then synchronize instance state. **Output:** None. Mutates the simulation scene and step counter, leaving the source scene unchanged. |
| [`PhysicsWorld.sync()`](../../src/physics_world.py#L236) | Copy Bullet poses and velocities back into dynamic objects in the simulation scene. **Output:** None. Updates position, Euler rotation, linear velocity, and angular velocity; static objects are skipped. |
| [`PhysicsWorld.reset()`](../../src/physics_world.py#L254) | Clear the solver and contact manifolds, restore initial instance state, and rebuild collision bodies. **Output:** None. Resets simulated time and all body/mass records. |
| [`PhysicsWorld.close()`](../../src/physics_world.py#L273) | Disconnect this world's Bullet client if still connected. **Output:** None. Marks the client closed; repeated calls are harmless. |

## Existing checks

[test_physics_world.py](../../Testing/Developer_Tests/test_physics_world.py), [test_properties.py](../../Testing/Developer_Tests/test_properties.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[scene](scene.md), [physics_render](physics_render.md), [physics_render](../Frontend/physics_render.md), [part_format](part_format.md).
