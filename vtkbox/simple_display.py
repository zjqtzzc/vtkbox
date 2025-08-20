import numpy as np
from vtkmodules import all as vtk

from .color import get_rand_color, get_a_great_color
from .actor_creator import point_actor, source_actor

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


def vtk_show(*args, with_color=False):
    # clear old actor
    _display_component.renderer.RemoveAllViewProps()
    # init color
    if with_color:
        color = get_a_great_color()
    else:
        color = (1.0, 1.0, 1.0)
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
