# startMenu.py: frontend guide

Source: [src/startMenu.py](../../src/startMenu.py). [Documentation index](../README.md).

The CustomTkinter startup window: branding, scene creation/import, and part creation/opening.

## How it works

`showStartMenu()` returns a `SimuOStartMenu` toplevel. Button callbacks either invoke a no-argument creation callback or pass a selected filename to an open/import callback. The chooser closes before invoking an accepted action. File-dialog cancellation keeps it open.

## Contracts and editing considerations

- `parent` owns the Tk window; `on_new`/`on_new_part` take no arguments, while `on_import`/`on_open_part` receive a filename.
- `logo_path` is optional; missing images fall back to a text logo.
- Modal input capture occurs after the toplevel is mapped. Moving it earlier can produce Linux visibility/grab failures.
- The standalone block previews the menu and prints callback choices; normal startup is coordinated by `main.py`.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`SimuOStartMenu.__init__(parent, logo_path=None, on_new=None, on_import=None, title='SimuO', width=520, height=710, on_new_part=None, on_open_part=None)`](../../src/startMenu.py#L11) | Build a fixed-size startup chooser with optional logo and scene/part action callbacks. **Output:** None. Creates a Tk toplevel and schedules centering and modal capture after mapping. |
| [`SimuOStartMenu._grab_when_visible(event)`](../../src/startMenu.py#L83) | Acquire modal input capture only once this startup toplevel is mapped and viewable. **Output:** None. Ignores map events from child widgets. |
| [`SimuOStartMenu._build_ui(logo_path)`](../../src/startMenu.py#L97) | Create the logo/title panel and scene/part buttons, falling back to a text logo if no image exists. **Output:** None. Builds and packs child widgets. |
| [`SimuOStartMenu._new_part()`](../../src/startMenu.py#L311) | Close the chooser and invoke the optional no-argument new-part callback. **Output:** None. Calls the callback only if supplied. |
| [`SimuOStartMenu._open_part()`](../../src/startMenu.py#L322) | Prompt for a part file, then close the chooser and invoke its optional open-part callback. **Output:** None. Cancellation leaves the chooser open. |
| [`SimuOStartMenu._build_text_logo(parent)`](../../src/startMenu.py#L337) | Create a styled text placeholder when the image logo is unavailable. **Output:** None. Packs a label into the supplied parent. |
| [`SimuOStartMenu._center_on_screen()`](../../src/startMenu.py#L375) | Calculate screen-centered geometry using configured startup-window dimensions. **Output:** None. Moves and sizes the toplevel after idle layout. |
| [`SimuOStartMenu._new_project()`](../../src/startMenu.py#L410) | Close the chooser and invoke the optional no-argument new-scene callback. **Output:** None. |
| [`SimuOStartMenu._import_project()`](../../src/startMenu.py#L425) | Prompt for a scene file, then close the chooser and pass its path to the optional import callback. **Output:** None. Cancellation leaves the chooser open. |
| [`SimuOStartMenu._close()`](../../src/startMenu.py#L463) | Release modal capture if possible and destroy the startup toplevel. **Output:** None. Suppresses capture-release errors during closure. |
| [`showStartMenu(parent, logo_path=None, on_new=None, on_import=None, on_new_part=None, on_open_part=None)`](../../src/startMenu.py#L479) | Construct a startup chooser attached to the supplied Tk parent. **Output:** SimuOStartMenu: New chooser window; this helper does not start or wait on an event loop. |
| [`new_project()`](../../src/startMenu.py#L540) | Print the new-scene selection for the standalone menu preview. **Output:** None. Writes preview feedback to stdout. |
| [`import_project(filepath)`](../../src/startMenu.py#L552) | Print the imported scene path for the standalone menu preview. **Output:** None. Writes preview feedback to stdout. |

## Existing checks

[test_part_menu.py](../../Testing/Developer_Tests/test_part_menu.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[main](main.md), [resources](../Backend/resources.md).
