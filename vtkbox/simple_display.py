import random

import numpy
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules import all as vtk
from typing import Iterable, Union


def color_actor(actor, color):
    if color is True:
        actor.GetProperty().SetColor(random.random(), random.random(), random.random())
    elif isinstance(color, Iterable):
        if sum(color) > 3:
            color = [c / 255 for c in color]
        actor.GetProperty().SetColor(*color)


def intensity_to_rgb(intensity: int):
    c = np.array([0, 255, 255])
    m = np.array([255, 0, 255])
    y = np.array([255, 255, 0])
    if intensity < 0:
        rgb = c
    elif intensity < 128:
        rgb = c * (128 - intensity) / 128 + y * intensity / 128
    elif intensity < 256:
        rgb = y * (256 - intensity) / 128 + m * (intensity - 128) / 128
    else:
        rgb = m
    return rgb.astype(int)


def point_actor(points_list: Union[vtk.vtkPoints, list, np.ndarray], color=False, point_size=3):
    if isinstance(points_list, vtk.vtkPoints):
        points = points_list
    else:
        if isinstance(points_list, list):
            points_list = np.array(points_list)
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(points_list))
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.EmissiveOff()
    mapper.SetScaleFactor(0.0)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    color_actor(actor, color)
    actor.GetProperty().SetPointSize(point_size)
    return actor


def point_actor_with_intensity(points_list: Union[list, np.ndarray], point_size=3):
    p_list = []
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")
    for x, y, z, i in points_list:
        p_list.append([x, y, z])
        colors.InsertNextTuple3(*intensity_to_rgb(i))
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(p_list))
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.GetPointData().SetScalars(colors)
    mapper = vtk.vtkPointGaussianMapper()
    mapper.SetInputData(polydata)
    mapper.EmissiveOff()
    mapper.SetScaleFactor(0.0)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(point_size)
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


def stl_actor(stl_path_or_reader):
    if type(stl_path_or_reader) is str:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(stl_path_or_reader)
    elif stl_path_or_reader.IsA('vtkSTLReader'):
        reader = stl_path_or_reader
    else:
        print('类型错误')
        return
    reader.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def line_actor(points_list: Union[vtk.vtkPoints, list, np.ndarray], color=False, line_width=8):
    if isinstance(points_list, vtk.vtkPoints):
        points = points_list
    else:
        if isinstance(points_list, list):
            points_list = np.array(points_list)
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(points_list))
    line_source = vtk.vtkPolyLineSource()
    line_source.SetPoints(points)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(line_source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    color_actor(actor, color)
    actor.GetProperty().SetLineWidth(line_width)
    return actor


def source_actor(source):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


class _DisplayComponent:
    def __init__(self):
        # renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0, 0, 0)
        # RenderWindow
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetPosition(0, 3000)
        self.render_window.SetSize(3000, 1600)
        # interactor
        self.interactor = vtk.vtkRenderWindowInteractor()
        # connect vtk part
        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleMultiTouchCamera())


_display_component = _DisplayComponent()


def get_display_component():
    return _display_component


def vtk_show(*args, color: Union[bool, Iterable] = False):
    # clear old actor
    _display_component.renderer.RemoveAllViewProps()
    # Insert Actor
    for item in args:
        if isinstance(item, (list, np.ndarray)):
            actor = point_actor(item, color)
        elif issubclass(type(item), vtk.vtkPolyDataAlgorithm):
            actor = source_actor(item)
        else:
            actor = item
        _display_component.renderer.AddActor(actor)
    _display_component.interactor.Initialize()
    _display_component.interactor.Start()


def min_max_nd(source):
    """
    依次返回n维数组各维度的min、max
    例如输入n*3点云，返回xmin, xmax, ymin, ymax, zmin, zmax
    :param source:
    :return:
    """
    if not isinstance(source, numpy.ndarray):
        source = numpy.array(source)
    result = []
    for dim in source.T:
        result.append(numpy.min(dim))
        result.append(numpy.max(dim))
    return tuple(result)



def center_3D(source):
    if type(source) == list:
        source = np.array(source)
    center = source.mean(axis=0)
    return center


def pass_filter(source, axis: str, min=None, max=None, both=False):
    if axis in 'xX0':
        axis = 0
    elif axis in 'yY1':
        axis = 1
    elif axis in 'zZ2':
        axis = 2
    else:
        return source
    if min is None and max is None:
        return source
    elif min is None:
        res_in = [p for p in source if p[axis] <= max]
        res_out = [p for p in source if p[axis] > max]
    elif max is None:
        res_in = [p for p in source if p[axis] >= min]
        res_out = [p for p in source if p[axis] < min]
    else:
        res_in = [p for p in source if max >= p[axis] >= min]
        res_out = [p for p in source if p[axis] < min or p[axis] > max]
    if both:
        return res_in, res_out
    else:
        return res_in


def Up(cloud, distance, axis='y'):
    dict_axis = {
        'x': 0,
        'y': 1,
        'z': 2,
    }
    if axis not in dict_axis:
        return
    for i in cloud:
        i[dict_axis[axis]] += distance


def numpy_cube(size):
    l = []
    for i in range(size):
        for j in range(size):
            for k in range(size):
                l.append([i / size - .5, j / size - .5, k / size - .5])
    return np.array(l)
