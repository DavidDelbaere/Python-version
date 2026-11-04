"""Independent rigid-body scene snapshot, stepped by Bullet at 240 Hz."""
import copy
import math

import numpy as np

from scene import Scene


def quaternion(rotation):
    """Editor rotations are degrees and use Rx * Ry * Rz, as in renderer.py."""
    x, y, z = (math.radians(v)/2 for v in rotation)
    sx, sy, sz = math.sin(x), math.sin(y), math.sin(z)
    cx, cy, cz = math.cos(x), math.cos(y), math.cos(z)
    return (sx*cy*cz + cx*sy*sz, cx*sy*cz - sx*cy*sz,
            cx*cy*sz + sx*sy*cz, cx*cy*cz - sx*sy*sz)


def editor_rotation(matrix):
    r = np.asarray(matrix).reshape(3,3)
    y = math.asin(max(-1, min(1, r[0,2])))
    if abs(math.cos(y)) > 1e-7:
        x, z = math.atan2(-r[1,2],r[2,2]), math.atan2(-r[0,1],r[0,0])
    else:
        x, z = math.atan2(r[2,1],r[1,1]), 0
    return [math.degrees(v) for v in (x,y,z)]


def state_vector(value, label, positive=False):
    result = np.asarray(value, dtype=float)
    if result.shape != (3,) or not np.isfinite(result).all():
        raise ValueError(f"{label} must contain three finite numbers")
    if positive and np.any(result <= 0):
        raise ValueError(f"{label} must be positive for physics rendering")
    return result.tolist()


