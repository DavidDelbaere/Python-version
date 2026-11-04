from pathlib import Path

from part_assets import load_asset
from part_format import number, vector


class SceneObject:
    def __init__(self, name="Object", meshPath=None):
        self.name = name
        self.meshPath = meshPath

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
        self._restitution = None
        self._body_type = None

        self.asset = None
        self.part = None
        if meshPath is not None:
            self.asset = load_asset(meshPath)
            self.part = self.asset.part
            if self.part is not None:
                self.position = list(self.part.position)
                self.velocity = list(self.part.velocity)
            if name == "Object":
                self.name = self.part.name if self.part else Path(meshPath).stem

    # -------------------------------------------------
    # Static Functions
    # -------------------------------------------------

    def setPosition(self, x, y, z):
        self.position = [x, y, z]

    def setRotation(self, x, y, z):
        self.rotation = [x, y, z]

    def setVelocity(self, x, y, z):
        self.velocity = [x, y, z]

    @property
    def restitution(self):
        if self._restitution is not None:
            return self._restitution
        return self.part.restitution if self.part is not None else 0.0

    @restitution.setter
    def restitution(self, value):
        self._restitution = number(value, "Bounce", minimum=0, maximum=1)

    @property
    def body_type(self):
        if self._body_type is not None:
            return self._body_type
        return self.part.body_type if self.part is not None else "static"

    @body_type.setter
    def body_type(self, value):
        if value not in ("static", "dynamic"):
            raise ValueError("Body type must be static or dynamic")
        self._body_type = value

    def setPhysicsProperties(self, bounce, velocity, body_type=None):
        bounce = number(bounce, "Bounce", minimum=0, maximum=1)
        velocity = vector(velocity, "Velocity")
        if body_type is not None and body_type not in ("static", "dynamic"):
            raise ValueError("Body type must be static or dynamic")
        self.restitution = bounce
        self.velocity = list(velocity)
        if body_type is not None:
            self.body_type = body_type

    def setAcceleration(self, x, y, z):
        self.acceleration = [x, y, z]


class Scene:
    def __init__(self):
        self.filepath = None
        self.objects = []
        self.dirty = False

    def addObject(self, obj):
        self.objects.append(obj)
    
    def sceneHasObjects(self):
        for sceneObject in self.objects:
            return True

        return False
