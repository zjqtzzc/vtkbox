from vtk import vtkAxesActor
from .vjoint import VLink


class RobotAxes:
    def __init__(self, links: dict[str, 'VLink']):
        self._axes = []
        for link in links.values():
            axes = vtkAxesActor()
            axes.AxisLabelsOff()
            axes.SetTotalLength(0.2, 0.2, 0.2)
            link.prop.AddPart(axes)
            self._axes.append(axes)

    def set_visible(self, value: bool):
        for axes in self._axes:
            axes.SetVisibility(value)