class PhysicsWorld:
    dt = 1/240

    def __init__(self, source_scene, gravity=-9.81, floor=True):
        # Lazy import keeps editing and saving available without the solver.
        import pybullet as bullet
        self.bullet = bullet
        self.client = bullet.connect(bullet.DIRECT)
        if self.client < 0:
            raise RuntimeError("Could not create physics world")
        self.gravity = gravity
        self.floor = floor
        self.scene = Scene()
        self.initial = []
        self.bodies = []
        self.masses = []
        self.legacy_count = 0
        self.steps = 0
        try:
            for source in source_scene.objects:
                if source.asset is None:
                    continue
                obj = copy.copy(source)
                for name in ("position", "rotation", "velocity", "acceleration", "angularVelocity", "scale"):
                    setattr(obj, name, state_vector(getattr(source,name), f"{source.name}: {name}", name == "scale"))
                self.scene.addObject(obj)
                self.initial.append({name: list(getattr(obj,name)) for name in
                                     ("position", "rotation", "velocity", "angularVelocity", "acceleration")})
            self._build()
        except BaseException:
            self.close()
            raise

    def _build(self):
        b, client = self.bullet, self.client
        b.setTimeStep(self.dt, physicsClientId=client)
        b.setPhysicsEngineParameter(numSolverIterations=80, numSubSteps=4, deterministicOverlappingPairs=1,
                                   restitutionVelocityThreshold=0.05, physicsClientId=client)
        self.set_gravity(self.gravity)
        if self.floor:
            shape = b.createCollisionShape(b.GEOM_PLANE, planeNormal=[0,1,0], physicsClientId=client)
            floor = b.createMultiBody(baseMass=0, baseCollisionShapeIndex=shape, physicsClientId=client)
            # Bullet multiplies contacting coefficients. Neutral floor factors
            # let each part's own coefficient determine floor contact.
            b.changeDynamics(floor,-1,lateralFriction=1,restitution=1,physicsClientId=client)
        for obj in self.scene.objects:
            part = obj.part
            scale = np.asarray(obj.scale)
            if part:
                size = np.asarray(part.size)*scale
                if part.sketch is None and part.features is None:
                    shape = b.createCollisionShape(b.GEOM_BOX,halfExtents=(size/2).tolist(),physicsClientId=client)
                else:
                    mesh = obj.asset.vertices.reshape(-1,6)[:,:3]
                    options = {} if obj.body_type == "dynamic" else {
                        "indices":list(range(len(mesh))), "flags":b.GEOM_FORCE_CONCAVE_TRIMESH,
                    }
                    shape = b.createCollisionShape(b.GEOM_MESH,vertices=mesh.tolist(),meshScale=obj.scale,
                                                  physicsClientId=client,**options)
                mass = part.mass * (float(np.prod(scale)) if part.mass_source == "density" else 1)
                if obj.body_type == "static":
                    mass = 0
                friction = part.friction
            else:
                self.legacy_count += 1
                vertices = obj.asset.vertices.reshape(-1,6)[:,:3]
                dynamic = obj.body_type == "dynamic"
                # Bullet supports moving mesh hulls, while concave triangle
                # meshes must remain static. Do not use static mesh flags for
                # an object that the user has made dynamic.
                mesh_options = {} if dynamic else {
                    "indices": list(range(len(vertices))), "flags": b.GEOM_FORCE_CONCAVE_TRIMESH,
                }
                shape = b.createCollisionShape(b.GEOM_MESH,vertices=vertices.tolist(),
                                              meshScale=obj.scale,physicsClientId=client,**mesh_options)
                mass, friction = (1.0 if dynamic else 0), 0.5
            restitution = obj.restitution
            if not math.isfinite(mass):
                raise ValueError(f"{obj.name}: scaled mass is not finite")
            if shape < 0:
                raise ValueError(f"{obj.name}: could not create collision shape")
            body = b.createMultiBody(baseMass=mass,baseCollisionShapeIndex=shape,
                                     basePosition=obj.position,baseOrientation=quaternion(obj.rotation),
                                     physicsClientId=client)
            if body < 0:
                raise ValueError(f"{obj.name}: could not create rigid body")
            settings = dict(lateralFriction=friction,restitution=restitution,
                            linearDamping=0,angularDamping=0)
            if part and mass and part.sketch is None and part.features is None:
                x,y,z = size
                inertia = [mass*(y*y+z*z)/12,mass*(x*x+z*z)/12,mass*(x*x+y*y)/12]
                if not np.isfinite(inertia).all() or min(inertia) <= 0:
                    raise ValueError(f"{obj.name}: scaled inertia is not finite and positive")
                settings["localInertiaDiagonal"] = inertia
                settings["ccdSweptSphereRadius"] = float(min(size))*0.2
                settings["contactProcessingThreshold"] = 0
            b.changeDynamics(body,-1,physicsClientId=client,**settings)
            b.resetBaseVelocity(body,linearVelocity=obj.velocity if mass else [0,0,0],
                                angularVelocity=obj.angularVelocity if mass else [0,0,0],physicsClientId=client)
            self.bodies.append(body)
            self.masses.append(mass)

    @property
    def time(self):
        return self.steps*self.dt

    def set_gravity(self, value):
        if not math.isfinite(value):
            raise ValueError("Gravity must be finite")
        self.gravity = value
        self.bullet.setGravity(0,value,0,physicsClientId=self.client)

    def step(self, count=1):
        b, client = self.bullet, self.client
        for _ in range(count):
            for obj, body, mass in zip(self.scene.objects,self.bodies,self.masses):
                if mass and any(obj.acceleration):
                    position, _ = b.getBasePositionAndOrientation(body,physicsClientId=client)
                    b.applyExternalForce(body,-1,(np.asarray(obj.acceleration)*mass).tolist(),position,
                                         b.WORLD_FRAME,physicsClientId=client)
            b.stepSimulation(physicsClientId=client)
            self.steps += 1
        self.sync()

    def sync(self):
        b, client = self.bullet, self.client
        for obj, body, mass in zip(self.scene.objects,self.bodies,self.masses):
            if not mass:
                continue
            position, orientation = b.getBasePositionAndOrientation(body,physicsClientId=client)
            linear, angular = b.getBaseVelocity(body,physicsClientId=client)
            obj.position = list(position)
            obj.rotation = editor_rotation(b.getMatrixFromQuaternion(orientation))
            obj.velocity, obj.angularVelocity = list(linear), list(angular)

    def reset(self):
        b, client = self.bullet, self.client
        # Recreate contact manifolds as well as poses for repeatable playback.
        b.resetSimulation(physicsClientId=client)
        self.bodies.clear()
        self.masses.clear()
        self.legacy_count = 0
        self.steps = 0
        for obj, state in zip(self.scene.objects,self.initial):
            for name, value in state.items():
                setattr(obj,name,list(value))
        self._build()

    def close(self):
        if self.client >= 0:
            self.bullet.disconnect(physicsClientId=self.client)
            self.client = -1
