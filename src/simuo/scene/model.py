"""Scene objects, organizational groups, and their container."""

from uuid import uuid4


class SceneObject:
    """Represent a single mesh instance inside the simulation scene.

    Attributes:
        name: Human-readable label for the object.
        meshPath: Path to the OBJ model used by this object.
        position: [x, y, z] world position.
        rotation: [x, y, z] Euler rotation in degrees.
        scale: [x, y, z] scale factors.
        velocity: Current linear velocity.
        acceleration: Current linear acceleration.
        angularVelocity: Current rotational velocity.
    """

    def __init__(self, name="Object", meshPath=None, identifier=None):
        """Create a new scene object.

        Args:
            name: Display name for the object.
            meshPath: File path to the mesh asset for this object.
            identifier: Persistent ID, generated for new objects and older files.
        """
        self.name = name
        self.meshPath = meshPath
        self.identifier = identifier if isinstance(identifier, str) and identifier else uuid4().hex
        # Editor controls are independent of simulation state.
        self.editor_visible = True
        self.selection_locked = False
        self._group_visible = True
        self._group_locked = False
        self._isolated_out = False

    # -------------------------------------------------
    # Static Properties
    # -------------------------------------------------

        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]

    # -------------------------------------------------
    # Dynamic Properties
    # -------------------------------------------------

        self.velocity = [0.0, 0.0, 0.0]
        self.acceleration = [0.0, 0.0, 0.0]
        self.angularVelocity = [0.0, 0.0, 0.0]

    # -------------------------------------------------
    # Static Functions
    # -------------------------------------------------

    @property
    def viewport_visible(self):
        return self.editor_visible and self._group_visible and not self._isolated_out

    @property
    def viewport_locked(self):
        return self.selection_locked or self._group_locked

    def setPosition(self, x, y, z):
        """Set the object's world-space position.

        Args:
            x: X coordinate.
            y: Y coordinate.
            z: Z coordinate.
        """
        self.position = [x, y, z]

    def setRotation(self, x, y, z):
        """Set the object's Euler rotation angles in degrees.

        Args:
            x: Rotation around the X axis.
            y: Rotation around the Y axis.
            z: Rotation around the Z axis.
        """
        self.rotation = [x, y, z]

    def setVelocity(self, x, y, z):
        """Set the object's linear velocity vector.

        Args:
            x: Velocity along X.
            y: Velocity along Y.
            z: Velocity along Z.
        """
        self.velocity = [x, y, z]

    def setAcceleration(self, x, y, z):
        """Set the object's linear acceleration vector.

        Args:
            x: Acceleration along X.
            y: Acceleration along Y.
            z: Acceleration along Z.
        """
        self.acceleration = [x, y, z]


class SceneGroup:
    """An organizational folder; membership never changes object transforms."""

    def __init__(self, name="Group", identifier=None):
        self.identifier = identifier if isinstance(identifier, str) and identifier else uuid4().hex
        self.name = name
        self.members = []
        self.expanded = True
        self.editor_visible = True
        self.selection_locked = False


class Scene:
    """Container for all objects in the active simulation scene."""

    def __init__(self):
        """Initialize an empty scene.

        Returns:
            Scene: A scene container with no objects.
        """
        self.filepath = None
        self.objects = []
        self.groups = []
        self.root_order = []
        self.dirty = False

    def addObject(self, obj):
        """Append an object to the scene.

        Args:
            obj: A SceneObject instance to add.
        """
        if any(existing.identifier == obj.identifier for existing in self.objects):
            obj.identifier = uuid4().hex
        self.objects.append(obj)
        self.root_order.append(obj.identifier)

    def normalize_hierarchy(self):
        """Repair old/malformed organization without losing any objects."""
        identifiers = {obj.identifier for obj in self.objects}
        used = set(identifiers)
        members = set()
        for group in self.groups:
            if group.identifier in used:
                group.identifier = uuid4().hex
            used.add(group.identifier)
            cleaned = []
            for key in group.members:
                if isinstance(key, str) and key in identifiers and key not in members:
                    cleaned.append(key)
                    members.add(key)
            group.members = cleaned
        valid = used - members
        roots = []
        for key in [*self.root_order, *(group.identifier for group in self.groups),
                    *(obj.identifier for obj in self.objects)]:
            if isinstance(key, str) and key in valid and key not in roots:
                roots.append(key)
        self.root_order = roots

    def sceneHasObjects(self):
        """Check whether the scene contains any objects.

        Returns:
            bool: True if at least one object exists, otherwise False.
        """
        for sceneObject in self.objects:
            return True

        return False
