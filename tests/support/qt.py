"""Configure OpenGL before the first QApplication, for every Qt test subset."""

from PySide6.QtWidgets import QApplication

from simuo.rendering.context import configure_opengl

configure_opengl()


def get_application():
    return QApplication.instance() or QApplication([])
