import numpy
from vtkmodules import all as vtk
from vtkmodules.util.numpy_support import numpy_to_vtk

from .color import vtk_color_from_intensity


def point_actor(points: vtk.vtkPoints | list | numpy.ndarray,
                color: tuple[float, float, float] = (1, 1, 1),
                point_size=3):
    vtk_points = None
    if isinstance(points, list):
        points = numpy.array(points)
        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(points))
    elif isinstance(points, numpy.ndarray):
        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(points))
    elif isinstance(points, vtk.vtkPoints):
        vtk_points = points
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.EmissiveOff()
    mapper.SetScaleFactor(0.0)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetPointSize(point_size)
    return actor


def point_actor_with_intensity(points: list | numpy.ndarray, point_size=3):
    if isinstance(points, list):
        points = numpy.array(points)
    xyz_arr = points[:, :3]
    i_arr = points[:, 3]
    colors = vtk_color_from_intensity(i_arr)

    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(xyz_arr))
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    polydata.GetPointData().SetScalars(colors)
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.EmissiveOff()
    mapper.SetScaleFactor(0.0)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(point_size)
    return actor


def line_actor(points: vtk.vtkPoints | list | numpy.ndarray,
               color: tuple[float, float, float] = (1, 1, 1),
               line_width=8):
    vtk_points = None
    if isinstance(points, list):
        points = numpy.array(points)
        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(points))
    elif isinstance(points, numpy.ndarray):
        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(points))
    elif isinstance(points, vtk.vtkPoints):
        vtk_points = points
    line_source = vtk.vtkPolyLineSource()
    line_source.SetPoints(vtk_points)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(line_source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetLineWidth(line_width)
    return actor


def source_actor(source):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def poly_actor(polydata, v_filter=False):
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()

    if v_filter:
        v_filter = vtk.vtkVertexGlyphFilter()
        v_filter.SetInputData(polydata)
        mapper.SetInputConnection(v_filter.GetOutputPort())
    else:
        mapper.SetInputData(polydata)
    actor.SetMapper(mapper)
    return actor


def stl_actor(stl_path_or_reader: str | vtk.vtkSTLReader):
    if type(stl_path_or_reader) is str:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_path_or_reader)
    elif stl_path_or_reader.IsA('vtkSTLReader'):
        reader = stl_path_or_reader
    else:
        raise TypeError(f'输入stl 类型错误')
    reader.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor
