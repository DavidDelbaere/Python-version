"""Qt startup dialog for creating or opening an editor project."""

from importlib.resources import as_file, files

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QFileDialog, QLabel, QPushButton, QVBoxLayout

from simuo.ui.theme import load_stylesheet


class StartupDialog(QDialog):
    """Qt startup dialog, kept in the same event loop as the OpenGL window."""

    def __init__(self):
        super().__init__()

        self.action = None
        self.filepath = None

        self.setWindowTitle("SimuO")
        self.setFixedSize(520, 610)
        self.setStyleSheet(load_stylesheet("startup"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 36, 48, 42)
        layout.setSpacing(12)

        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        with as_file(files("simuo.resources").joinpath("images", "simuo_logo.png")) as logo_path:
            pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    390,
                    270,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        layout.addWidget(logo, 1)

        title = QLabel("SimuO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("3D Physics Simulator")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #9c9c9c; font-size: 12px;")
        layout.addWidget(subtitle)
        layout.addSpacing(18)

        new_button = QPushButton("New Scene")
        new_button.clicked.connect(self.new_project)
        layout.addWidget(new_button)

        import_button = QPushButton("Import Scene")
        import_button.clicked.connect(self.import_project)
        layout.addWidget(import_button)

    def new_project(self):
        self.action = "new"
        self.accept()

    def import_project(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import SimuO Project",
            "",
            "SimuO Projects (*.simuO);;All Files (*)",
        )
        if filepath:
            self.action = "import"
            self.filepath = filepath
            self.accept()
