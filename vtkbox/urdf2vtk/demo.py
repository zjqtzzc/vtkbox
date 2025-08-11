from vtkbox.urdf2vtk import VRobot
import os

robot = VRobot(os.path.expanduser("~/PycharmProjects/Pinocchio/0808URDF/urdf/000_urdf.SLDASM.urdf"),
               os.path.expanduser("~/PycharmProjects/Pinocchio/0808URDF"))

from vtkbox.simple_display import vtk_show

vtk_show(robot.root.prop)
