# physics_render.py: backend guide

Source: [src/physics_render.py](../../src/physics_render.py). [Documentation index](../README.md).

The timer, scene-snapshot, visual floor, and GPU lifecycle bridge between `PhysicsWorld` and the shared OpenGL viewport.

This file serves both layers. See the [frontend companion](../Frontend/physics_render.md) for its other responsibilities.

## How it works

`tick()` caps elapsed wall time at 0.1 seconds, accumulates it while running, executes whole fixed physics steps, preserves the fractional remainder, and refreshes viewport/status. A solver exception pauses playback and displays the error.

`reset()` pauses and rebuilds initial physics state; `single_step()` pauses and advances once. `change_floor()` changes solver settings, resets, and updates visible floor objects and uploads. `closeEvent()` stops timers, clears uploaded buffers when valid, and disconnects Bullet.

## Contracts and editing considerations

- The visual floor is a finite box whose top is y=0. The solver's floor is an infinite plane; their geometry is intentionally different.
- The render scene shares simulated instances from `world.scene`, so `sync()` updates the objects drawn by the viewport.
- The floor's CPU mesh is constructed with `Part`, `PartAsset`, and `box_vertices()`; it is an editor helper, not a saved project asset.
- Window construction can fail on missing dependencies or invalid state. The scene editor's open-render action reports supported failures.
- Preserve lifecycle cleanup when changing timers or windows to avoid a live Bullet client or repaint timer after closure.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`PhysicsRenderWindow._ground()`](../../src/physics_render.py#L91) | Build a static visual floor patch sized around the initial simulation scene; the actual solver floor is a plane. **Output:** SceneObject: Floor box with CPU mesh and top surface at y=0. |
| [`PhysicsRenderWindow.reset()`](../../src/physics_render.py#L157) | Pause playback, rebuild the world's initial state, and refresh the viewport and status. **Output:** None. |
| [`PhysicsRenderWindow.single_step()`](../../src/physics_render.py#L169) | Pause playback and simulate exactly one fixed timestep. **Output:** None. Repaints the updated state and status. |
| [`PhysicsRenderWindow.change_floor(enabled)`](../../src/physics_render.py#L180) | Enable or disable floor contact, reset playback, and rebuild the visible object uploads when the viewport is ready. **Output:** None. Updates both solver floor behavior and the visual floor patch. |
| [`PhysicsRenderWindow.tick()`](../../src/physics_render.py#L201) | Accumulate capped wall time, run whole fixed physics steps, and refresh the display. Solver errors pause playback and display the error. **Output:** None. Updates the accumulator, simulated state, and UI. |
| [`PhysicsRenderWindow.closeEvent(event)`](../../src/physics_render.py#L240) | Stop both timers, release uploaded scene buffers, disconnect Bullet, and accept window closure. **Output:** None. Consumes the close event. |

## Existing checks

[gui_physics_playback.py](../../Testing/Developer_Tests/gui_physics_playback.py), [test_physics_world.py](../../Testing/Developer_Tests/test_physics_world.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[physics_render](../Frontend/physics_render.md), [physics_world](physics_world.md), [renderer](renderer.md), [part_assets](part_assets.md).
