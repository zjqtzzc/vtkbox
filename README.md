# vtkbox

VTK 可视化工具库，提供便捷的 VTK 对象构建和显示功能。

## 主要功能

- **点云可视化**: 支持普通点云和带强度信息的点云
- **线可视化**: 支持折线显示
- **几何体**: 支持包围盒、VTK 源对象等
- **机器人模型**: 支持从 URDF 文件加载机器人模型
- **多进程支持**: 支持在独立进程中运行可视化器
- **交互操作**: 支持键盘快捷键（如按 'o' 切换透视/平行投影）

## 主要 API

### vtk_show

快速显示函数，支持点云数组、VTK Actor 或 VTK 源对象。

```python
vtk_show(*args, with_color=False)
```

**示例**:
```python
import vtkbox
import numpy as np

# 显示点云
points = np.random.rand(100, 3)
vtkbox.vtk_show(points, with_color=True)

# 显示多个对象
vtkbox.vtk_show(points1, points2, points3, with_color=True)
```

### VTKVisualizer

完整的可视化器类。

**主要方法**:
- `add_points(points, color=(1, 1, 1), point_size=3, name=None)`: 添加点云
- `add_points_with_intensity(points, point_size=3, name=None)`: 添加带强度信息的点云
- `add_line(points, color=(1, 1, 1), line_width=8, name=None)`: 添加折线
- `add_box(xmin, xmax, ymin, ymax, zmin, zmax, opacity=1, name=None)`: 添加包围盒
- `add_actor(actor, name=None)`: 添加自定义 Actor
- `set_robot(urdf_path, mesh_root_path)`: 加载机器人模型
- `get_actor(name|uid)`: 获取 Actor
- `remove_actor(name|uid)`: 移除 Actor
- `set_visible(name|uid, visible)`: 设置可见性
- `show()`: 显示可视化窗口

**示例**:
```python
import vtkbox
import numpy as np

viz = vtkbox.VTKVisualizer()

# 添加点云
viz.add_points(points, color=(1, 0, 0), name="points1")
viz.add_points_with_intensity(intensity_points, name="points2")

# 添加线
viz.add_line(line_points, color=(0, 1, 0), name="line1")

# 添加包围盒
viz.add_box(xmin, xmax, ymin, ymax, zmin, zmax, opacity=0.5, name="box1")

# 加载机器人模型
viz.set_robot("robot.urdf", "mesh_root_path")

# 显示
viz.show()
```

### create_visualizer_subprocess

创建多进程可视化器，在独立进程中运行。使用 RPC 技术，通过接口进行跨进程通信，并且不再返回actor。

**示例**:
```python
viz = vtkbox.create_visualizer_subprocess()
viz.add_points(points, name="points")
viz.show()
```

### VRobot

机器人模型类，用于加载和操作 URDF 机器人模型。

```python
from vtkbox.urdf2vtk import VRobot

robot = VRobot("robot.urdf", "mesh_root_path")
```
