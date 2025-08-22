from vtkmodules import all as vtk
import numpy
from urdf_parser_py.urdf import Robot as URobot, Joint as UJoint, Link as ULink


class VLink:
    def __init__(self, name, visual: list[vtk.vtkActor], collision: list[vtk.vtkActor]):
        self.name = name
        self.prop = vtk.vtkAssembly()
        self.parent: str = None
        self.children = []  # type: list[str]

        self._visual = visual
        self._collision = collision

        for actor in self._visual:
            self.prop.AddPart(actor)
        for actor in self._collision:
            self.prop.AddPart(actor)


        self._total_visible = True
        self._collision_visible = False
        self._update_visibility()

    def set_visibility(self, value: bool):
        self._total_visible = value
        self._update_visibility()

    def set_collision_visibility(self, value: bool):
        self._collision_visible = value
        self._update_visibility()

    def _update_visibility(self):
        for actor in self._visual:
            actor.SetVisibility(self._total_visible)
        for actor in self._collision:
            actor.SetVisibility(self._collision_visible and self._total_visible)


class _MimicData:
    joint: str
    multiplier: float
    offset: float

class VJoint:
    TYPE = ['continuous', 'revolute', 'prismatic', 'fixed', 'floating', 'planar']

    prop: vtk.vtkAssembly

    name: str
    type: str
    parent: str
    child: str
    origin_xyz: numpy.ndarray
    origin_rpy: numpy.ndarray
    axis: numpy.ndarray
    # optional
    mimic: _MimicData = None

    def __init__(self):
        self.prop = vtk.vtkAssembly()

    def set_input(self, ujoint: UJoint):
        assert ujoint.type in VJoint.TYPE, f'Joint {ujoint.name} type error: {type}'
        self.name = ujoint.name
        self.type = ujoint.type
        self.parent = ujoint.parent
        self.child = ujoint.child
        self.origin_xyz = numpy.array(ujoint.origin.xyz)
        self.origin_rpy = numpy.array(ujoint.origin.rpy)
        self.axis = numpy.array(ujoint.axis)
        self._set_static_transform(self.origin_xyz, self.origin_rpy)
        #
        if ujoint.mimic:
            self.mimic = _MimicData()
            self.mimic.joint = ujoint.mimic.joint
            self.mimic.multiplier = ujoint.mimic.multiplier
            self.mimic.offset = ujoint.mimic.offset

    def _set_static_transform(self, xyz, rpy):
        x, y, z = xyz
        roll, pitch, yaw = numpy.degrees(rpy)
        trans = vtk.vtkTransform()
        trans.Translate(x, y, z)
        trans.RotateZ(yaw)
        trans.RotateY(pitch)
        trans.RotateX(roll)
        self.prop.SetUserTransform(trans)

    def _update(self, pos: float):
        if self.type == 'prismatic':
            vector = self.axis * pos
            self.prop.SetPosition(vector)
        else:
            vector = self.axis * numpy.rad2deg(pos)
            self.prop.SetOrientation(vector)

    def update(self, pos: float):
        if self.mimic:
            print(f'Warning Mimic {self.name} to {self.mimic.joint}; Cannot update self')
            return
        self._update(pos)

    def update_mimic(self, pos: float):
        if not self.mimic:
            print(f'Warning Joint {self.name} has no mimic')
            return
        target = pos * self.mimic.multiplier + self.mimic.offset
        self._update(target)