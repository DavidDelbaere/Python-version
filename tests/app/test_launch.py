"""Package imports, entrypoint compatibility, and working-directory independence."""

from importlib import resources
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QLabel

from tests.support.paths import ROOT
from tests.support.qt import get_application
from simuo.ui.startup import StartupDialog
from simuo.ui.theme import load_stylesheet


class ApplicationPackaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_application()

    def test_checkout_launchers_import_the_same_package_from_another_directory(self):
        code = (
            "import runpy, sys\n"
            "entry = runpy.run_path(sys.argv[1], run_name='launcher_check')\n"
            "from simuo.app import main\n"
            "assert entry['main'] is main\n"
        )
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory() as folder:
            for launcher in (ROOT / "main.py", ROOT / "src/main.py"):
                result = subprocess.run(
                    [sys.executable, "-c", code, str(launcher)], cwd=folder,
                    env=environment, capture_output=True, text=True, timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_module_entrypoint_delegates_to_application_main(self):
        with patch("simuo.app.main", return_value=7) as main:
            with self.assertRaises(SystemExit) as exit_status:
                runpy.run_module("simuo", run_name="__main__")
        self.assertEqual(exit_status.exception.code, 7)
        main.assert_called_once_with()

    def test_startup_dialog_logo_and_all_styles_are_package_resources(self):
        dialog = StartupDialog()
        self.addCleanup(dialog.close)
        pixmaps = [label.pixmap() for label in dialog.findChildren(QLabel)]
        self.assertTrue(any(pixmap is not None and not pixmap.isNull() for pixmap in pixmaps))
        package = resources.files("simuo.resources")
        self.assertTrue(package.joinpath("images", "simuo_logo.png").is_file())
        for name in ("startup", "main_window", "hierarchy", "properties", "viewport_tools"):
            self.assertTrue(load_stylesheet(name).strip())

    def test_theme_resources_do_not_depend_on_the_current_directory(self):
        code = (
            "from simuo.ui.theme import load_stylesheet\n"
            "from importlib.resources import files\n"
            "assert 'QMainWindow' in load_stylesheet('main_window')\n"
            "assert files('simuo.resources').joinpath('images', 'simuo_logo.png').is_file()\n"
        )
        environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, "-c", code], cwd=folder, env=environment,
                                    capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_scene_data_and_file_io_import_without_any_gui_or_graphics_dependencies(self):
        code = (
            "import sys\n"
            "from simuo.scene.model import Scene, SceneObject\n"
            "from simuo.scene.persistence import load_project, save_project\n"
            "scene = Scene()\n"
            "scene.addObject(SceneObject('Object'))\n"
            "assert len(scene.objects) == 1\n"
            "assert not any(name.startswith(('PySide6', 'OpenGL', 'numpy', 'glm')) for name in sys.modules)\n"
        )
        environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, "-S", "-c", code], cwd=folder, env=environment,
                                    capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
