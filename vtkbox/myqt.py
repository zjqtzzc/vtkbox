import math

from PyQt6.QtWidgets import QSlider


class MyFloatSlider(QSlider):
    """
    支持浮点数值的QSlider子类，通过自动缩放因子实现浮点值与整数滑块的转换。
    
    主要特性:
    - 自动计算合适的缩放因子以确保精度(默认4k)
    - 重写value()方法返回浮点值
    - 重写setValue()接受浮点值输入
    - 支持浮点范围和刻度间隔设置
    
    属性:
        _scale (int): 内部缩放因子，用于将浮点值转换为整数进行滑块操作
    """
    _scale = 10

    def setRange(self, min: float, max: float):
        self._scale = math.pow(2, 12 - round(math.log2(max - min)))
        super().setRange(round(min * self._scale), round(max * self._scale))

    def value(self):
        return super().value() / self._scale

    def setValue(self, value: float):
        super().setValue(round(value * self._scale))

    def setTickInterval(self, interval: float):
        super().setTickInterval(round(interval * self._scale))