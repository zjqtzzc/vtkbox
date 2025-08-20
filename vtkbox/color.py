import random
from typing import overload, Sequence

import numpy
import vtk



_build_in_color = [
    (0, 255, 128),
    (76, 54, 245),
    (245, 213, 17),
    (245, 32, 5)
]
_build_in_color_iter = iter(_build_in_color)

def get_a_great_color():
    global _build_in_color_iter
    try:
        color = _build_in_color_iter.__next__()
    except StopIteration: # 如果build in color 取完了，就随机改变亮度再取一轮
        scale = random.random()
        if random.randint(0, 1):
            new_color = [[round(c * scale) for c in color] for color in _build_in_color]
        else:
            new_color = [[255 - round((255 - c)*scale) for c in color] for color in _build_in_color]
        _build_in_color_iter = iter(new_color)
        color = _build_in_color_iter.__next__()
    return color255_to_1(color)

def get_rand_color():
    return random.random(), random.random(), random.random()


@overload
def color255_to_1(rgb: Sequence[int]): ...


@overload
def color255_to_1(r: int, g: int, b: int): ...


def color255_to_1(*args):
    if len(args) == 1:
        r, g, b = args[0]
    elif len(args) == 3:
        r, g, b = args
    else:
        raise TypeError("未找到匹配的实现")
    return r / 255, g / 255, b / 255


def vtk_color_from_intensity(intensity: numpy.ndarray):
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")

    def intensity_to_rgb(inte_: float):
        c = numpy.array([0, 255, 255])
        m = numpy.array([255, 0, 255])
        y = numpy.array([255, 255, 0])
        if inte_ < 0:
            rgb = c
        elif inte_ < 0.5:
            rgb = c * (0.5 - inte_) / 0.5 + y * inte_ / 0.5
        elif inte_ < 1:
            rgb = y * (1 - inte_) / 0.5 + m * (inte_ - 0.5) / 0.5
        else:
            rgb = m
        return rgb.astype(int)

    unit_i = intensity / intensity.max()
    for i in unit_i:
        colors.InsertNextTuple3(*intensity_to_rgb(i))
    return colors
