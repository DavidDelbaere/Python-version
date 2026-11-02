"""A shared recording viewport for editor tests without a graphics driver."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget


class FakeViewport(QWidget):
    """Record scene updates without requiring a graphics driver."""

    object_picked = Signal(object)
    frame_requested = Signal()
    escape_requested = Signal()

    def __init__(self, parent, scene):
        super().__init__(parent)
        self.rendered = list(scene.objects)
        self.scene = scene
        self.pick_modifiers = Qt.NoModifier
        self.update_count = 0
        self.selected_object_id = None
        self.framed_object = None

    def frame_object(self, obj):
        self.framed_object = obj

    def set_selected_object(self, obj):
        self.selected_object_id = obj.identifier if obj is not None else None

    def set_selected_objects(self, objects):
        self.selected_object_ids = {obj.identifier for obj in objects}
        self.set_selected_object(objects[-1] if objects else None)

    def sync_scene_objects(self):
        self.rendered = list(self.scene.objects)

    def update(self):
        self.update_count += 1
        super().update()

    def clearRenderObjects(self):
        self.rendered.clear()

    def addNewObject(self, obj):
        self.rendered.append(obj)
