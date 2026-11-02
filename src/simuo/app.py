"""Application lifecycle and public launch entrypoints."""

import sys

from PySide6.QtWidgets import QApplication, QDialog

from simuo.rendering.context import configure_opengl
from simuo.scene.model import Scene


def main():
    from simuo.ui.main_window import SimuOMainWindow
    from simuo.ui.startup import StartupDialog

    configure_opengl()
    application = QApplication(sys.argv)

    startup = StartupDialog()
    if startup.exec() != QDialog.Accepted:
        return 0

    if startup.action == "new":
        print("Creating new SimuO build")
        window = SimuOMainWindow()
    else:
        print("Opening project:", startup.filepath)
        window = SimuOMainWindow(projectPath=startup.filepath)

    window.show()
    return application.exec()


class App:
    """Top-level application launcher for SimuO."""

    def __init__(self, projectPath=None, scene=None):
        """Initialize the application shell.

        Args:
            projectPath: Optional path to a saved project.
            scene: Optional scene to attach to the app.
        """

        self.projectPath = projectPath

        self.scene = scene

        self.window = None

        if self.scene is None:
            self.scene = Scene()

    def run(self):
        """Start the application and show the main editor window.

        Returns:
            int: The return code from the Qt application event loop, if any.
        """

        configure_opengl()
        from simuo.ui.main_window import SimuOMainWindow

        app = QApplication.instance()

        ownsApp = app is None

        if app is None:
            app = QApplication(sys.argv)



        self.window = SimuOMainWindow(projectPath=self.projectPath, scene=self.scene)

        self.window.show()

        if ownsApp:
            return app.exec()

        return 0
