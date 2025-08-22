import time
from multiprocessing import Process, Queue
from queue import Empty

import vtk

from .visualizer import VTKVisualizer


class _RemoteProcedureCallClient:
    def __init__(self, request: Queue, path=tuple()):
        self.__request = request
        self.__path = path

    def __getattr__(self, item):
        return _RemoteProcedureCallClient(self.__request, self.__path + (item,))

    def __call__(self, *args, **kwargs):
        self.__request.put((self.__path, args, kwargs))


def sub_main(request: Queue):
    viz = VTKVisualizer()

    def handle(obj, event):
        while True:
            try:
                t0 = time.time()
                path, args, kwargs = request.get_nowait()
                t1 = time.time()
            except Empty:
                break
            target = viz
            for p in path:
                target = getattr(target, p)
            target(*args, **kwargs)
            t2 = time.time()
            print(f'get cost {t1-t0:.3f}s, call cost {t2-t1:.3f}s')

        obj.Render()

    viz._viz.interactor.AddObserver(vtk.vtkCommand.TimerEvent, handle)
    viz._viz.interactor.CreateRepeatingTimer(20)

    while viz._viz.render_window.GetNeverRendered():
        path, args, kwargs = request.get()
        target = viz
        for p in path:
            target = getattr(target, p)
        target(*args, **kwargs)


def create_visualizer_subprocess() -> VTKVisualizer:
    q_request = Queue()
    Process(target=sub_main, args=(q_request, )).start()

    return _RemoteProcedureCallClient(q_request)