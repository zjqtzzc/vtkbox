import os
import sys
import numpy

from typing import overload, TypeVar
from uuid import uuid4

import vtkmodules.all as vtk

from .urdf2vtk import VRobot
from .color import color255_to_1, get_a_great_color
from .actor_creator import point_actor, source_actor

T = TypeVar('T', vtk.vtkActor, vtk.vtkProp3D)


class _DisplayComponent:
    def __init__(self):
        # renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(*color255_to_1(0x0a, 0x19, 0x2f))

        # 初始使用透视投影
        self.is_perspective = True

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

        # 设置按键观察者，处理键盘事件
        self.interactor.AddObserver("KeyPressEvent", self._key_press_event)

    def _key_press_event(self, obj, event):
        """处理键盘按键事件"""
        key = self.interactor.GetKeySym()

        # 按下"o"键切换透视/平行投影
        if key.lower() == "o":
            self.toggle_perspective()

    def toggle_perspective(self):
        """切换相机的透视/平行投影模式"""
        camera = self.renderer.GetActiveCamera()

        if self.is_perspective:
            # 切换到平行投影
            camera.ParallelProjectionOn()
        else:
            # 切换到透视投影
            camera.ParallelProjectionOff()

        # 更新状态标志
        self.is_perspective = not self.is_perspective

        # 重新渲染以显示更改
        self.render_window.Render()

        # 可以在这里添加状态提示，例如打印当前模式
        mode = "透视" if self.is_perspective else "平行"
        print(f"已切换到{mode}投影模式")


_global_display_component = _DisplayComponent()


def vtk_show(*args, with_color=False):
    _global_display_component.renderer.RemoveAllViewProps()
    # init color
    if with_color:
        color = get_a_great_color()
    else:
        color = (1.0, 1.0, 1.0)
    # Insert Actor
    for item in args:
        if isinstance(item, (list, numpy.ndarray)):
            actor = point_actor(item, color)
        elif issubclass(type(item), vtk.vtkPolyDataAlgorithm):
            actor = source_actor(item)
        else:
            actor = item
        _global_display_component.renderer.AddActor(actor)
    _global_display_component.interactor.Initialize()
    _global_display_component.interactor.Start()


class VTKVisualizer:
    def __init__(self):
        self._viz = _DisplayComponent()

        self.robot = None  # type: None | VRobot
        # actor 检索表
        self._actor_map = {}  # type: dict[int, vtk.vtkProp] # actor 检索表， 不包括robot
        self._actor_name_map = {}  # type: dict[str, int]

    def show(self):
        self._viz.interactor.Initialize()
        self._viz.interactor.Start()

    def set_robot(self, urdf_path: str, mesh_root_path: str):
        if self.robot is not None:
            self._viz.renderer.RemoveActor(self.robot.root.prop)
        self.robot = VRobot(urdf_path, mesh_root_path)
        self._viz.renderer.AddActor(self.robot.root.prop)
        return self.robot

    def add_actor(self, actor: T, name: str = None) -> tuple[int, T]:
        uid = uuid4().int
        if name is not None:
            if name in self._actor_name_map:
                raise ValueError(f"actor name conflict: {name}")
            self._actor_name_map[name] = uid

        self._actor_map[uid] = actor
        self._viz.renderer.AddActor(actor)
        return uid, actor

    @overload
    def get_actor(self, name: str) -> vtk.vtkActor | None:
        ...

    @overload
    def get_actor(self, uid: int) -> vtk.vtkActor | None:
        ...

    def get_actor(self, arg):
        if isinstance(arg, str):
            uid = self._actor_name_map.get(arg, None)
        else:
            uid = arg
        actor = self._actor_map.get(uid, None)
        return actor

    @overload
    def remove_actor(self, name: str) -> None:
        ...

    @overload
    def remove_actor(self, uid: int) -> None:
        ...

    def remove_actor(self, arg):
        if isinstance(arg, str):
            uid = self._actor_name_map.pop(arg, None)
        else:
            uid = arg
        actor = self._actor_map.pop(uid, None)
        if actor is None:
            print(f'无法移除 {arg}, 对象不存在')
            return
        self._viz.renderer.RemoveActor(actor)

    def add_points(self, points: list | numpy.ndarray, color: tuple[float, float, float] = (1, 1, 1), point_size=3,
                   name: str = None) -> tuple[int, vtk.vtkActor]:
        actor = point_actor(points, color, point_size)
        return self.add_actor(actor, name)

    def add_box(self, xmin, xmax, ymin, ymax, zmin, zmax, opacity: float = 1, name: str = None) -> tuple[
        int, vtk.vtkActor]:
        cube_source = vtk.vtkCubeSource()
        cube_source.SetBounds([xmin, xmax, ymin, ymax, zmin, zmax])
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube_source.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opacity)
        return self.add_actor(actor, name)
