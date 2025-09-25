from multiprocessing import Process, Queue
from queue import Empty
from typing import Any, Union
import vtk
import numpy
from .visualizer import VTKVisualizer
from .urdf2vtk.vtk_struct import VRobot


class VTKVisualizerRemote:
    """接口类，不应直接实例化。使用 create_visualizer_subprocess() 获取实例。"""
    robot: VRobot
    def __new__(cls, *args, **kwargs):
        raise TypeError("VTKVisualizerRemote 不应直接实例化，请使用 create_visualizer_subprocess()")
    def show(self) -> None: pass
    def set_robot(self, urdf_path: str, mesh_root_path: str) -> None: pass
    def add_actor(self, actor: Any, name: str = None) -> None: pass
    def get_actor(self, name: str) -> None: pass
    def remove_actor(self, name: str) -> None: pass
    def add_points(self, points: Union[list, numpy.ndarray], color: tuple[float, float, float] = (1, 1, 1), point_size: int = 3, name: str = None) -> None: pass
    def add_points_with_intensity(self, points: Union[list, numpy.ndarray], point_size: int = 3, name: str = None) -> None: pass
    def add_box(self, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, opacity: float = 1, name: str = None) -> None: pass
    def add_line(self, points: Union[list, numpy.ndarray], color: tuple[float, float, float] = (1, 1, 1), line_width: int = 8, name: str = None) -> None: pass
    def set_visible(self, name: str, visible: bool) -> None: pass


class _RemoteProcedureCallClient:
    def __init__(self, request: Queue, path: tuple = ()):
        self.__request = request
        self.__path = path
    def __getattr__(self, item: str):
        return _RemoteProcedureCallClient(self.__request, self.__path + (item,))
    def __call__(self, *args, **kwargs) -> None:
        self.__request.put((self.__path, args, kwargs))


def sub_main(request: Queue) -> None:
    viz = VTKVisualizer()
    def handle_timer_event(obj, event) -> None:
        while True:
            try:
                path, args, kwargs = request.get_nowait()
            except Empty:
                break
            target = viz
            for p in path:
                target = getattr(target, p)
            target(*args, **kwargs)
        obj.Render()
    viz._viz.interactor.AddObserver(vtk.vtkCommand.TimerEvent, handle_timer_event)
    viz._viz.interactor.CreateRepeatingTimer(20)
    while viz._viz.render_window.GetNeverRendered():
        path, args, kwargs = request.get()
        target = viz
        for p in path:
            target = getattr(target, p)
        target(*args, **kwargs)


def create_visualizer_subprocess() -> VTKVisualizerRemote:
    q_request = Queue()
    Process(target=sub_main, args=(q_request,)).start()
    return _RemoteProcedureCallClient(q_request)
