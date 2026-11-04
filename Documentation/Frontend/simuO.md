# simuO.py: frontend guide

Source: [src/simuO.py](../../src/simuO.py). [Documentation index](../README.md).

The main Qt scene-editing window and application wrapper: menus, object pickers, transform/property dialogs, child editors, and playback windows.

This file serves both layers. See the [backend companion](../Backend/simuO.md) for its other responsibilities.

## How it works

`App.run()` configures OpenGL 3.3 Core Profile, creates or reuses `QApplication`, shows `SimuOMainWindow`, and enters the event loop only if it owns the application. The window owns a `Scene`, an `OpenGLViewport`, temporary-part management, and references to part/playback windows.

User actions open modal object pickers and dialogs. Accepted edits update instances, mark the scene dirty, and request repaint. New/open/close operations protect unsaved work with Save/Discard/Cancel.

## Contracts and editing considerations

- Properties exposes dynamic/static behavior, bounce, and starting velocity; material density/color/custom fields are not general UI controls here.
- Rotation controls use degrees; position controls use metres. These change scene instances, not the referenced reusable part file.
- The temporary-parts dock is shown only while unsaved copies exist. Closing or replacing a scene must respect save cancellation/failure.
- Render creates an independent simulation window; edits require a new playback snapshot to take effect.
- Child window references prevent premature collection. Disabled toolbar actions are placeholders, not implemented tools.
- Import/load/save/delete implementations are documented separately in the backend companion.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`SimuOMainWindow.__init__(projectPath=None, scene=None)`](../../src/simuO.py#L40) | Build the scene editor, viewport, menus, temporary-part panel, and child-window registries; optionally load a project before GL initialization. **Output:** None. |
| [`SimuOMainWindow.createTemporaryPartsPanel()`](../../src/simuO.py#L186) | Create a hidden dock showing unsaved part copies and their temporary directory. **Output:** None. Adds its visibility action to the Window menu. |
| [`SimuOMainWindow.refreshTemporaryParts()`](../../src/simuO.py#L206) | Repopulate temporary-part names and paths, showing the dock only when copies exist. **Output:** None. Updates panel contents and visibility. |
| [`SimuOMainWindow.newPart()`](../../src/simuO.py#L223) | Open an independent feature-based part editor and retain its window reference. **Output:** None. Leaves the scene open. |
| [`SimuOMainWindow.newProject()`](../../src/simuO.py#L235) | Protect unsaved changes, then clear scene objects, uploaded buffers, temporary copies, and project identity. **Output:** None. Resets the editor to a clean untitled scene after confirmation. |
| [`SimuOMainWindow.openFile()`](../../src/simuO.py#L385) | Prompt for a project, protect unsaved work, and load it; clear old temporary copies only after success. **Output:** None. Cancellation leaves the current scene open. |
| [`SimuOMainWindow.confirmUnsavedChanges(title)`](../../src/simuO.py#L596) | Offer Save/Discard/Cancel when dirty objects, an unsaved scene, or temporary parts need protection. **Output:** bool: True if clean, discarded, or successfully saved; False on cancellation or failed save. |
| [`SimuOMainWindow.confirmTemporaryParts(title)`](../../src/simuO.py#L622) | Preserve the older temporary-part confirmation entry point by delegating to the full scene unsaved-change check. **Output:** bool: Whether the requested operation may continue. |
| [`SimuOMainWindow.closeEvent(event)`](../../src/simuO.py#L634) | Protect unsaved changes, close playback windows, release temporary copies, and accept closure; otherwise ignore it. **Output:** None. Controls window closure through the event. |
| [`SimuOMainWindow.openSetRotationObjectList()`](../../src/simuO.py#L656) | Show a scene-object picker and open the rotation dialog for the selected row. **Output:** None. Uses a nested selection callback. |
| [`SimuOMainWindow.openSetRotationObjectList.selectObject()`](../../src/simuO.py#L687) | Read the enclosing picker's selected row and open that object's rotation controls. **Output:** None. Accepts the picker only when a row is selected. |
| [`SimuOMainWindow.openSetRotationDialog(sceneObject)`](../../src/simuO.py#L713) | Show XYZ Euler angle controls and apply accepted values to one scene instance. **Output:** None. Accepted edits mark the scene dirty and repaint the viewport. |
| [`SimuOMainWindow.openSetRotationDialog.applyRotation()`](../../src/simuO.py#L790) | Apply the enclosing dialog's XYZ angle values and finish the dialog. **Output:** None. Mutates the selected object, marks dirty, and repaints. |
| [`SimuOMainWindow.openRepositionObjectList()`](../../src/simuO.py#L819) | Show an object picker and open position controls for the selected row. **Output:** None. Leaves state unchanged until a position edit is accepted. |
| [`SimuOMainWindow.openRepositionObjectList.selectObject()`](../../src/simuO.py#L850) | Read the enclosing picker's selected row and open that object's position controls. **Output:** None. Accepts the picker only when a row is selected. |
| [`SimuOMainWindow.openPositionDialog(sceneObject)`](../../src/simuO.py#L876) | Show XYZ position controls for one scene instance and apply accepted coordinates. **Output:** None. Accepted edits mark the scene dirty and repaint. |
| [`SimuOMainWindow.openPositionDialog.applyPosition()`](../../src/simuO.py#L952) | Apply the enclosing dialog's XYZ coordinates and finish the dialog. **Output:** None. Mutates the selected instance, marks dirty, and repaints. |
| [`SimuOMainWindow.createMenus()`](../../src/simuO.py#L981) | Create scene file/window/help menus and physics playback action with shortcuts and callbacks. **Output:** None. Stores menu/action references used elsewhere by the window. |
| [`SimuOMainWindow.showControls()`](../../src/simuO.py#L1053) | Display scene, camera, property-editing, and shortcut guidance. **Output:** None. Opens an informational dialog. |
| [`SimuOMainWindow.createToolbar()`](../../src/simuO.py#L1071) | Build scene tools, disable unavailable operations, and add Properties/Delete Part actions. **Output:** None. Stores tool action references for selection state. |
| [`SimuOMainWindow.openDeletePartDialog()`](../../src/simuO.py#L1120) | Prompt for a non-axis object to remove, then delegate accepted deletion. **Output:** None. Displays guidance when the scene has no removable parts. |
| [`SimuOMainWindow.openPropertiesObjectList()`](../../src/simuO.py#L1174) | Choose a non-axis instance for property editing, opening its dialog directly when only one exists. **Output:** None. Displays guidance if no editable objects exist. |
| [`SimuOMainWindow.openPropertiesDialog(sceneObject)`](../../src/simuO.py#L1204) | Read accepted body-type, bounce, and velocity edits and apply them only if effective values changed. **Output:** None. Marks the scene dirty and repaints; cancellation leaves the instance unchanged. |
| [`SimuOMainWindow.openPhysicsRender()`](../../src/simuO.py#L1226) | Open and retain an independent live simulation window for the current scene. **Output:** None. Displays guidance or dependency/validation errors when playback cannot start. |
| [`SimuOMainWindow.toolSelected(name)`](../../src/simuO.py#L1251) | Update toolbar checks and dispatch a selected implemented tool to its object picker. **Output:** None. Opens position or rotation controls for those tool names. |
| [`App.__init__(projectPath=None, scene=None)`](../../src/simuO.py#L1280) | Store an optional project path and scene, creating an empty scene when omitted. **Output:** None. Defers Qt window creation to run. |
| [`App.run()`](../../src/simuO.py#L1302) | Configure an OpenGL 3.3 core surface, create/show the scene editor, and run Qt only if this App owns QApplication. **Output:** int: Qt exit code, or 0 when an existing application already owns the event loop. |

## Existing checks

[test_properties.py](../../Testing/Developer_Tests/test_properties.py), [test_project_safety.py](../../Testing/Developer_Tests/test_project_safety.py), [test_scene_deletion.py](../../Testing/Developer_Tests/test_scene_deletion.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[simuO](../Backend/simuO.md), [renderer](renderer.md), [properties_dialog](properties_dialog.md), [feature_editor](feature_editor.md), [physics_render](physics_render.md).
