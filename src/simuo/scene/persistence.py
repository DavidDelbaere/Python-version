"""Read/write .simuO data without depending on Qt or the renderer."""

import json
from pathlib import Path

from simuo.scene.model import SceneGroup, SceneObject


def load_project(path):
    """Return objects, groups, and root order, including legacy-file defaults."""
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    objects = []
    for entry in data.get("objects", []):
        obj = SceneObject(
            name=entry["name"],
            meshPath=Path(entry["meshPath"]) if entry.get("meshPath") else None,
            identifier=entry.get("id"),
        )
        editor = entry.get("editor", {})
        if isinstance(editor, dict):
            visible = editor.get("visible", True)
            locked = editor.get("selection_locked", False)
            obj.editor_visible = visible if isinstance(visible, bool) else True
            obj.selection_locked = locked if isinstance(locked, bool) else False
        position = entry.get("position", [0.0, 0.0, 0.0])
        rotation = entry.get("rotation", [0.0, 0.0, 0.0])
        scale = entry.get("scale", [1.0, 1.0, 1.0])
        obj.setPosition(position[0], position[1], position[2])
        obj.setRotation(rotation[0], rotation[1], rotation[2])
        obj.scale = [scale[0], scale[1], scale[2]]
        objects.append(obj)

    groups = []
    entries = data.get("groups", [])
    for entry in entries if isinstance(entries, list) else []:
        if not isinstance(entry, dict):
            continue
        group = SceneGroup(str(entry.get("name", "Group")), identifier=entry.get("id"))
        members = entry.get("objects", [])
        group.members = members if isinstance(members, list) else []
        for attribute, field, default in (
            ("expanded", "expanded", True),
            ("editor_visible", "visible", True),
            ("selection_locked", "selection_locked", False),
        ):
            value = entry.get(field, default)
            setattr(group, attribute, value if isinstance(value, bool) else default)
        groups.append(group)
    roots = data.get("hierarchy_order", [])
    return objects, groups, roots if isinstance(roots, list) else []


def save_project(scene, path):
    """Save the existing version-1 format; let the caller handle write errors."""
    data = {
        "version": 1,
        "objects": [
            {
                "id": obj.identifier,
                "name": obj.name,
                "meshPath": str(obj.meshPath) if obj.meshPath is not None else None,
                "position": list(obj.position),
                "rotation": list(obj.rotation),
                "scale": list(obj.scale),
                "editor": {"visible": obj.editor_visible, "selection_locked": obj.selection_locked},
            }
            for obj in scene.objects
        ],
        "groups": [
            {
                "id": group.identifier,
                "name": group.name,
                "objects": list(group.members),
                "expanded": group.expanded,
                "visible": group.editor_visible,
                "selection_locked": group.selection_locked,
            }
            for group in scene.groups
        ],
        "hierarchy_order": list(scene.root_order),
    }
    Path(path).write_text(json.dumps(data, indent=4), encoding="utf-8")
