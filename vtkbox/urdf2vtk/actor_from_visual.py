import os
import warnings
from math import degrees, ceil, sqrt
from typing import Optional, List

from urdf_parser_py.urdf import Visual, Box, Cylinder, Sphere, Material, Mesh, Collision
from vtkmodules import all as vtk

class ActorCreator:
    rm_mesh_package_name = True
    def __init__(self, mesh_root: str):
        self._material_map = {}
        self._mesh_root = mesh_root

    def register_material(self, materials: List[Material]):
        for material in materials:
            self._material_map[material.name] = material.color.rgba

    def get_mesh_filepath(self, mesh_url: str):
        # 检查 URI 是否合理
        assert mesh_url.startswith('package://'), "URI does not start with 'package://'"

        path = mesh_url[len('package://'):]
        # 分离包名和相对路径
        if self.rm_mesh_package_name:
            path = path.split('/', 1)[1]

        full_path = os.path.join(self._mesh_root, path)
        return full_path

    def paser_visual(self, visual: Visual) -> Optional[vtk.vtkActor]:
        actor = self._create_actor(getattr(visual, "geometry", None), getattr(visual, "origin", None))
        if actor is None:
            return None
        # 染色
        prop: vtk.vtkProperty = actor.GetProperty()
        if hasattr(visual, "material") and visual.material:
            if visual.material.color is not None:
                r, g, b, a = visual.material.color.rgba
                prop.SetColor(r, g, b)
                prop.SetOpacity(a)
            elif visual.material.name is not None:
                r, g, b, a = self._material_map[visual.material.name]
                prop.SetColor(r, g, b)
                prop.SetOpacity(a)
        return actor

    def paser_collision(self, collision: Collision) -> Optional[vtk.vtkActor]:
        actor = self._create_actor(getattr(collision, "geometry", None), getattr(collision, "origin", None), True)
        if actor is None:
            return None

        prop: vtk.vtkProperty = actor.GetProperty()
        prop.SetOpacity(0.5)
        return actor

    def _create_actor(self, geometry, origin, capsule=False) -> Optional[vtk.vtkActor]:
        if isinstance(geometry, Box):
            source = box_source(geometry.size)
        elif isinstance(geometry, Cylinder):
            if capsule:
                source = capsule_source(geometry.length, geometry.radius)
            else:
                source = cylinder_source(geometry.length, geometry.radius)
        elif isinstance(geometry, Sphere):
            source = sphere_source(geometry.radius)
        elif isinstance(geometry, Mesh):
            source = mesh_source(self.get_mesh_filepath(geometry.filename), geometry.scale)
        else:
            warnings.warn(f'Unknown geometry type: {type(geometry)}')
            return None

        # rpy 生效顺序为 zyx
        transform = vtk.vtkTransform()
        if hasattr(origin, 'xyz') and origin.xyz:
            transform.Translate(*origin.xyz)
        if hasattr(origin, 'rpy') and origin.rpy:
            r, p, y = origin.rpy
            transform.RotateZ(degrees(y))
            transform.RotateY(degrees(p))
            transform.RotateX(degrees(r))

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetTransform(transform)
        transform_filter.SetInputConnection(source.GetOutputPort())

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transform_filter.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        return actor

def box_source(size: list):
    source = vtk.vtkCubeSource()
    x, y, z = size
    source.SetXLength(x)
    source.SetYLength(y)
    source.SetZLength(z)
    return source

def cylinder_source(length: float, radius: float):
    source = vtk.vtkCylinderSource()
    source.SetHeight(length)
    source.SetRadius(radius)
    resolution = max(6, ceil(sqrt(radius) // 0.006))
    source.SetResolution(resolution)

    # urdf cylinder z轴对称，vtk为y轴对称
    transform = vtk.vtkTransform()
    transform.RotateX(90)

    filter = vtk.vtkTransformPolyDataFilter()
    filter.SetInputConnection(source.GetOutputPort())
    filter.SetTransform(transform)
    return filter

def capsule_source(length: float, radius: float):
    import vtk, math

    # 【构造胶囊体轮廓：在 x-z 平面构造右侧半边轮廓】
    # 轮廓包含三部分：
    # 1. 底部四分之一圆弧，从 (0, -length/2 - radius) 到 (radius, -length/2)
    # 2. 中间竖直线，从 (radius, -length/2) 到 (radius, length/2)
    # 3. 顶部四分之一圆弧，从 (radius, length/2) 到 (0, length/2 + radius)
    points = vtk.vtkPoints()
    polyLine = vtk.vtkPolyLine()
    point_id = 0

    # 底部四分之一圆弧
    nArc = 20  # 弧上点数
    for i in range(nArc + 1):
        t = i / nArc
        theta = t * (math.pi / 2)  # 从 0 到 π/2
        x = radius * math.sin(theta)
        z = -length / 2 - radius * math.cos(theta)
        points.InsertNextPoint(x, 0, z)  # 轮廓在 x-z 平面，y=0
        point_id += 1

    # 中间竖直线（不重复两端点）
    nLine = 20
    for i in range(1, nLine):
        t = i / nLine
        x = radius
        z = -length / 2 + t * length
        points.InsertNextPoint(x, 0, z)
        point_id += 1

    # 顶部四分之一圆弧
    for i in range(nArc + 1):
        t = i / nArc
        theta = (math.pi / 2) * (1 - t)  # 从 π/2 到 0
        x = radius * math.sin(theta)
        z = length / 2 + radius * math.cos(theta)
        points.InsertNextPoint(x, 0, z)
        point_id += 1

    polyLine.GetPointIds().SetNumberOfIds(point_id)
    for i in range(point_id):
        polyLine.GetPointIds().SetId(i, i)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyLine)

    profile = vtk.vtkPolyData()
    profile.SetPoints(points)
    profile.SetLines(cells)

    # 【旋转生成三维胶囊体】
    extrude = vtk.vtkRotationalExtrusionFilter()
    extrude.SetInputData(profile)
    extrude.SetResolution(60)  # 旋转分辨率，可根据需要调整
    extrude.SetAngle(360)      # 完整旋转 360 度
    extrude.Update()

    return extrude

def sphere_source(radius: float):
    source = vtk.vtkSphereSource()
    source.SetRadius(radius)
    phi_resolution = max(6, ceil(sqrt(radius) // 0.012))
    theta_resolution = max(6, ceil(sqrt(radius) // 0.008))
    source.SetPhiResolution(phi_resolution)
    source.SetThetaResolution(theta_resolution)
    return source

def mesh_source(file_path, scale):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(file_path)
    if scale is None:
        return reader
    else:
        transform = vtk.vtkTransform()
        transform.Scale(scale)

        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputConnection(reader.GetOutputPort())
        transformFilter.SetTransform(transform)
        # transformFilter.Update()
        return transformFilter

