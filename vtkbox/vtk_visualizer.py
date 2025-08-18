import os
import sys

from simple_display import *
from urdf2vtk import VRobot
from typing import overload


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


class VTKVisualizer:
    def __init__(self):
        self._viz = _DisplayComponent()

        self._robot = None  # type: None | VRobot

    def set_robot(self, urdf_path, mesh_root_path):
        if self._robot is not None:
            self._viz.renderer.RemoveActor(self._robot.root.prop)
        self._robot = VRobot(urdf_path, mesh_root_path)
        self._viz.renderer.AddActor(self._robot.root.prop)
        return self._robot
