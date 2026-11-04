# main.py: frontend guide

Source: [src/main.py](../../src/main.py). [Documentation index](../README.md).

The desktop entry point. It chooses the scene editor or Part Editor from command-line arguments or the Tk startup chooser.

## How it works

1. Before Qt imports, choose the Linux `xcb` backend when an X display exists, while respecting an explicit `QT_QPA_PLATFORM`.
2. Parse an optional project path, `--new`, and `--part-editor`. A `.simuOPart` path routes to the Part Editor automatically.
3. If no route is specified, run `startup_menu()` and collect `(action, filepath)` from nested callbacks.
4. Destroy the hidden Tk root before starting the chosen Qt editor. `main()` returns the editor exit code, or `None` when the chooser is cancelled.

## Contracts and editing considerations

- Startup actions are `new`, `import`, `new_part`, and `open_part`; a path is optional for creation actions.
- The menu callbacks record selection in a captured dictionary; they do not create editors themselves.
- This module imports scene dependencies before parsing options, so broken imports can also prevent `--help`.
- Keep resource lookup independent of the shell's working directory through `resource_path()`.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`startup_menu()`](../../src/main.py#L18) | Run the modal Tk startup chooser and destroy its hidden root after selection or closure. **Output:** tuple: (action, filepath), with None values when no action/path was chosen. |
| [`startup_menu.new_project()`](../../src/main.py#L34) | Record the startup choice to create an empty scene in the enclosing result dictionary. **Output:** None. Mutates captured startup state. |
| [`startup_menu.import_project(filepath)`](../../src/main.py#L43) | Record the chosen scene path and import action in the enclosing startup state. **Output:** None. Mutates captured startup state. |
| [`startup_menu.new_part()`](../../src/main.py#L55) | Record the startup choice to create a new editable part. **Output:** None. Mutates captured startup state. |
| [`startup_menu.open_part(filepath)`](../../src/main.py#L63) | Record the chosen part path and open-part action in the enclosing startup state. **Output:** None. Mutates captured startup state. |
| [`main()`](../../src/main.py#L97) | Parse command-line options, choose the scene/part editor or startup menu, and start the selected application. **Output:** int or None: Editor event-loop exit code, or None if the startup chooser was closed without a selection. |

## Existing checks

[test_part_menu.py](../../Testing/Developer_Tests/test_part_menu.py), [test_portability.py](../../Testing/Developer_Tests/test_portability.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[startMenu](startMenu.md), [simuO](simuO.md), [part_editor](part_editor.md), [resources](../Backend/resources.md).
