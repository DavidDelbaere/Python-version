# physics_render.py: frontend guide

Source: [src/physics_render.py](../../src/physics_render.py). [Documentation index](../README.md).

A separate nonmodal physics-playback window with Play/Pause, Step, Reset, scene framing, gravity, and optional floor controls.

This file serves both layers. See the [backend companion](../Backend/physics_render.md) for its other responsibilities.

## How it works

`PhysicsRenderWindow(source_scene)` creates a `PhysicsWorld` snapshot, a render scene with an optional visual floor, an `OpenGLViewport`, controls, and a timer. Playback starts running. P toggles, R resets, F frames; standard viewport camera controls also work.

Status shows playback time, dynamic/static counts, legacy mesh guidance, and up to five dynamic-object heights/speeds. Tick/step/reset/floor lifecycle behavior is detailed in the backend companion.

## Contracts and editing considerations

- Playback preserves the editor scene's transform and motion lists. Property edits require a new playback window to create a fresh snapshot.
- Gravity is world Y acceleration in m/s². Step advances 1/240 s. Reset restores the snapshot and pauses.
- Framing accounts for rotated/scaled object bounds and optional floor level, excluding the oversized visual floor patch.
- Pausing clears accumulated time so restarting does not catch up paused wall time. Solver errors stop playback and appear in the UI.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`PhysicsRenderWindow.__init__(source_scene, parent=None)`](../../src/physics_render.py#L19) | Create a nonmodal playback window, independent physics snapshot, render viewport, controls, and running timer. **Output:** None. |
| [`PhysicsRenderWindow.frame_scene()`](../../src/physics_render.py#L110) | Frame rotated/scaled simulation objects and optional floor level, excluding the oversized floor patch from bounds. **Output:** None. Updates the viewport camera. |
| [`PhysicsRenderWindow.set_running(running)`](../../src/physics_render.py#L134) | Set playback state, clear accumulated time, and update the play button. **Output:** None. Resets the wall-clock reference to avoid catching up paused time. |
| [`PhysicsRenderWindow.toggle()`](../../src/physics_render.py#L148) | Switch between running and paused playback and update the status display. **Output:** None. |
| [`PhysicsRenderWindow._update_status()`](../../src/physics_render.py#L225) | Display playback time, body counts, legacy-mesh guidance, and up to five dynamic object speeds. **Output:** None. Replaces the status label text. |

## Existing checks

[gui_physics_playback.py](../../Testing/Developer_Tests/gui_physics_playback.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[physics_render](../Backend/physics_render.md), [physics_world](../Backend/physics_world.md), [renderer](renderer.md), [simuO](simuO.md).
