"""A compact viewport rail of real transform and framing actions."""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QToolBar

from simuo.ui.theme import load_stylesheet


def tool_icon(kind):
    pixmap = QPixmap(40, 40)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(2, 2)
    painter.setPen(QPen(QColor("#c1cbd7"), 1.4, Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    if kind == "position":
        painter.drawLine(2, 10, 18, 10)
        painter.drawLine(10, 2, 10, 18)
        for a, b in (((2, 10), (5, 7)), ((2, 10), (5, 13)),
                     ((18, 10), (15, 7)), ((18, 10), (15, 13)),
                     ((10, 2), (7, 5)), ((10, 2), (13, 5)),
                     ((10, 18), (7, 15)), ((10, 18), (13, 15))):
            painter.drawLine(*a, *b)
    elif kind == "rotation":
        painter.drawArc(3, 3, 14, 14, 50 * 16, 285 * 16)
        painter.drawLine(14, 2, 17, 5)
        painter.drawLine(17, 5, 13, 7)
    elif kind == "scale":
        painter.drawRect(3, 10, 7, 7)
        painter.drawLine(8, 12, 17, 3)
        painter.drawLine(12, 3, 17, 3)
        painter.drawLine(17, 3, 17, 8)
    else:
        for points in (((2, 7), (2, 2), (7, 2)), ((13, 2), (18, 2), (18, 7)),
                       ((18, 13), (18, 18), (13, 18)), ((7, 18), (2, 18), (2, 13))):
            painter.drawLine(*points[0], *points[1])
            painter.drawLine(*points[1], *points[2])
        if kind == "frame_scene":
            painter.drawRect(5, 8, 4, 6)
            painter.drawRect(11, 6, 4, 8)
        else:
            painter.drawLine(7, 10, 13, 10)
            painter.drawLine(10, 7, 10, 13)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)


def create_viewport_tools(window, focus_transform, frame_selected, frame_scene):
    toolbar = QToolBar("Viewport Tools", window)
    toolbar.setObjectName("editor.tools")  # Retain the existing workspace identity.
    toolbar.setMovable(False)
    toolbar.setFloatable(False)
    toolbar.setAllowedAreas(Qt.ToolBarArea.LeftToolBarArea | Qt.ToolBarArea.RightToolBarArea)
    toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
    toolbar.setIconSize(QSize(20, 20))
    toolbar.setStyleSheet(load_stylesheet("viewport_tools"))
    window.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)

    def section(title):
        label = QLabel(title)
        label.setObjectName("toolGroupLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.addWidget(label)

    section("EDIT")
    transforms = {}
    for attribute, title in (("position", "Edit Position"), ("rotation", "Edit Rotation"), ("scale", "Edit Scale")):
        action = QAction(tool_icon(attribute), title, toolbar)
        action.setToolTip(f"{title}\nOpen the {attribute} fields in Properties for the selected objects")
        action.setStatusTip(f"Edit selected objects' {attribute} in Properties")
        action.triggered.connect(lambda checked=False, attribute=attribute: focus_transform(attribute))
        toolbar.addAction(action)
        transforms[attribute] = action
    toolbar.addSeparator()
    section("VIEW")
    for action, kind, tooltip in (
        (frame_selected, "frame_selected", "Frame Selected (F)\nFit the visible selection in the viewport"),
        (frame_scene, "frame_scene", "Frame Scene (Shift+F)\nFit all visible scene objects in the viewport"),
    ):
        action.setIcon(tool_icon(kind))
        action.setToolTip(tooltip)
        toolbar.addAction(action)
    for action in (*transforms.values(), frame_selected, frame_scene):
        button = toolbar.widgetForAction(action)
        button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        button.setAccessibleName(action.text())
    return toolbar, transforms
