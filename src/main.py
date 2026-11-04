
import argparse
import os
import sys
from pathlib import Path

# The camera uses pointer warping, which requires X11 (or XWayland).
# Respect an explicitly selected Qt backend.
if sys.platform.startswith("linux") and os.environ.get("DISPLAY"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import customtkinter as ctk
from startMenu import showStartMenu
from simuO import App
from resources import resource_path


def startup_menu():
    root = ctk.CTk()

    root.withdraw()

    startup = {
        "action": None,
        "filepath": None
    }

    def new_project():
        startup["action"] = "new"

    def import_project(filepath):
        startup["action"] = "import"
        startup["filepath"] = filepath

    def new_part():
        startup["action"] = "new_part"

    def open_part(filepath):
        startup["action"] = "open_part"
        startup["filepath"] = filepath

    logo_path = resource_path("Images", "simuo_logo.png")

    menu = showStartMenu(
        parent=root,
        logo_path=logo_path,
        on_new=new_project,
        on_import=import_project,
        on_new_part=new_part,
        on_open_part=open_part,
    )

    # Wait until the startup menu closes.
    root.wait_window(menu)

    root.destroy()

    return (
        startup["action"],
        startup["filepath"]
    )


def main():
    parser = argparse.ArgumentParser(description="SimuO scene and part editors")
    parser.add_argument("project", nargs="?", help=".simuO scene or .simuOPart to open")
    parser.add_argument("--new", action="store_true", help="open a new scene directly")
    parser.add_argument("--part-editor", action="store_true", help="open the part sketch editor (optionally supply a .simuOPart)")
    args = parser.parse_args()
    if args.part_editor:
        action,filepath = "open_part" if args.project else "new_part",args.project
    elif args.project and Path(args.project).suffix.lower()==".simuopart":
        action,filepath = "open_part",args.project
    elif args.project:
        action, filepath = "import", args.project
    elif args.new:
        action, filepath = "new", None
    else:
        action, filepath = startup_menu()

    if action is None:
        return

    if action in ("new_part","open_part"):
        from part_editor import run_part_editor
        return run_part_editor(filepath)

    if action == "new":
        print("Creating new SimuO build")

        app = App()

    elif action == "import":
        print("Opening project:", filepath)

        app = App(projectPath=filepath)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
