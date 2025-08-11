from vtkmodules import all as vtk
import numpy

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


class VJoint:
    TYPE = ['continuous', 'revolute', 'prismatic', 'fixed', 'floating', 'planar']

    def __init__(self, name='', type='unknown', parent='', child='', origin_xyz: list = None,
                 origin_rpy: list = None, axis: list = None):
        # input check
        assert type in VJoint.TYPE, f'Joint {name} type error: {type}'
        assert parent, f'Joint {name} must have parent'
        assert child, f'Joint {name} must have child'
        if origin_xyz is None:
            origin_xyz = [0, 0, 0]
        if origin_rpy is None:
            origin_rpy = [0, 0, 0]
        if axis is None:
            axis = [0, 0, 1]
        # trans axis into unit vector
        axis = numpy.array(axis)
        norm = numpy.linalg.norm(axis)
        if norm == 0:
            raise ValueError(f'Joint {name} axis can\'t be zero')
        axis = axis / norm
        # input params
        self.name = name
        self.type = type
        self.parent = parent
        self.child = child
        self.origin_xyz = origin_xyz
        self.origin_rpy = origin_rpy
        self.axis = axis
        #
        self.prop = vtk.vtkAssembly()
        #
        self.set_pose(origin_xyz, origin_rpy)

    def set_pose(self, xyz, rpy):
        x, y, z = xyz
        roll, pitch, yaw = numpy.degrees(rpy)

        trans = vtk.vtkTransform()
        trans.Translate(x, y, z)
        trans.RotateZ(yaw)
        trans.RotateY(pitch)
        trans.RotateX(roll)

        self.prop.SetUserTransform(trans)

    def set_pose_2(self, xyz, wxyz):

        q = vtk.vtkQuaterniond()
        q.Set(*wxyz)
        rot_matrix = [[0, 0, 0, ], [0, 0, 0], [0, 0, 0]]
        q.ToMatrix3x3(rot_matrix)

        matrix4x4 = vtk.vtkMatrix4x4()
        matrix4x4.Identity()

        for i in range(3):
            for j in range(3):
                matrix4x4.SetElement(i, j, rot_matrix[i][j])
            matrix4x4.SetElement(i, 3, xyz[i])

        self.prop.SetUserMatrix(matrix4x4)
